import os
import sys
import json

import app_paths

# Names from your routing image
TRACK_NAMES = [
    "Kick", "Snare", "Low Tom", "High Tom", "Overhead L", "Hi Hat", "Bass", "Keys L",
    "Keys R", "Piano Low", "Piano High", "Chris Acc G", "Acc Guitar", "Chris Elec", "Amb L", "INST 2",
    "Chris Voc", "Voc 2", "Voc 3", "Voc 4", "Amb R", "Choir L", "Choir R", "Choir R",
    "Ch 25", "Ch 26", "Ch 27", "WL HH 1", "WL HH 2", "Telex TB", "Shure Wireless", "PASTOR"
]

def get_track_names():
    """Loads track names from the user's app data folder if available, else uses defaults."""
    json_path = app_paths.get_data_file_path("wing_channels.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                return [track.get("config_name", "") for track in data]
        except Exception as e:
            print(f"Error loading JSON: {e}")
    return TRACK_NAMES

def send_command(command):
    """Sends a command to Audacity via the named pipe."""
    if sys.platform == 'win32':
        pipe_name = r'\\.\pipe\to-os-pipe'
    else:
        # Standard path for Fedora/Linux
        pipe_name = f'/tmp/audacity_script_pipe.to.{os.getuid()}'
    
    with open(pipe_name, 'w') as pipe:
        pipe.write(command + '\n')
        pipe.flush()

def rename_all_tracks():
    # Ensure we start at the top track
    send_command("SelectAll:")
    send_command("TrackHome:")
    
    names = get_track_names()
    for name in names:
        print(f"Naming track: {name}")
        send_command(f'SetTrack:Name="{name}"')
        send_command("SelectNextTrack:")

if __name__ == "__main__":
    try:
        rename_all_tracks()
        print("\nSuccess! All 32 tracks renamed.")
    except FileNotFoundError:
        print("Error: Audacity pipe not found. Is Audacity running and mod-script-pipe enabled?")