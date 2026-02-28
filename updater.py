import os
import sys
import platform
import subprocess
import time

def perform_update(save_path):
    if platform.system() == "Windows":
        # Create StartupInfo object to hide the window
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0 # SW_HIDE

        # Removed 'start ""' which was forcing a new window
        # Added /VERYSILENT for maximum invisibility
        cmd = [
            save_path, 
            '/VERYSILENT', 
            '/SUPPRESSMSGBOXES', 
            '/NOCANCEL', 
            '/NORESTART', 
            '/CLOSEAPPLICATIONS', 
            f'/LOG={os.path.join(os.path.dirname(save_path), "update_install.log")}'
        ]
        
        # Launch without creating a console window
        subprocess.Popen(
            cmd, 
            startupinfo=si, 
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        time.sleep(0.5) 
    else:
        # Linux remains background-safe
        app_path = sys.executable
        app_dir = os.path.dirname(os.path.abspath(app_path))
        script = f"sleep 2 && tar -xzf '{save_path}' -C '{app_dir}' && '{app_path}' &"
        subprocess.Popen(['bash', '-c', script])