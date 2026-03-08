#!/bin/bash

# --- CONFIG ---
APP_NAME="AudacityTrackRenamer"
ENTRY_POINT="rename_tracks_ui.py"

echo "🚀 Building $APP_NAME for $OSTYPE..."

# 1. Sync dependencies
uv sync --group dev

# 2. Setup OS-specific flags
# macOS uses --windowed for the .app bundle
# Windows/Linux use --noconsole to hide the terminal
OS_FLAGS="--noconsole"
[[ "$OSTYPE" == "darwin"* ]] && OS_FLAGS="--windowed"

# 3. Build the App
# --collect-all is vital for the behringer_mixer's dynamic OSC loading
uv run pyinstaller \
    $OS_FLAGS \
    --onefile \
    --clean \
    --name "$APP_NAME" \
    --collect-all behringer_mixer \
    "$ENTRY_POINT"

# 4. Result Check
if [ -d "dist" ]; then
    echo "--------------------------------------------"
    echo "✅ Build Complete!"
    echo "Binary location: $(pwd)/dist/"
    echo "--------------------------------------------"
else
    echo "❌ Build failed."
    exit 1
fi