import os
import sys
import platform
import subprocess
import time

def perform_update(save_path):
    if platform.system() == "Windows":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0

        # Get the actual directory where the app is running
        app_dir = os.path.dirname(os.path.abspath(sys.executable))
        
        cmd = [
            save_path, 
            '/VERYSILENT', 
            '/SUPPRESSMSGBOXES', 
            '/NOCANCEL', 
            '/NORESTART', 
            f'/DIR={app_dir}',  # Force extraction to the current app directory
            f'/LOG={os.path.join(os.path.dirname(save_path), "update_install.log")}'
        ]
        
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