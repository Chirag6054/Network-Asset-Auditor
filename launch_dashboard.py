import sys
import os
from streamlit.web import cli as stcli

def get_script_path():
    # Detects if the script is running inside a PyInstaller EXE
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "dashboard.py")
    return "dashboard.py"

if __name__ == "__main__":
    script_path = get_script_path()
    # Check if the path exists before running to avoid the 404
    if not os.path.exists(script_path):
        print(f"Error: Could not find {script_path}")
        input("Press Enter to exit...")
    else:
        sys.argv = ["streamlit", "run", script_path, "--global.developmentMode=false"]
        sys.exit(stcli.main())