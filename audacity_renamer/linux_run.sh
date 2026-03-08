#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to that directory so uv finds your local imports
cd "$SCRIPT_DIR"

# Get the absolute path to the system python3
SYSTEM_PYTHON=$(which python3)

echo "Launching via uv using $SYSTEM_PYTHON..."

# Pass the absolute path of system python to uv's --python flag
uv run --python "$SYSTEM_PYTHON" python rename_tracks_ui.py