from typing import Optional
import os
import sys
import json
import time  # Added for stability
import app_paths

# --- Cross-Platform Pipe Configuration ---
if sys.platform == 'win32':
    TONAME = r'\\.\pipe\ToSrvPipe'
    FROMNAME = r'\\.\pipe\FromSrvPipe'
else:
    uid = os.getuid()
    TONAME = f'/tmp/audacity_script_pipe.to.{uid}'
    FROMNAME = f'/tmp/audacity_script_pipe.from.{uid}'

def get_track_names():
    """Loads track names from wing_channels.json (checks local dir first)."""
    filename = "wing_channels.json"
    
    # Check 1: Local directory (where the script is)
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    # Check 2: App Data directory (via app_paths)
    config_path = app_paths.get_data_file_path(filename)
    
    json_path = local_path if os.path.exists(local_path) else config_path

    if not os.path.exists(json_path):
        print(f"Warning: JSON file not found at {local_path} or {config_path}")
        return []

    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            return [track.get("config_name", "") for track in data]
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return []

def send_command(command):
    """Sends command and reads response. Crucial for stability."""
    try:
        with open(TONAME, 'w') as out_pipe:
            out_pipe.write(command + '\n')
            out_pipe.flush()
        
        response = ""
        with open(FROMNAME, 'r') as in_pipe:
            while True:
                line = in_pipe.readline()
                response += line
                if line == '\n':
                    break
        return response
    except Exception as e:
        raise e

def rename_all_tracks(names: Optional[list[str]] = None):
    """Main logic: uses absolute indexing with timing delays for reliability."""
    names = names or get_track_names()
    
    if not names:
        print("No track names found to apply.")
        return

    print(f"Applying {len(names)} names. Please wait...")

    # Start by deselecting everything to prevent multi-track renaming
    send_command("SelectNone:")

    for i, name in enumerate(names):
        if not name:
            continue
            
        try:
            # 1. Select the specific track
            # Mode=Set is critical: it clears previous selections
            send_command(f'SelectTracks: Track={i} TrackCount=1 Mode=Set')
            
            # 2. TINY PAUSE (prevents Audacity from skipping commands)
            time.sleep(0.05) 
            
            # 3. Rename the selected track
            send_command(f'SetTrack: Name="{name}"')
            
            # 4. Another tiny pause
            time.sleep(0.05)
            
            print(f"Track {i:02d} -> {name}")
            
        except Exception as e:
            print(f"Failed at track {i}: {e}")
            break

if __name__ == "__main__":
    try:
        rename_all_tracks()
        print("\nSuccess! Process finished.")
    except Exception as e:
        print(f"\nError: {e}")