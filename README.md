# Roblox Peek 🧸🎮

> A lightweight macOS utility that turns your Roblox gaming session into Discord Rich Presence.

**Roblox Peek** is a lightweight, local-only macOS utility that detects the Roblox game you're currently playing and displays it as a cute Discord Rich Presence.

It runs quietly in the background and automatically updates your Discord activity when you join or leave Roblox games.

Everything runs locally on your Mac. No Roblox login. No external backend. No tracking.

---

## ✨ Features

- 🎮 Detect Roblox game sessions
- 🏅 Detect game names
- ♡ Detect game creators
- 🖼️ Dynamic Roblox game thumbnails
- 🌐 Detect Roblox server Job IDs
- 🔗 Join Game button
- 👤 Add Friend button
- ⏱️ Server session timer
- 🔄 Timer resets when joining a different game/server
- 💬 Discord Rich Presence
- 🔌 Discord auto-reconnect
- 🛡️ Roblox & Discord error handling
- 🚀 Automatic background mode with LaunchAgent
- 🔒 Local-only architecture

---

## 🛠️ Requirements

Before installing, make sure you have:

- macOS
- Roblox Player
- Discord Desktop
- Python 3
- An active internet connection for Roblox API requests and Discord Rich Presence

---

## 🍓 Quick Start

### 1. Install directly

The easiest way to install Roblox Peek is using the one-command installer:

```bash
curl -fsSL https://raw.githubusercontent.com/strawbkvma/roblox-peek/main/install.sh | bash
```

The installer automatically:

- 📦 Downloads or updates Roblox Peek
- 🐍 Creates a Python virtual environment
- 📚 Installs the required dependencies
- 🎮 Configures your Discord Application ID
- ⚙️ Configures the macOS LaunchAgent
- 🚀 Starts Roblox Peek in the background

If `config.py` already exists, the installer will keep the existing configuration.

---

### 2. Discord Application Setup

Roblox Peek uses a Discord Application to display Rich Presence.

You will need a **Discord Application Client ID**.

When running the installer for the first time, you may be asked:

```text
Enter your Discord Client ID:
```

Enter the **Application ID** from your Discord Developer Portal.

> The Discord Application ID is a public identifier and is not a bot token or client secret.

---

### 3. Start Roblox

Open Roblox Player and join a game.

Roblox Peek automatically detects the active Roblox session from the local Roblox Player logs.

You don't need to keep Terminal open.

---

### 4. Open Discord

Make sure Discord Desktop is running.

Once Roblox Peek detects your game, your Discord activity will automatically update.

That's it. 🧸🎮🍓

---

## 💬 Discord Rich Presence

When you're playing Roblox, Discord displays an activity similar to:

> **Playing Roblox 🎮 · Catalog Avatar Creator**

The Rich Presence includes:

- 🏅 Current game name
- ♡ Game creator
- 🖼️ Roblox game thumbnail
- ⏱️ Current server session time
- 🔗 Join Game button
- 👤 Add Friend button

### Activity Example

```text
Playing Roblox 🎮 · Capybara Onsen ♨

Roblox
🏅 Playing Capybara Onsen ♨
♡ by Dojo Empire

[ Join Game ] [ Add Friend ]

🎮 8:14
```

The activity automatically changes when you join another Roblox game.

---

## 🎮 Game Detection

Roblox Peek reads the local Roblox Player logs to determine the current game session.

It extracts information such as:

```text
Place ID
Universe ID
Job ID
User ID
```

This information is then used to retrieve game metadata and create the Discord Rich Presence.

### Session Flow

```text
Roblox Player
      │
      │ Local Player Logs
      ▼
┌─────────────────────┐
│   Roblox Detector   │
│      main.py        │
└──────────┬──────────┘
           │
           │ Place ID
           │ Universe ID
           │ Job ID
           ▼
┌─────────────────────┐
│    Roblox API       │
│                     │
│ Game information    │
│ Creator information │
│ Game thumbnail      │
└──────────┬──────────┘
           │
           │ Game metadata
           ▼
┌─────────────────────┐
│   Discord RPC       │
│    discord_rpc.py   │
└──────────┬──────────┘
           │
           │ Discord IPC
           ▼
┌─────────────────────┐
│       Discord       │
│   Rich Presence     │
└─────────────────────┘
```

---

## 🔗 Join Game

Roblox Peek detects the current Roblox server **Job ID** from the Roblox Player session.

When available, the **Join Game** button uses the detected game/server information to allow you to jump back into the current Roblox session.

The timer also resets when a new game or server session is detected.

---

## 👤 Add Friend

The **Add Friend** button opens the Roblox profile associated with the detected account.

Roblox handles the actual friend request through its own interface.

Roblox Peek does not automatically send friend requests or access your Roblox account credentials.

---

## 🚀 Background Mode

Roblox Peek automatically configures a macOS **LaunchAgent** when you run the installer.

The LaunchAgent:

- starts Roblox Peek automatically when you log in
- keeps the application running in the background
- allows Rich Presence updates without keeping Terminal open
- retries the Discord connection if Discord is not available yet

The LaunchAgent is created at:

```text
~/Library/LaunchAgents/com.strawbkvma.roblox-peek.plist
```

