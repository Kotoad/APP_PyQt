import os
import sys
import platform
import subprocess

def perform_update(save_path):
    """Executes the update based on the OS."""
    if platform.system() == "Windows":
        print(f"Running Windows installer: {save_path}")
        # Run Inno Setup installer silently
        subprocess.Popen([save_path, '/SILENT', '/CLOSEAPPLICATIONS'])
    else:
        # For PyInstaller on Linux, sys.executable points to the packaged binary
        app_path = sys.executable
        app_dir = os.path.dirname(os.path.abspath(app_path))
        
        # Fixed: Use tar instead of unzip
        script = f"sleep 2 && tar -xzf '{save_path}' -C '{app_dir}' && '{app_path}' &"
        subprocess.Popen(['bash', '-c', script])