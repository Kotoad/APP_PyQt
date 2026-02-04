"""
installer_gui.py - Online Windows Installer UI
Downloads application payload from GitHub and installs it.
"""

import sys
import os
import shutil
import json
import subprocess
import winreg
import zipfile
import urllib.request
import traceback
from pathlib import Path
from datetime import datetime

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QCheckBox, QProgressBar,
        QFileDialog, QMessageBox, QFrame
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QFont, QIcon
except ImportError:
    print("[!] PyQt6 not found. Install with: pip install PyQt6")
    sys.exit(1)

# ================= CONFIGURATION =================
# REPLACE THIS WITH YOUR GITHUB RELEASE ASSET URL
GITHUB_ZIP_URL = "https://github.com/Kotoad/APP_PyQt/releases/download/V0.1/app_package.zip"
# =================================================

class InstallerWorker(QThread):
    """Background installation worker thread with Download support"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, install_path, create_shortcut):
        super().__init__()
        self.install_path = install_path
        self.create_shortcut = create_shortcut
        self.app_name = "OmniBoard Studio"
        self.company_name = "Developer"
        self.download_url = GITHUB_ZIP_URL
        
    def run(self):
        """Execute installation in background"""
        try:
            self._install()
            self.finished.emit(True, "Installation completed successfully!")
        except Exception as e:
            error_trace = traceback.format_exc()
            self.finished.emit(False, f"Installation failed: {str(e)}\n\n{error_trace}")
    
    def _report_download_progress(self, block_num, block_size, total_size):
        """Callback for urllib to update progress bar"""
        downloaded = block_num * block_size
        if total_size > 0:
            percent = int((downloaded / total_size) * 100)
            # Map download (0-100%) to progress bar (10-80%)
            scaled_progress = 10 + int(percent * 0.7)
            self.progress.emit(scaled_progress)
            
            # Update status text occasionally
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            self.status.emit(f"Downloading... {mb_downloaded:.1f}MB / {mb_total:.1f}MB")

    def _install(self):
        install_dir = Path(self.install_path)
        
        # Step 1: Create directories
        self.status.emit("Creating installation directory...")
        self.progress.emit(5)
        install_dir.mkdir(parents=True, exist_ok=True)
        
        backup_dir = Path(os.path.expanduser("~\\AppData\\Local\\OmniBoard Studio"))
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 2: Download the ZIP file
        self.status.emit("Connecting to GitHub...")
        zip_path = install_dir / "app_package.zip"
        
        try:
            # FIX: Add headers to trick GitHub into thinking we are a browser
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')]
            urllib.request.install_opener(opener)

            # Download file
            urllib.request.urlretrieve(
                self.download_url, 
                zip_path, 
                self._report_download_progress
            )
        except Exception as e:
            raise ConnectionError(f"Failed to download from GitHub: {e}")

        # Step 3: Extract ZIP
        self.status.emit("Extracting files...")
        self.progress.emit(85)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(install_dir)
        except zipfile.BadZipFile:
            raise Exception("Downloaded file is corrupt or not a valid zip file.")
        finally:
            if zip_path.exists():
                os.remove(zip_path)

        # Step 4: SMART SEARCH for the Executable
        # This fixes the "FileNotFound" error by looking inside subfolders recursively
        self.status.emit("Locating application...")
        
        target_name = "OmniBoard Studio.exe"
        found_exes = list(install_dir.rglob("*.exe")) # rglob searches recursively
        
        dest_exe = None
        
        # Priority 1: Find exact name match
        for exe in found_exes:
            if exe.name == target_name:
                dest_exe = exe
                break
        
        # Priority 2: Fallback to ANY exe found (if user renamed it)
        if not dest_exe and found_exes:
            dest_exe = found_exes[0]
            
        if not dest_exe:
            # Debug info to help user
            found_files = [f.name for f in install_dir.rglob("*") if f.is_file()]
            msg = f"Application executable not found in downloaded package.\nSearched for: {target_name}\n"
            msg += f"Files actually found in zip: {found_files[:5]}..." if found_files else "Zip appeared empty."
            raise FileNotFoundError(msg)

        # Step 5: Create uninstaller
        self.status.emit("Creating uninstaller...")
        self.progress.emit(90)
        self._create_uninstaller_bat(install_dir, backup_dir)
        
        # Step 6: Metadata
        install_info = {
            "app_name": self.app_name,
            "version": "1.0.0",
            "install_date": datetime.now().isoformat(),
            "install_path": str(install_dir),
            "exe_location": str(dest_exe), # Store where we actually found it
            "source": "GitHub Release"
        }
        with open(install_dir / "install_info.json", 'w') as f:
            json.dump(install_info, f, indent=2)

        # Step 7: Shortcuts & Registry
        if self.create_shortcut:
            self._create_shortcut(dest_exe)
            
        self._register_uninstaller(install_dir, dest_exe)
        
        self.progress.emit(100)
        self.status.emit("Installation complete!")

    def _create_uninstaller_bat(self, install_dir, backup_dir):
        uninstall_bat = install_dir / "uninstall.bat"
        uninstall_content = f'''@echo off
setlocal enabledelayedexpansion
title Uninstalling {self.app_name}
echo Uninstalling {self.app_name}...
timeout /t 2 /nobreak
rmdir /s /q "{install_dir}" 2>nul
set /p delete_backup="Also delete saved projects? (y/n) "
if /i "%%delete_backup%%"=="y" (
    rmdir /s /q "{backup_dir}" 2>nul
)
del "%USERPROFILE%\\Desktop\\{self.app_name}.lnk" 2>nul
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\{self.app_name}.lnk" 2>nul
reg delete "HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.app_name}" /f 2>nul
echo Uninstall complete!
pause
exit
'''
        with open(uninstall_bat, 'w') as f:
            f.write(uninstall_content)

    def _create_shortcut(self, exe_path):
        try:
            desktop_path = Path.home() / "Desktop" / f"{self.app_name}.lnk"
            self._create_lnk(exe_path, desktop_path)
            
            start_menu = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            start_menu.mkdir(parents=True, exist_ok=True)
            self._create_lnk(exe_path, start_menu / f"{self.app_name}.lnk")
        except Exception:
            pass
    
    def _create_lnk(self, target, shortcut_path):
        vbs_content = f'''
            Set oWS = WScript.CreateObject("WScript.Shell")
            Set oLink = oWS.CreateShortcut("{shortcut_path}")
            oLink.TargetPath = "{target}"
            oLink.WorkingDirectory = "{Path(target).parent}"
            oLink.Description = "{self.app_name}"
            oLink.Save
        '''
        vbs_path = Path.home() / "create_shortcut.vbs"
        with open(vbs_path, 'w') as f:
            f.write(vbs_content)
        try:
            subprocess.run(['cscript', str(vbs_path)], check=True, capture_output=True)
        finally:
            if vbs_path.exists(): os.remove(vbs_path)
    
    def _register_uninstaller(self, install_dir, exe_path):
        try:
            registry_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall"
            app_key = self.app_name.replace(" ", "_")
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, f"{registry_path}\\{app_key}") as key:
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, self.app_name)
                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, str(install_dir / "uninstall.bat"))
                winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, self.company_name)
        except Exception:
            pass

class InstallerWindow(QMainWindow):
    """Professional installer UI"""
    def __init__(self):
        super().__init__()
        self.app_name = "OmniBoard Studio"
        self.setWindowTitle(f"{self.app_name} - Online Installer")
        self.setGeometry(100, 100, 600, 450)
        self._setup_ui()
        self.show()
    
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Headers
        title = QLabel(f"{self.app_name}")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        layout.addWidget(QLabel("This installer will download the latest version from GitHub."))
        
        # Path
        layout.addWidget(QLabel("Installation Directory:"))
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setText(os.path.expanduser(os.path.join(os.path.dirname(sys.executable), f"{self.app_name}")))
        path_layout.addWidget(self.path_input)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        # Options
        self.shortcut_check = QCheckBox("Create desktop shortcut")
        self.shortcut_check.setChecked(True)
        layout.addWidget(self.shortcut_check)
        
        # Progress & Status
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.install_btn = QPushButton("Download & Install")
        self.install_btn.setMinimumHeight(40)
        self.install_btn.clicked.connect(self._start)
        btn_layout.addWidget(self.install_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(cancel_btn)
        layout.addStretch()
        layout.addLayout(btn_layout)
        
    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "Select Directory", self.path_input.text())
        if d: self.path_input.setText(d)
        
    def _start(self):
        self.install_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.worker = InstallerWorker(self.path_input.text(), self.shortcut_check.isChecked())
        self.worker.progress.connect(self.progress.setValue)
        self.worker.status.connect(self.status_label.setText)
        self.worker.finished.connect(self._done)
        self.worker.start()
        
    def _done(self, success, msg):
        self.install_btn.setEnabled(True)
        if success:
            QMessageBox.information(self, "Success", msg)
            self.close()
        else:
            QMessageBox.critical(self, "Error", msg)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = InstallerWindow()
    sys.exit(app.exec())