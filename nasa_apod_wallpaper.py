#!/usr/bin/env python3
"""
NASA APOD Desktop Background Setter
Fetches the Astronomy Picture of the Day and sets it as macOS desktop background
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
import subprocess
from datetime import datetime

# Directory to store downloaded wallpapers and config
WALLPAPER_DIR = Path.home() / ".nasa_apod_wallpapers"
WALLPAPER_DIR.mkdir(exist_ok=True)

CONFIG_FILE = WALLPAPER_DIR / "config.json"


def load_api_key():
    """Load API key from config file or environment variable"""
    # First try environment variable
    api_key = os.environ.get("NASA_API_KEY")
    if api_key:
        return api_key

    # Then try config file
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                api_key = config.get('api_key')
                if api_key:
                    return api_key
        except Exception as e:
            print(f"Warning: Could not read config file: {e}")

    # Prompt user to set up API key
    print("\n" + "=" * 60)
    print("NASA API Key Required")
    print("=" * 60)
    print("\nTo use this script, you need a free NASA API key.")
    print("\n1. Get your key at: https://api.nasa.gov/")
    print("2. Run this script again and enter your key when prompted")
    print("\nOr set it as an environment variable:")
    print("   export NASA_API_KEY='your_key_here'")
    print("\nOr create a config file at:")
    print(f"   {CONFIG_FILE}")
    print('   With content: {"api_key": "your_key_here"}')
    print("=" * 60)

    # Try to get key interactively
    try:
        api_key = input("\nEnter your NASA API key (or press Ctrl+C to exit): ").strip()
        if api_key:
            # Save it to config file
            with open(CONFIG_FILE, 'w') as f:
                json.dump({"api_key": api_key}, f, indent=2)
            print(f"\nAPI key saved to {CONFIG_FILE}")
            return api_key
    except (KeyboardInterrupt, EOFError):
        print("\nSetup cancelled.")

    sys.exit(1)


# Load API key
NASA_API_KEY = load_api_key()
APOD_API_URL = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"


def fetch_apod_data(date=None):
    """Fetch the APOD metadata from NASA API"""
    url = APOD_API_URL
    if date:
        url += f"&date={date}"

    try:
        print(f"Fetching NASA APOD data{f' for {date}' if date else ''}...")
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        return data
    except urllib.error.HTTPError as e:
        if e.code == 500:
            print(f"NASA API is experiencing issues (500 error).")
            print("This is a temporary server problem. Please try again later.")
            print("\nYou can also try a specific date with: python3 nasa_apod_wallpaper.py YYYY-MM-DD")
        else:
            print(f"HTTP Error {e.code}: {e.reason}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error fetching APOD data: {e}")
        print("Check your internet connection.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def download_image(url, filename):
    """Download the image from the given URL"""
    try:
        print(f"Downloading image from: {url}")
        filepath = WALLPAPER_DIR / filename
        urllib.request.urlretrieve(url, filepath)
        print(f"Image saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error downloading image: {e}")
        sys.exit(1)


def set_macos_wallpaper(image_path):
    """Set the macOS desktop wallpaper using AppleScript"""
    try:
        script = f'''
        tell application "System Events"
            tell every desktop
                set picture to "{image_path}"
            end tell
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        print(f"Desktop wallpaper updated successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error setting wallpaper: {e}")
        sys.exit(1)


def main():
    print("=" * 60)
    print("NASA Astronomy Picture of the Day - Wallpaper Setter")
    print("=" * 60)

    # Get date from command line argument if provided
    date = None
    if len(sys.argv) > 1:
        date = sys.argv[1]
        print(f"Requesting APOD for date: {date}")

    # Fetch APOD data
    apod_data = fetch_apod_data(date)

    # Display info about today's APOD
    print(f"\nTitle: {apod_data.get('title', 'N/A')}")
    print(f"Date: {apod_data.get('date', 'N/A')}")
    print(f"Media Type: {apod_data.get('media_type', 'N/A')}")

    # Check if it's an image (not a video)
    if apod_data.get('media_type') != 'image':
        print("\nToday's APOD is not an image (it might be a video).")
        print(f"URL: {apod_data.get('url', 'N/A')}")
        print("Cannot set as wallpaper. Please try again tomorrow!")
        sys.exit(0)

    # Get the HD URL if available, otherwise use standard URL
    image_url = apod_data.get('hdurl') or apod_data.get('url')

    if not image_url:
        print("Error: No image URL found in APOD data")
        sys.exit(1)

    # Create filename from date and title
    date_str = apod_data.get('date', datetime.now().strftime('%Y-%m-%d'))
    extension = os.path.splitext(image_url)[1] or '.jpg'
    filename = f"apod_{date_str}{extension}"

    # Download the image
    image_path = download_image(image_url, filename)

    # Set as wallpaper
    set_macos_wallpaper(image_path)

    print("\n" + "=" * 60)
    print("Description:")
    print(apod_data.get('explanation', 'N/A'))
    print("=" * 60)


if __name__ == "__main__":
    main()
