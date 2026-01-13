# GUI Installer - Complete Setup Guide

## What You Have Now

A **professional Windows installer with GUI** that:
- ✅ Asks user where to install
- ✅ Creates desktop shortcut (optional)
- ✅ Bundles resources folder with subfolders
- ✅ Shows progress bar
- ✅ Creates uninstaller
- ✅ Modern Windows UI

---

## File Structure You Need

```
your-project/
├── dist/
│   └── main_pyqt.exe              ← Built by build_exe.py
├── resources/                      ← Your resources folder
│   ├── icons/
│   ├── templates/
│   ├── data/
│   └── ... (any subfolders)
├── installer_gui.py                ← NEW installer (this file)
├── build_exe.py                    ← Existing build script
├── main_pyqt.py
├── GUI_pyqt.py
├── ... (all your app files)
└── requirements.txt
```

---

## Step-by-Step Setup

### Step 1: Build Your Application .exe

```bash
python build_exe.py
```

**Expected output:**
```
✓ Removed build/
[*] Building executable with PyInstaller...
[✓] Build successful!
    dist/main_pyqt.exe - Your standalone executable
```

Now you have: `dist/main_pyqt.exe`

### Step 2: Create Your Resources Folder Structure

Make sure you have a `resources/` folder in your project with subfolders:

```
resources/
├── icons/
│   ├── icon.png
│   ├── logo.png
│   └── ...
├── templates/
│   ├── template1.json
│   └── ...
├── data/
│   └── ...
└── config.json
```

**These will be copied to the installation directory.**

### Step 3: Build the Installer GUI

Now create an installer of the installer:

```bash
pyinstaller installer_gui.py --onefile --windowed --name="Install Visual Programming" --distpath=dist
```

This creates: `dist/Install Visual Programming.exe`

**Or faster:** Use this build script:

```python
# build_installer.py
import PyInstaller.__main__

PyInstaller.__main__.run([
    'installer_gui.py',
    '--onefile',
    '--windowed',
    '--name=Install Visual Programming',
    '--distpath=dist',
    '--hidden-import=PyQt6.QtCore',
    '--hidden-import=PyQt6.QtGui',
    '--hidden-import=PyQt6.QtWidgets',
    '--noconfirm',
])
print("✓ Installer created: dist/Install Visual Programming.exe")
```

Then: `python build_installer.py`

### Step 4: Create Distribution Package

Create a folder structure for distribution:

```
Visual-Programming-v1.0.0/
├── Install Visual Programming.exe   ← Installer
├── README.md                        ← Instructions
└── resources/                       ← Bundled with installer (optional)
    ├── icons/
    ├── templates/
    └── data/
```

### Step 5: Test the Installer

1. **On same machine:**
   - Double-click `Install Visual Programming.exe`
   - Choose installation location (e.g., `C:\Program Files\Visual Programming`)
   - Check "Create desktop shortcut"
   - Click Install
   - Verify desktop shortcut appears
   - Click shortcut to launch app

2. **On different machine:**
   - Extract ZIP to different location
   - Run installer
   - Verify installation works

### Step 6: Create Final Distribution ZIP

```
Visual-Programming-v1.0.0.zip
├── Install Visual Programming.exe
├── README.md
├── resources/  (optional)
│   └── ...
└── LICENSE (optional)
```

Users just need to:
1. Extract ZIP
2. Double-click `Install Visual Programming.exe`
3. Choose location
4. Done!

---

## What The Installer Does

### During Installation:

1. **Validates paths** (5%)
   - Checks exe exists
   
2. **Creates directory** (10%)
   - Makes installation folder
   
3. **Copies executable** (25%)
   - Copies main_pyqt.exe to installation folder
   
4. **Copies resources** (45%)
   - Copies resources/ folder with all subfolders
   
5. **Creates desktop shortcut** (65%)
   - Optional: Creates Windows shortcut
   
6. **Creates uninstaller** (80%)
   - Adds uninstall.bat to installation folder
   
7. **Saves metadata** (90%)
   - Creates install_info.json
   
8. **Complete** (100%)
   - Shows success message

### Installation Directory Structure:

