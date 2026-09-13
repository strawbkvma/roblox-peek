import json
import re
import subprocess
import time
import urllib.parse
import urllib.request

from pypresence import Presence
from config import DISCORD_CLIENT_ID


POLL_INTERVAL = 2

rpc = None

last_state = None
last_place_id = None
last_job_id = None
game_start_time = None

account_user_id = None


# ─────────────────────────────────────────────
# ROBLOX LOG
# ─────────────────────────────────────────────

def get_latest_log():
    result = subprocess.run(
        "ls -t ~/Library/Logs/Roblox/*Player*_last.log | head -1",
        shell=True,
        capture_output=True,
        text=True,
    )

    log = result.stdout.strip()

    if not log:
        raise RuntimeError("Roblox log tidak ditemukan.")

    return log


def is_roblox_running():
    result = subprocess.run(
        ["pgrep", "-f", "/Roblox.app/Contents/MacOS/RobloxPlayer"],
        capture_output=True,
        text=True,
    )

    return result.returncode == 0


def parse_timestamp(line):
    match = re.match(
        r"^(\d{4}-\d{2}-\d{2}T[\d:.]+Z)",
        line,
    )

    if match:
        return match.group(1)

    return ""


# ─────────────────────────────────────────────
# USER ID
# ─────────────────────────────────────────────

def get_account_user_id(log_path):
    with open(
        log_path,
        "r",
        encoding="utf-8",
        errors="ignore",
    ) as file:
        text = file.read()

    # CharacterFetchUrl:
    # userId%3d7536017679
    matches = re.findall(
        r"userId%3[dD]([0-9]+)",
        text,
    )

    # GameJoinLoadTime:
    # userid:7536017679
    if not matches:
        matches = re.findall(
            r"userid:([0-9]+)",
            text,
            re.IGNORECASE,
        )

    # URL encoded JSON:
    # UserId%3a7536017679
    if not matches:
        matches = re.findall(
            r"UserId%3[aA]([0-9]+)",
            text,
        )

    # Normal JSON:
    # "UserId":7536017679
    if not matches:
        matches = re.findall(
            r'"UserId"\s*:\s*([0-9]+)',
            text,
        )

    if not matches:
        return None

    return matches[-1]


# ─────────────────────────────────────────────
# GAME STATE
# ─────────────────────────────────────────────

def parse_latest_game_state(log_path):
    with open(
        log_path,
        "r",
        encoding="utf-8",
        errors="ignore",
    ) as file:
        lines = file.readlines()

    latest_leave_index = -1
    latest_success = None
    pending_join = None

    for index, line in enumerate(lines):
        if "leaveUGCGameInternal" in line:
            latest_leave_index = index

        # Normal join flow.
        if "GameJoinUtil::joinGamePostStandard" in line:
            place_match = re.search(
                r'"placeId":([0-9]+)',
                line,
            )

            if place_match:
                pending_join = {
                    "index": index,
                    "timestamp": parse_timestamp(line),
                    "place_id": place_match.group(1),
                    "job_id": None,
                    "universe_id": None,
                    "user_id": None,
                }

        # Both normal joins and makePlaceLauncherRequest can
        # produce a successful status response.
        if "status code:" in line:
            decoded_line = urllib.parse.unquote(line)
            decoded_line = decoded_line.replace("\\", "")

            job_match = re.search(
                r'"jobId":"([^"]+)"',
                line,
            )

            place_match = re.search(
                r'"PlaceId":([0-9]+)',
                decoded_line,
            )

            universe_match = re.search(
                r'"UniverseId":([0-9]+)',
                decoded_line,
            )

            user_match = re.search(
                r'"UserId":([0-9]+)',
                decoded_line,
            )

            # Fallback for the encoded CharacterFetchUrl.
            if not place_match:
                place_match = re.search(
                    r'placeId=([0-9]+)',
                    decoded_line,
                    re.IGNORECASE,
                )

            if job_match and job_match.group(1):
                if pending_join is None:
                    pending_join = {
                        "index": index,
                        "timestamp": parse_timestamp(line),
                        "place_id": None,
                        "job_id": None,
                        "universe_id": None,
                        "user_id": None,
                    }

                pending_join["job_id"] = job_match.group(1)

            if pending_join is not None:
                if place_match:
                    pending_join["place_id"] = place_match.group(1)

                if universe_match:
                    pending_join["universe_id"] = universe_match.group(1)

                if user_match:
                    pending_join["user_id"] = user_match.group(1)

        if "Game join succeeded." in line:
            if pending_join is not None:
                if (
                    pending_join.get("job_id")
                    and pending_join.get("place_id")
                    and pending_join.get("universe_id")
                ):
                    latest_success = {
                        **pending_join,
                        "success_index": index,
                        "success_timestamp": parse_timestamp(line),
                    }

                pending_join = None

    if latest_success is None:
        return {
            "playing": False,
            "session": None,
        }

    if latest_leave_index > latest_success["success_index"]:
        return {
            "playing": False,
            "session": None,
        }

    return {
        "playing": True,
        "session": latest_success,
    }


# ─────────────────────────────────────────────
# ROBLOX API
# ─────────────────────────────────────────────

def get_universe_id(place_id):
    url = (
        f"https://apis.roblox.com/"
        f"universes/v1/places/{place_id}/universe"
    )

    with urllib.request.urlopen(
        url,
        timeout=10,
    ) as response:
        data = json.loads(response.read())

    return str(data["universeId"])


