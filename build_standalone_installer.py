"""
build_standalone_installer.py - Create Online Installer Executable
"""

import PyInstaller.__main__
import os
import shutil
from pathlib import Path

def build_installer():
    """Build the lightweight online installer"""
    
    print("[*] Building Online Installer...")
    
    # We DO NOT bundle the dist/ folder or resources anymore.
    # We only need the installer script itself.
    
    args = [
        'installer_gui.py',
        '--onefile',
        '--windowed',
        '--name=OmniBoard Studio Installer',
        '--distpath=dist',
        '--noconfirm',
        # Keep basic UI imports available
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=PyQt6.QtWidgets',
    ]
    
    # If you have an icon, verify path and add it
    if os.path.exists('resources/images/APPicon.ico'):
        args.append('--icon=resources/images/APPicon.ico')
    
    try:
        PyInstaller.__main__.run(args)
        print("\n[✓] Installer built successfully!")
        print(f"    Output: dist/OmniBoard Studio Installer.exe")
        print(f"    Type: Online Installer (downloads from GitHub)")
        return True
    except Exception as e:
        print(f"\n[✗] Build failed: {e}")
        return False

if __name__ == '__main__':
    build_installer()