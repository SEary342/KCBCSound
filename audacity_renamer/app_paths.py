import sys
import os

APP_NAME = "AudacityTrackRenamer"

def get_app_support_dir():
    """Gets the path to the user's application support directory."""
    if sys.platform == "win32":
        path = os.path.join(os.environ["APPDATA"], APP_NAME)
    elif sys.platform == "darwin": # macOS
        path = os.path.join(os.path.expanduser("~/Library/Application Support"), APP_NAME)
    else: # Linux, etc.
        path = os.path.join(os.path.expanduser("~/.config"), APP_NAME)
    
    os.makedirs(path, exist_ok=True)
    return path

def get_data_file_path(filename):
    """Gets the full path to a data file in the app support directory."""
    return os.path.join(get_app_support_dir(), filename)

def get_bundle_path(relative_path):
    """Gets path to internal resources bundled by PyInstaller."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)