def get_game_info(universe_id):
    url = (
        "https://games.roblox.com/v1/games"
        f"?universeIds={universe_id}"
    )

    with urllib.request.urlopen(
        url,
        timeout=10,
    ) as response:
        data = json.loads(response.read())

    if not data.get("data"):
        raise RuntimeError(
            f"Game info tidak ditemukan untuk Universe {universe_id}"
        )

    return data["data"][0]


def get_thumbnail(universe_id):
    params = urllib.parse.urlencode({
        "universeIds": universe_id,
        "size": "512x512",
        "format": "Png",
        "isCircular": "false",
    })

    url = (
        "https://thumbnails.roblox.com/v1/games/icons?"
        + params
    )

    with urllib.request.urlopen(
        url,
        timeout=10,
    ) as response:
        data = json.loads(response.read())

    if not data.get("data"):
        return None

    return data["data"][0].get("imageUrl")


# ─────────────────────────────────────────────
# DISCORD
# ─────────────────────────────────────────────

def connect_discord():
    global rpc

    while True:
        try:
            rpc = Presence(DISCORD_CLIENT_ID)
            rpc.connect()
            print("Discord Rich Presence connected!")
            return
        except Exception as error:
            print(f"Discord belum tersedia: {error}")
            print("Retrying in 5 seconds...")
            time.sleep(5)


def show_browsing():
    global last_state
    global last_place_id
    global last_job_id
    global game_start_time

    if last_state == "browsing":
        return

    rpc.clear()

    payload = {
        "details": "👀 Browsing Game",
        "state": "♡ choosing what to play",
    }

    # Add Friend tetap tersedia saat browsing
    if account_user_id:
        payload["buttons"] = [
            {
                "label": "Add Friend",
                "url": (
                    "https://www.roblox.com/users/"
                    f"{account_user_id}/profile"
                ),
            }
        ]

    rpc.update(**payload)

    last_state = "browsing"
    last_place_id = None
    last_job_id = None
    game_start_time = None

    print("Roblox opened, but not playing a game.")

    if account_user_id:
        print(f"   User ID   : {account_user_id}")


def clear_presence():
    global last_state
    global last_place_id
    global last_job_id
    global game_start_time
    global account_user_id

    if last_state == "offline":
        return

    try:
        rpc.clear()
    except Exception:
        pass

    last_state = "offline"
    last_place_id = None
    last_job_id = None
    game_start_time = None
    account_user_id = None

    print("Roblox closed → Discord Presence cleared.")


# ─────────────────────────────────────────────
# GAME PRESENCE
# ─────────────────────────────────────────────

def update_game_presence(
    game,
    universe_id,
    place_id,
    job_id,
):
    global last_state
    global last_place_id
    global last_job_id
    global game_start_time

    game_name = game["name"]
    creator_name = game["creator"]["name"]

    thumbnail_url = get_thumbnail(universe_id)

    # Reset timer when changing game/server
    if (
        place_id != last_place_id
        or job_id != last_job_id
    ):
        game_start_time = time.time()

    if job_id:
        join_url = (
            "https://www.roblox.com/games/start"
            f"?placeId={place_id}"
            f"&gameInstanceId="
            f"{urllib.parse.quote(job_id)}"
        )
    else:
        join_url = (
            f"https://www.roblox.com/games/{place_id}"
        )

    buttons = [
        {
            "label": "Join Game",
            "url": join_url,
        }
    ]

    if account_user_id:
        buttons.append(
            {
                "label": "Add Friend",
                "url": (
                    "https://www.roblox.com/users/"
                    f"{account_user_id}/profile"
                ),
            }
        )

    payload = {
        "details": f"🏅 Playing {game_name}",
        "state": f"♡ by {creator_name}",
        "start": game_start_time,
        "buttons": buttons,
        "large_text": game_name,
    }

    if thumbnail_url:
        payload["large_image"] = thumbnail_url

    rpc.update(**payload)

    last_state = "playing"
    last_place_id = place_id
    last_job_id = job_id

    print()
    print("GAME DETECTED!")
    print(f"   Game      : {game_name}")
    print(f"   Creator   : {creator_name}")
    print(f"   Place ID  : {place_id}")
    print(f"   Universe  : {universe_id}")
    print(f"   Job ID    : {job_id}")
    print(f"   User ID   : {account_user_id}")
    print(
        f"   Thumbnail : "
        f"{'✓' if thumbnail_url else '✗'}"
    )
    print()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    global account_user_id

    print("roblox-peek started")
    print()

    connect_discord()

    while True:
        try:

            if not is_roblox_running():
                clear_presence()

                time.sleep(POLL_INTERVAL)
                continue

            log_path = get_latest_log()

            # Detect account as soon as Roblox is running
            detected_user_id = get_account_user_id(log_path)

            if detected_user_id:
                if detected_user_id != account_user_id:
                    account_user_id = detected_user_id

                    print(
                        f"Roblox Account detected"
                    )
                    print(
                        f"   User ID   : {account_user_id}"
                    )

            result = parse_latest_game_state(log_path)

            if not result["playing"]:
                show_browsing()

                time.sleep(POLL_INTERVAL)
                continue

            session = result["session"]

            place_id = session["place_id"]
            job_id = session["job_id"]
            universe_id = session["universe_id"]

            if not universe_id:
                universe_id = get_universe_id(
                    place_id
                )

            if (
                last_state == "playing"
                and place_id == last_place_id
                and job_id == last_job_id
            ):
                time.sleep(POLL_INTERVAL)
                continue

            game = get_game_info(universe_id)

            update_game_presence(
                game,
                universe_id,
                place_id,
                job_id,
            )

        except Exception as error:
            print(f"{error}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