After installation, user sees:
```
C:\Program Files\Visual Programming\
├── main_pyqt.exe          ← The application
├── resources/             ← All your resources
│   ├── icons/
│   ├── templates/
│   └── data/
├── uninstall.bat          ← Uninstaller
├── install_info.json      ← Installation info
```

---

## Customizing the Installer

### Change Installation Path Default

**In installer_gui.py, find this line:**

```python
self.path_input.setText(os.path.expanduser("~\\AppData\\Local\\Visual Programming"))
```

Change to:

```python
# Program Files (recommended)
self.path_input.setText("C:\\Program Files\\Visual Programming")

# Or Documents
self.path_input.setText(os.path.expanduser("~\\Documents\\Visual Programming"))

# Or App Data
self.path_input.setText(os.path.expanduser("~\\AppData\\Local\\MyApp"))
```

### Change App Name

Find and replace all:
```python
"Visual Programming Interface"
```

With your app name:
```python
"My Cool App"
```

### Add Icon to Installer

Create or add an icon file, then modify the build command:

```bash
pyinstaller installer_gui.py --onefile --windowed --icon=icon.ico --name="Install My App"
```

---

## Complete Workflow (Summary)

### For You (Developer):

```bash
# 1. Build main application
python build_exe.py
  → Creates dist/main_pyqt.exe

# 2. Build installer
python build_installer.py
  → Creates dist/Install Visual Programming.exe

# 3. Create distribution folder
mkdir Visual-Programming-v1.0.0
copy dist/Install Visual Programming.exe Visual-Programming-v1.0.0/
copy README.md Visual-Programming-v1.0.0/
xcopy /E resources Visual-Programming-v1.0.0/resources

# 4. Create ZIP
Right-click Visual-Programming-v1.0.0
→ Send to → Compressed (zipped) folder

# 5. Send ZIP to users!
```

### For Your Users:

```
1. Extract ZIP
2. Double-click "Install Visual Programming.exe"
3. Choose where to install
4. Click Install
5. Done! Desktop shortcut created
6. Click shortcut to run app
```

---

## Uninstalling

Users can uninstall by:

**Option 1: Uninstall batch file**
```
C:\Program Files\Visual Programming\
→ Run uninstall.bat
```

**Option 2: Delete folder**
```
Delete C:\Program Files\Visual Programming\
Delete C:\Users\[User]\Desktop\Visual Programming Interface.lnk
```

---

## Troubleshooting

### "Executable not found: dist/main_pyqt.exe"

**Solution:** You need to build the application first:
```bash
python build_exe.py
```

### Installer won't create shortcut

**Solution:** Run as Administrator, or check if VBS is disabled on system

### Resources folder not copied

**Solution:** Make sure you have a `resources/` folder in project root

### Installer won't launch

**Solution:** Make sure PyQt6 is installed:
```bash
pip install PyQt6
```

---

## Files You Now Have

1. **`build_exe.py`** - Builds main application .exe
2. **`installer_gui.py`** - GUI installer source code
3. **`build_installer.py`** - Builds installer .exe (optional script)

---

## Next Steps

### Option 1: Simple (Just Files)
```bash
# Build app
python build_exe.py

# Build installer
pyinstaller installer_gui.py --onefile --windowed --name="Install My App"

# Users extract ZIP and run: Install My App.exe
```

### Option 2: Professional (Add Icons)
```bash
# Same as above, but add icon to installer
pyinstaller installer_gui.py --onefile --windowed --icon=icon.ico --name="Install My App"
```

### Option 3: Advanced (Customized)
```bash
# Edit installer_gui.py
# - Change colors
# - Change app name
# - Change default install path
# - Add company branding

# Then rebuild
pyinstaller installer_gui.py --onefile --windowed --icon=icon.ico
```

---

## Summary

You now have a **professional Windows installer** that:

✅ Has a modern UI  
✅ Lets users choose installation folder  
✅ Creates desktop shortcut  
✅ Bundles resources folder  
✅ Includes uninstaller  
✅ Shows progress  
✅ Handles errors gracefully  

Users just need to:

1. Extract ZIP
2. Run installer
3. Click Install
4. Done!

Your code is protected in .exe format and easy for non-technical users to install.

---

*Created: January 13, 2026*
