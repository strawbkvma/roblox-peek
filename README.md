# Roblox Peek 🎮

A macOS utility that detects the Roblox game currently being played and displays it as a Discord Rich Presence.

## Features

- Detects the active Roblox game from Roblox client logs
- Shows game name and creator
- Displays Roblox game thumbnail
- Shows elapsed play time
- Join the current Roblox game session
- Open the Roblox profile to add a friend
- Automatically runs in the background using macOS LaunchAgent

## Requirements

- macOS
- Python 3
- Roblox
- Discord desktop app
- A Discord Application with Rich Presence enabled

## Setup

1. Clone this repository.
2. Create a Python virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
cd ~/roblox-peek

cat > .gitignore <<'EOF'
.venv/
__pycache__/
*.pyc

config.py
*.backup
*.working
*.before-parser-fix

launchagent*.log

.DS_Store
