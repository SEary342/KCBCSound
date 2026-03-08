import tkinter as tk
from tkinter import messagebox
import threading
import asyncio
import os
import json
import rename_tracks
import app_paths

# Import the main function from the dump script to run it directly
from dump_wing_channels import main as dump_wing_main

DEFAULT_MIXER_IP = "192.168.1.126"

class TrackRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audacity Track Renamer")
        self.root.wm_attributes('-topmost', 1)
        # Load initial track names from JSON or defaults
        self.track_names = rename_tracks.get_track_names()
        
        # Create a main frame
        main_frame = tk.Frame(root)
        main_frame.pack(padx=20, pady=20)
        
        # --- IP Configuration ---
        ip_frame = tk.Frame(main_frame)
        ip_frame.grid(row=0, column=0, columnspan=4, pady=(0, 15), sticky="ew")
        ip_frame.columnconfigure(1, weight=1) # Make entry expand
        
        lbl_ip = tk.Label(ip_frame, text="Mixer IP:")
        lbl_ip.grid(row=0, column=0, padx=(0, 5))
        
        self.ip_entry = tk.Entry(ip_frame)
        self.ip_entry.grid(row=0, column=1, sticky="ew")
        self.load_config() # Populate the IP entry
        
        # Instruction Label
        lbl_instruct = tk.Label(main_frame, text="Edit track names below and click 'Rename Tracks'.")
        lbl_instruct.grid(row=1, column=0, columnspan=4, pady=(0, 15))

        self.entries = []
        
        # Create 32 entries in 2 columns
        for i in range(32):
            if i < 16:
                col_offset = 0
                row = i + 2
            else:
                col_offset = 2
                row = (i - 16) + 2
            
            # Label
            lbl = tk.Label(main_frame, text=f"{i+1:02d}:")
            lbl.grid(row=row, column=col_offset, sticky="e", padx=(5, 2))
            
            # Entry
            entry = tk.Entry(main_frame, width=20)
            if i < len(self.track_names):
                entry.insert(0, self.track_names[i])
            
            entry.grid(row=row, column=col_offset+1, padx=(0, 15), pady=2)
            self.entries.append(entry)

        # Buttons Frame
        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(pady=(0, 20))
        
        self.btn_run = tk.Button(self.btn_frame, text="Rename Tracks", command=self.run_rename, height=2, width=15)
        self.btn_run.pack(side=tk.LEFT, padx=5)
        
        self.btn_reset = tk.Button(self.btn_frame, text="Reset Local", command=self.reset_defaults)
        self.btn_reset.pack(side=tk.LEFT, padx=5)

        self.btn_refresh = tk.Button(self.btn_frame, text="Refresh from Mixer", command=self.refresh_from_mixer)
        self.btn_refresh.pack(side=tk.LEFT, padx=5)

    def load_config(self):
        """Loads configuration like the mixer IP from a JSON file."""
        config_path = app_paths.get_data_file_path("config.json")
        ip = DEFAULT_MIXER_IP
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    ip = config.get("mixer_ip", DEFAULT_MIXER_IP)
            except (json.JSONDecodeError, IOError):
                pass # Use default if file is corrupt or unreadable
        self.ip_entry.delete(0, tk.END)
        self.ip_entry.insert(0, ip)

    def save_config(self):
        """Saves the current mixer IP to the config file."""
        config_path = app_paths.get_data_file_path("config.json")
        config = {"mixer_ip": self.ip_entry.get().strip()}
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
        except IOError as e:
            print(f"Warning: Could not save config file: {e}")

    def reset_defaults(self):
        """Reloads names from the JSON file into the UI entries."""
        self.track_names = rename_tracks.get_track_names()
        for i, entry in enumerate(self.entries):
            entry.delete(0, tk.END)
            if i < len(self.track_names):
                entry.insert(0, self.track_names[i])

    def set_ui_state(self, is_enabled):
        """Disables or enables all buttons in the button frame."""
        state = tk.NORMAL if is_enabled else tk.DISABLED
        for child in self.btn_frame.winfo_children():
            if isinstance(child, tk.Button):
                child.configure(state=state)

    def refresh_from_mixer(self):
        """Fetches names from the WING mixer in a background thread."""
        self.save_config() # Save the IP before trying to connect
        self.root.configure(cursor="wait")
        self.set_ui_state(False)

        def run_async_task():
            """Wrapper to run the async dump function and handle results."""
            try:
                ip_address = self.ip_entry.get().strip()
                # Run the async main function from the dump script
                asyncio.run(dump_wing_main(ip_address=ip_address))
                # Schedule the success handler to run on the main UI thread
                self.root.after(0, self.on_refresh_success)
            except Exception as e:
                # Schedule the error handler to run on the main UI thread.
                # Pass the method and argument directly to avoid lambda scoping issues.
                self.root.after(0, self.on_refresh_error, e)

        # Run the wrapper in a separate thread to avoid blocking the UI
        thread = threading.Thread(target=run_async_task, daemon=True)
        thread.start()

    def on_refresh_success(self):
        """UI update on successful mixer refresh."""
        self.reset_defaults()
        self.root.configure(cursor="")
        self.set_ui_state(True)
        messagebox.showinfo("Success", "Successfully refreshed track names from the mixer.")

    def on_refresh_error(self, error):
        """UI update on failed mixer refresh."""
        self.root.configure(cursor="")
        self.set_ui_state(True)
        messagebox.showerror("Mixer Error", f"Could not get names from mixer.\n\nDetails: {error}")

    def run_rename(self):
        """Sends the names from the UI entries to Audacity."""
        try:
            # Start at the top of the Audacity project
            rename_tracks.send_command("SelectAll:")
            rename_tracks.send_command("TrackHome:")
            
            for i, entry in enumerate(self.entries):
                name = entry.get().strip()
                # Apply the name to the current track
                rename_tracks.send_command(f'SetTrack:Name="{name}"')
                # Move focus to the next track down
                rename_tracks.send_command("SelectNextTrack:")
            
            messagebox.showinfo("Success", "Audacity tracks renamed!")
            
        except Exception as e:
            messagebox.showerror("Audacity Error", f"Is Audacity running with mod-script-pipe enabled?\n\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TrackRenamerApp(root)
    root.mainloop()