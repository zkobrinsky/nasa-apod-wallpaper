#!/bin/bash
# Daily NASA APOD Wallpaper Updater
# This script runs the Python wallpaper setter and logs the output

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_FILE="$HOME/.nasa_apod_wallpapers/apod.log"

echo "==================== $(date) ====================" >> "$LOG_FILE"
python3 "$SCRIPT_DIR/nasa_apod_wallpaper.py" >> "$LOG_FILE" 2>&1
echo "" >> "$LOG_FILE"
