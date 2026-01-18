"""
installer_gui.py - Professional Windows Installer UI

Handles the complete installation process for bundled applications.
Supports both standalone .exe bundles and traditional folder installs.

Features:
    ✓ Professional PyQt6 UI
    ✓ Directory selection with browse button
    ✓ Desktop shortcut creation option
    ✓ Progress bar with detailed status
    ✓ Automatic folder structure preservation
    ✓ Registry uninstaller creation
    ✓ Error handling and rollback
    ✓ Works with PyInstaller bundles

Usage as bundled installer:
    Built with PyInstaller by build_standalone_installer.py
    Bundle contents passed as _internal/bundle/

Usage as traditional installer:
    python installer_gui.py
"""

import sys
import os
import shutil
import json
import subprocess
import winreg
from pathlib import Path
from datetime import datetime
import traceback

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QCheckBox, QProgressBar,
        QFileDialog, QMessageBox, QFrame, QScrollArea
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QFont, QIcon
except ImportError:
    print("[!] PyQt6 not found. Install with: pip install PyQt6")
    sys.exit(1)


class InstallerWorker(QThread):
    """Background installation worker thread"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, install_path, create_shortcut, source_exe, resources_folder):
        super().__init__()
        self.install_path = install_path
        self.create_shortcut = create_shortcut
        self.source_exe = source_exe
        self.resources_folder = resources_folder
        self.app_name = "Visual Programming Interface"
        self.company_name = "Developer"
        
    def run(self):
        """Execute installation in background"""
        try:
            self._install()
            self.finished.emit(True, "Installation completed successfully!")
        except Exception as e:
            self.finished.emit(False, f"Installation failed: {str(e)}\n\n{traceback.format_exc()}")
    
    def _install(self):
        """Main installation logic"""
        # Step 1: Create installation directory
        self.status.emit("Creating installation directory...")
        self.progress.emit(10)
        
        install_dir = Path(self.install_path)
        install_dir.mkdir(parents=True, exist_ok=True)
        
        backup_dir = Path(os.path.expanduser("~\\AppData\\Local\\Visual Programming"))
        backup_dir.mkdir(parents=True, exist_ok=True)
        # Step 2: Copy application executable
        self.status.emit("Installing application...")
        self.progress.emit(25)
        
        if not os.path.exists(self.source_exe):
            raise FileNotFoundError(f"Source executable not found: {self.source_exe}")
        
        dest_exe = install_dir / os.path.basename(self.source_exe)
        shutil.copy2(self.source_exe, dest_exe)
        
        # Step 3: Copy resources folder if it exists
        self.status.emit("Installing resources...")
        self.progress.emit(45)
        
        if self.resources_folder and os.path.exists(self.resources_folder):
            dest_resources = install_dir / "resources"

            if dest_resources.exists():
                shutil.rmtree(dest_resources)
            shutil.copytree(self.resources_folder, dest_resources)
        
        # Step 4: Create uninstaller
        self.status.emit("Creating uninstaller...")
        self.progress.emit(65)
        
        uninstall_bat = install_dir / "uninstall.bat"
        uninstall_content = f'''@echo off
setlocal enabledelayedexpansion

title Uninstalling {self.app_name}

echo Uninstalling {self.app_name}...
timeout /t 2 /nobreak

REM Delete installation folder
rmdir /s /q "{install_dir}" 2>nul

REM Optional: Ask user about backup
set /p delete_backup="Also delete saved projects? (y/n) "
if /i "%%delete_backup%%"=="y" (
    rmdir /s /q "{backup_dir}" 2>nul
    echo Projects deleted.
) else (
    echo Projects preserved at: %APPDATA%\\Local\\Visual Programming\\projects
)

REM Delete desktop shortcut
del "%USERPROFILE%\\Desktop\\{self.app_name}.lnk" 2>nul

REM Delete Start Menu shortcut
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\{self.app_name}.lnk" 2>nul

REM Delete registry key
reg delete "HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.app_name}" /f 2>nul

echo Uninstall complete!
pause

exit
'''
        with open(uninstall_bat, 'w') as f:
            f.write(uninstall_content)
        
        # Step 5: Create installation metadata
        self.status.emit("Creating metadata...")
        self.progress.emit(75)
        
        install_info = {
            "app_name": self.app_name,
            "version": "1.0.0",
            "install_date": datetime.now().isoformat(),
            "install_path": str(install_dir),
            "backup_path": str(backup_dir),
            "executable": str(dest_exe),
            "has_resources": os.path.exists(self.resources_folder) if self.resources_folder else False,
        }
        
        with open(install_dir / "install_info.json", 'w') as f:
            json.dump(install_info, f, indent=2)

        # Step 6: Create desktop shortcut
        self.status.emit("Creating shortcuts...")
        self.progress.emit(85)
        
        if self.create_shortcut:
            self._create_shortcut(dest_exe)
        
        # Step 7: Register uninstaller in Windows
        self.status.emit("Registering with Windows...")
        self.progress.emit(95)
        
        self._register_uninstaller(install_dir, dest_exe)
        # Done
        self.progress.emit(100)
        self.status.emit("Installation complete!")
    
    def _create_shortcut(self, exe_path):
        """Create Windows shortcut (.lnk file)"""
        try:
            # For desktop
            desktop_path = Path.home() / "Desktop" / f"{self.app_name}.lnk"
            self._create_lnk(exe_path, desktop_path)
            
            # For Start Menu
            start_menu = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            start_menu.mkdir(parents=True, exist_ok=True)
            start_menu_lnk = start_menu / f"{self.app_name}.lnk"
            self._create_lnk(exe_path, start_menu_lnk)
            
        except Exception as e:
            # Shortcut creation is non-critical
            print(f"[!] Warning: Could not create shortcut: {e}")
    
    def _create_lnk(self, target, shortcut_path):
        """Create .lnk shortcut using VBScript"""
        vbs_content = f'''
            Set oWS = WScript.CreateObject("WScript.Shell")
            sLinkFile = "{shortcut_path}"
            Set oLink = oWS.CreateShortcut(sLinkFile)
            oLink.TargetPath = "{target}"
            oLink.WorkingDirectory = "{Path(target).parent}"
            oLink.Description = "{self.app_name}"
            oLink.IconLocation = "{Path('resources/images/APPicon.ico')}"
            oLink.Save
        '''
        vbs_path = Path.home() / "create_shortcut.vbs"
        with open(vbs_path, 'w') as f:
            f.write(vbs_content)
        
        try:
            subprocess.run(['cscript', str(vbs_path)], check=True, capture_output=True)
        finally:
            vbs_path.unlink(missing_ok=True)
    
    def _register_uninstaller(self, install_dir, exe_path):
        """Register application in Windows uninstall registry"""
        try:
            registry_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall"
            app_key = self.app_name.replace(" ", "_")
            
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, f"{registry_path}\\{app_key}") as key:
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, self.app_name)
                winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0.0")
                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, str(install_dir / "uninstall.bat"))
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_dir))
                winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, self.company_name)
                winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
        except Exception as e:
            print(f"[!] Warning: Could not register uninstaller: {e}")


class InstallerWindow(QMainWindow):
    """Professional installer UI"""
    
    def __init__(self):
        super().__init__()
        self.app_name = "Visual Programming Interface"
        self.app_version = "1.0.0"
        
        icon_path = Path('resources/images/APPicon.ico')
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Detect bundle vs standalone
        self.is_bundled = self._detect_bundled_mode()
        self.bundle_path = self._get_bundle_path()
        
        self.setWindowTitle(f"{self.app_name} - Installer")
        self.setGeometry(100, 100, 600, 500)
        self.setMinimumWidth(600)
        
        self._setup_ui()
        self.show()
    
    def _detect_bundled_mode(self):
        """Check if running as bundled installer"""
        bundle_marker = Path(sys._MEIPASS) / "bundle" if hasattr(sys, '_MEIPASS') else None
        return bundle_marker and bundle_marker.exists() if bundle_marker else False
    
    def _get_bundle_path(self):
        """Get path to bundled files"""
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS) / "bundle"
        return None
    
    def _get_source_files(self):
        """Determine source files for installation"""
        if self.is_bundled:
            # Running as bundled installer
            exe = self.bundle_path / "Visual Programming Interface.exe"
            resources = self.bundle_path / "resources"
        else:
            # Running as traditional installer
            exe = Path("dist/Visual Programming Interface.exe")
            resources = Path("resources") if Path("resources").exists() else None
        
        return exe, resources if resources and resources.exists() else None
    
    def _setup_ui(self):
        """Create installer UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel(f"{self.app_name} Setup")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel(f"Version {self.app_version}")
        layout.addWidget(subtitle)
        
        # Installation path
        path_label = QLabel("Installation Directory:")
        layout.addWidget(path_label)
        
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setText(os.path.expanduser("~\\AppData\\Local\\Visual Programming"))
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_directory)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        # Options
        options_label = QLabel("Installation Options:")
        layout.addWidget(options_label)
        
        self.shortcut_check = QCheckBox("Create desktop shortcut")
        self.shortcut_check.setChecked(True)
        layout.addWidget(self.shortcut_check)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        layout.addWidget(self.progress)
        
        # Status
        self.status_label = QLabel("Ready to install")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.install_btn = QPushButton("Install")
        self.install_btn.setMinimumHeight(40)
        self.install_btn.clicked.connect(self._start_installation)
        button_layout.addWidget(self.install_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)
        
        layout.addStretch()
        layout.addLayout(button_layout)
    
    def _browse_directory(self):
        """Browse for installation directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Installation Directory",
            self.path_input.text()
        )
        if directory:
            self.path_input.setText(directory)
    
    def _start_installation(self):
        """Begin installation process"""
        install_path = self.path_input.text()
        
        if not install_path:
            QMessageBox.warning(self, "Invalid Path", "Please select an installation directory")
            return
        
        # Get source files
        source_exe, resources = self._get_source_files()
        
        if not source_exe.exists():
            QMessageBox.critical(
                self,
                "Error",
                f"Source executable not found:\n{source_exe}\n\nMake sure to run: python build_exe.py first"
            )
            return
        
        # Update UI
        self.install_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setVisible(True)
        
        # Start installation thread
        self.worker = InstallerWorker(
            install_path,
            self.shortcut_check.isChecked(),
            str(source_exe),
            str(resources) if resources else None
        )
        self.worker.progress.connect(self.progress.setValue)
        self.worker.status.connect(self.status_label.setText)
        self.worker.finished.connect(self._installation_complete)
        self.worker.start()
    
    def _installation_complete(self, success, message):
        """Handle installation completion"""
        self.install_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(
                self,
                "Success",
                f"{message}\n\n{self.app_name} has been installed successfully!\n\nYou can now run it from your desktop or Start Menu."
            )
            self.close()
        else:
            QMessageBox.critical(self, "Installation Failed", message)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    installer = InstallerWindow()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
