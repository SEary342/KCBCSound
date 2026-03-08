# Audacity Track Renamer & WING Sync

This tool automates the process of renaming tracks in Audacity. It features a graphical interface that allows you to manually edit track names or fetch them directly from a Behringer WING mixing console.

## Prerequisites

*   **Audacity**: Version 2.3.2 or later.
*   **Python**: 3.13+
*   **uv**: The Python package installer. If you don't have it, run `pip install uv`.
*   **Network Connection**: Required if syncing with a WING mixer.

## Installation

This project is managed with `uv`.

1.  To install the dependencies into a local virtual environment (`.venv`), run:
    ```bash
    uv sync
    ```
    This command reads the `uv.lock` file and installs the exact versions of the required packages.

    *(Note: `tkinter` is usually included with Python, but on some Linux distributions, you might need to install it separately, e.g., `sudo apt-get install python3-tk`)*

## Initial Setup (One-Time)

To allow Python to control Audacity, you must enable the `mod-script-pipe` module.

1.  Open Audacity.
2.  Navigate to the Preferences menu:
    *   **macOS**: `Audacity` -> `Settings...` (or `Preferences`)
    *   **Windows/Linux**: `Edit` -> `Preferences...`
3.  In the sidebar, select **Modules**.
4.  Locate `mod-script-pipe` in the list.
5.  Change the setting from **New** or **Disabled** to **Enabled**.
6.  Click **OK**.
7.  **Restart Audacity**.
    *   *Note: The named pipe is only created when Audacity starts up with the module enabled.*

## Usage

1.  Open your Audacity project.
    *   Ensure your project has **32 tracks** loaded to match the script's list.
2.  Run the UI application from your terminal:
    ```bash
    uv run python rename_tracks_ui.py
    ```
    This command executes the script within the `uv`-managed virtual environment.
3.  The application window will appear. You have several options:
    *   **Manual Edit**: Edit the names in the text fields directly.
    *   **Sync from Mixer**:
        *   Enter your WING console's IP address.
        *   Click **Refresh from Mixer** to fetch the current channel names.
    *   **Reset to Local**: Click **Reset Local** to discard any manual changes and reload the names from the last successful sync (`wing_channels.json`) or the built-in defaults.
4.  Once the names are correct, click **Rename Tracks** to apply them to your open Audacity project.

## Troubleshooting

*   **"Error: Audacity pipe not found"**:
    *   Ensure Audacity is currently running.
    *   Verify that `mod-script-pipe` is set to **Enabled** in Preferences.
    *   Ensure you restarted Audacity after enabling the module.
    *   On macOS/Linux, the script looks for `/tmp/audacity_script_pipe.to.<uid>`.
*   **Mixer Connection Issues**:
    *   Verify the IP address is correct.
    *   Ensure the computer is on the same network as the mixer.

## Development

### Building a Standalone Executable

You can bundle this application into a standalone executable (e.g., `.app` for macOS or `.exe` for Windows) using `PyInstaller`.

1.  Run the build command:
    ```bash
    build.sh
    ```

2.  The compiled application will be available in the `dist/` directory.