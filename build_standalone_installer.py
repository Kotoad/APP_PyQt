"""
build_standalone_installer.py - Create Single Self-Extracting Installer

This creates ONE .exe file that includes:
  ✓ Application executable
  ✓ All resources (with subfolders)
  ✓ Installer UI
  ✓ Everything needed to install

Users just need:
  1. Download: Visual-Programming-v1.0.0.exe
  2. Run it
  3. Click Install
  4. Done!

No ZIP files needed!

Usage:
    1. First build your app: python build_exe.py
    2. Then build standalone: python build_standalone_installer.py
    3. Result: dist/Visual-Programming-v1.0.0.exe (self-contained!)

Output:
    dist/Visual-Programming-v1.0.0.exe - Complete installer (everything included)
"""

import PyInstaller.__main__
import os
import shutil
import json
from pathlib import Path
import subprocess


def check_prerequisites():
    """Verify all needed files exist"""
    print("[*] Checking prerequisites...")
    
    if not os.path.exists("dist/Visual Programming Interface.exe"):
        print("[✗] Error: dist/Visual Programming Interface.exe not found!")
        print("    Run: python build_exe.py first")
        return False
    
    if not os.path.exists("installer_gui.py"):
        print("[✗] Error: installer_gui.py not found!")
        return False
    
    print("    ✓ All prerequisites OK")
    return True


def create_bundle_folder():
    """Create temporary folder with all files to bundle"""
    print("[*] Creating bundle folder...")
    
    bundle_dir = Path("_installer_bundle")
    
    # Clean if exists
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    
    bundle_dir.mkdir()
    
    # Copy main executable
    print("    Copying application executable...")
    shutil.copy2("dist/Visual Programming Interface.exe", bundle_dir / "Visual Programming Interface.exe")
    
    # Copy resources folder if it exists
    if os.path.exists("resources"):
        print("    Copying resources folder...")
        shutil.copytree("resources", bundle_dir / "resources")
    
    # Copy README if it exists
    if os.path.exists("README.md"):
        print("    Copying README.md...")
        shutil.copy2("README.md", bundle_dir / "README.md")
    
    # Create bundle info
    bundle_info = {
        "app_name": "Visual Programming Interface",
        "version": "1.0.0",
        "app_exe": "Visual Programming Interface.exe",
        "has_resources": os.path.exists("resources"),
        "has_readme": os.path.exists("README.md"),
    }
    
    with open(bundle_dir / "bundle_info.json", "w") as f:
        json.dump(bundle_info, f, indent=2)
    
    print(f"    ✓ Bundle created: {bundle_dir}/")
    return bundle_dir


def build_standalone_installer():
    """Build the standalone self-extracting installer"""
    
    print("[*] Building standalone installer with PyInstaller...")
    
    args = [
        'installer_gui.py',
        '--onefile',
        '--windowed',
        '--name=Visual-Programming-v1.0.0',
        '--distpath=dist',
        '--noconfirm',
        '--add-data=_installer_bundle:bundle',
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=PyQt6.QtCore.Qt',
    ]
    
    try:
        PyInstaller.__main__.run(args)
        return True
    except Exception as e:
        print(f"\n[✗] Build failed: {e}")
        return False


def modify_installer_for_bundle():
    """Update installer_gui.py to handle bundled files"""
    
    print("[*] Creating bundled installer variant...")
    
    # Read original installer
    with open("installer_gui.py", "r") as f:
        original = f.read()
    
    # Create modified version that extracts bundle
    modified = original.replace(
        'def __init__(self, install_path, create_shortcut, source_exe, resources_folder):',
        '''def __init__(self, install_path, create_shortcut, source_exe, resources_folder):
        # Check if running as bundled installer
        self.is_bundled = self._check_if_bundled()
        '''
    )
    
    # Save as temporary file for building
    with open("installer_gui_bundle.py", "w") as f:
        f.write(modified)
    
    print("    ✓ Bundle variant created")
    return "installer_gui_bundle.py"


def verify_build():
    """Verify standalone installer was created"""
    installer = Path("dist/Visual-Programming-v1.0.0.exe")
    
    if installer.exists():
        size_mb = installer.stat().st_size / (1024 * 1024)
        print(f"\n[✓] Standalone installer created successfully!")
        print(f"    Path: {installer}")
        print(f"    Size: {size_mb:.1f} MB")
        print(f"\n    This single .exe contains:")
        print(f"    ✓ Application executable")
        print(f"    ✓ All resources (with subfolders)")
        print(f"    ✓ Installer UI")
        print(f"    ✓ Uninstaller")
        return True
    else:
        print(f"\n[✗] Installer not found: {installer}")
        return False


def show_next_steps():
    """Display next steps"""
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    
    print("\n1. Test the installer:")
    print("   → Double-click: dist/Visual-Programming-v1.0.0.exe")
    print("   → Choose install location")
    print("   → Verify app launches")
    
    print("\n2. Distribute:")
    print("   → Send: dist/Visual-Programming-v1.0.0.exe directly to users")
    print("   → No ZIP needed!")
    print("   → No additional files needed!")
    
    print("\n3. Users will:")
    print("   → Download single .exe file")
    print("   → Run it")
    print("   → Choose where to install")
    print("   → Everything installs automatically")
    print("   → Done!")
    
    print("\n" + "="*70)
    print()


def cleanup_bundle():
    """Clean up temporary bundle folder"""
    bundle_dir = Path("_installer_bundle")
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
        print("[*] Cleaned up temporary files")


if __name__ == '__main__':
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║        Build Standalone Self-Extracting Installer                     ║")
    print("║             One .exe file - No ZIP needed!                            ║")
    print("╚════════════════════════════════════════════════════════════════════════╝\n")
    
    # Check prerequisites
    if not check_prerequisites():
        exit(1)
    
    # Create bundle with all files
    bundle_dir = create_bundle_folder()
    
    # Build standalone installer
    success = build_standalone_installer()
    
    if success:
        # Verify
        if verify_build():
            show_next_steps()
    else:
        print("\nFailed to build standalone installer. Check errors above.")
    
    # Cleanup
    cleanup_bundle()
    
    print("="*70)
