import os
import sys
import platform
import subprocess

def perform_update(save_path):
    """Executes the update based on the OS."""
    if platform.system() == "Windows":
        # Run Inno Setup installer silently
        subprocess.Popen([save_path, '/SILENT', '/CLOSEAPPLICATIONS'])
    else:
        # For PyInstaller on Linux, sys.executable points to the packaged binary
        app_path = sys.executable
        app_dir = os.path.dirname(os.path.abspath(app_path))
        
        # Sleep ensures the current process closes before overwriting
        script = f"sleep 2 && unzip -o '{save_path}' -d '{app_dir}' && '{app_path}' &"
        subprocess.Popen(['bash', '-c', script])