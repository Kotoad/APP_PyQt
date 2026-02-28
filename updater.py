import os
import sys
import platform
import subprocess
import time

def perform_update(save_path):
    if platform.system() == "Windows":
        # Using shell=True and start helps detach the installer from the parent console
        # Added /NOCANCEL to prevent users from interrupting the silent background task
        cmd = f'start "" "{save_path}" /SILENT /NOCANCEL /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /LOG="update_install.log"'
        subprocess.Popen(cmd, shell=True)
        
        # Give the OS a tiny breath to register the new process 
        # before we kill the parent
        time.sleep(0.5) 
    else:
        # Linux logic remains mostly the same
        app_path = sys.executable
        app_dir = os.path.dirname(os.path.abspath(app_path))
        script = f"sleep 2 && tar -xzf '{save_path}' -C '{app_dir}' && '{app_path}' &"
        subprocess.Popen(['bash', '-c', script])