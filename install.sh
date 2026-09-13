#!/bin/bash

set -e

REPO_URL="strawbkvma/roblox-peek.git"
INSTALL_DIR="$HOME/roblox-peek"
PLIST_NAME="com.strawbkvma.roblox-peek"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME.plist"

echo "ROBLOX PEEK INSTALLER"
echo "========================"
echo

# Clone / update project
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "📦 Updating existing installation..."
    cd "$INSTALL_DIR"
    git pull --ff-only
else
    echo "📦 Downloading Roblox Peek..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Python check
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python 3 is required."
    exit 1
fi

echo "⚙️ Setting up virtual environment..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "📚 Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Discord Client ID
echo
echo "🎮 Discord Application Setup"
echo

if [ -f "config.py" ]; then
    echo "✅ config.py already exists."
else
    read -r -p "Enter your Discord Client ID: " DISCORD_CLIENT_ID

    if [ -z "$DISCORD_CLIENT_ID" ]; then
        echo "❌ Discord Client ID cannot be empty."
        exit 1
    fi

    cat > config.py <<CONFIG
DISCORD_CLIENT_ID = "$DISCORD_CLIENT_ID"
CONFIG

    echo "✅ config.py created."
fi

# LaunchAgent
echo
echo "⚙️ Setting up LaunchAgent..."

mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_NAME</string>

    <key>ProgramArguments</key>
    <array>
        <string>$INSTALL_DIR/.venv/bin/python</string>
        <string>$INSTALL_DIR/main.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$INSTALL_DIR</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>$INSTALL_DIR/launchagent.log</string>

    <key>StandardErrorPath</key>
    <string>$INSTALL_DIR/launchagent-error.log</string>
</dict>
</plist>
PLIST

echo "🔄 Restarting Roblox Peek..."

launchctl bootout "gui/$(id -u)" "$PLIST_PATH" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"

echo
echo "🎉 Installation complete!"
echo
echo "Roblox Peek is now running in the background."
echo
echo "📁 Installed at:"
echo "$INSTALL_DIR"
echo
echo "Enjoy Roblox Rich Presence! 🧸🍓"