### Discord Startup Handling

If Discord is not running when Roblox Peek starts, the application does not crash.

Instead, it waits and retries the Discord connection automatically:

```text
Discord belum tersedia
        ↓
Retrying in 5 seconds...
        ↓
Discord starts
        ↓
Discord Rich Presence connected!
```

---

## 📁 Project Structure

```text
roblox-peek/
│
├── main.py
├── discord_rpc.py
├── install.sh
│
├── config.py
├── config.example.py
├── requirements.txt
│
├── README.md
├── .gitignore
└── LICENSE
```

The following files/directories are created locally and are **not included in the repository**:

```text
.venv/
config.py
launchagent.log
launchagent-error.log
```

---

## 🧩 Main Files

### `main.py`

Controls the main application logic, including:

- Roblox session detection
- Roblox log parsing
- game information retrieval
- session tracking
- Discord Rich Presence updates
- Discord reconnect handling
- error handling

### `discord_rpc.py`

Handles the Discord Rich Presence connection and presence updates.

### `install.sh`

Automates the installation process, including:

- Python environment setup
- dependency installation
- Discord configuration
- LaunchAgent configuration
- background application startup

### `config.py`

Contains the local Discord Application Client ID.

This file is intentionally excluded from Git.

### `config.example.py`

Example configuration file showing the expected configuration format.

### `requirements.txt`

Contains the Python dependencies required by Roblox Peek.

---

## ⚙️ Configuration

The main configuration file is:

```text
config.py
```

Example:

```python
DISCORD_CLIENT_ID = "YOUR_DISCORD_APPLICATION_ID"
```

The actual `config.py` file is excluded from Git using `.gitignore`.

This prevents your personal local configuration from being committed accidentally.

---

## 🐛 Troubleshooting

### Discord doesn't show the Rich Presence

Make sure:

1. Discord Desktop is running.
2. You are logged into Discord.
3. Roblox Peek is running.
4. Roblox Player is running.
5. You are currently inside a Roblox game.

You can check the LaunchAgent with:

```bash
launchctl print gui/$(id -u)/com.strawbkvma.roblox-peek
```

---

### Roblox game is not detected

Make sure:

1. Roblox Player is running.
2. You have joined a Roblox game.
3. Roblox has created a recent Player log.
4. Roblox Peek is running in the background.

You can check the Roblox logs with:

```bash
ls -lt ~/Library/Logs/Roblox/
```

---

### LaunchAgent is not running

Check the LaunchAgent:

```bash
launchctl print gui/$(id -u)/com.strawbkvma.roblox-peek
```

You can also check the process:

```bash
ps aux | grep "[r]oblox-peek"
```

If needed, restart the LaunchAgent:

```bash
launchctl bootout gui/$(id -u) \
~/Library/LaunchAgents/com.strawbkvma.roblox-peek.plist 2>/dev/null || true

launchctl bootstrap gui/$(id -u) \
~/Library/LaunchAgents/com.strawbkvma.roblox-peek.plist
```

---

### Discord was not open when macOS started

No action is required.

Roblox Peek automatically retries the Discord connection until Discord becomes available.

---

## 🔒 Privacy

Roblox Peek is designed to run locally on your Mac.

It does **not**:

- require your Roblox password
- log into your Roblox account
- store your Roblox credentials
- use an external backend
- send your Roblox browsing history to a server
- store game sessions in a database

Roblox Peek reads the local Roblox Player logs required to determine the current game session.

Game metadata and thumbnails are retrieved from Roblox's public APIs.

Discord Rich Presence is communicated directly to the Discord Desktop application.

Your Roblox credentials are never required. 🧸🍓

---

## 🛡️ Security Notes

Roblox Peek uses a Discord Application ID for Rich Presence.

Discord Application IDs are public identifiers and are **not equivalent to**:

- Discord bot tokens
- OAuth client secrets
- Personal access tokens
- Private API keys
- Authentication credentials

Never publish:

- Discord bot tokens
- OAuth client secrets
- Personal access tokens
- Private API keys
- Authentication credentials

---

## 🗺️ Roadmap

### 🎮 Roblox Detection

- Roblox game detection
- Place ID detection
- Universe ID detection
- Server Job ID detection
- Game creator detection
- Dynamic game thumbnails
- Multi-game session handling

### 💬 Discord

- Discord Rich Presence
- Discord auto-reconnect
- Dynamic game information
- Join Game button
- Add Friend button
- Session timer

### 🚀 System

- LaunchAgent background support
- One-command installation
- Automatic startup
- Improved installer experience

### 🧸 Future Improvements

- Better Roblox log compatibility
- Improved server joining
- More reliable game/session detection
- Optional configuration UI
- Additional Rich Presence customization

---

## 📜 License

Roblox Peek is open-source software licensed under the **MIT License**.

See [`LICENSE`](https://github.com/strawbkvma/roblox-peek/blob/main/LICENSE) for details.

---

## 🧸🍓 About

Roblox Peek started as a small macOS utility project built around **Roblox and Discord Rich Presence**.

The idea is simple:

> Make your Roblox status a little more cute. 🎮🧸🍓

Made with 🧸🍓 and too much time playing Roblox.
