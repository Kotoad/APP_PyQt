# Single Standalone Installer (No ZIP Needed!)

## What You're Building

A **single .exe file** that contains:
- ✅ Your application executable
- ✅ All resources (with subfolders preserved)
- ✅ Installer UI
- ✅ Everything needed to install

**Users just download 1 file and run it. That's it!**

---

## Quick Workflow (10 minutes)

### Step 1: Build Your App (5 minutes)
```bash
python build_exe.py
```
**Output:** `dist/main_pyqt.exe`

### Step 2: Build Standalone Installer (5 minutes)
```bash
python build_standalone_installer.py
```
**Output:** `dist/Visual-Programming-v1.0.0.exe` (300-400 MB, self-contained)

### Step 3: Send to Users
Users just get:
```
Visual-Programming-v1.0.0.exe
```

Users run it:
1. Double-click `.exe`
2. Choose install location
3. Click Install
4. Done! Desktop shortcut created

**No ZIP, no extra files, no hassle!**

---

## What Users See

```
┌────────────────────────────────────────┐
│ Visual Programming Interface            │
│ Professional Installation Wizard        │
├────────────────────────────────────────┤
│                                        │
│ Installation Location:                  │
│ [C:\Program Files\...] [Browse]        │
│                                        │
│ ☑ Create desktop shortcut              │
│ ☑ Include resources folder             │
│                                        │
│ Installation Progress:                  │
│ [████░░░░░░░░░░░░░░░░] 40%            │
│ Status: Installing application...      │
│                                        │
│           [Install]  [Cancel]          │
└────────────────────────────────────────┘
```

---

## What Gets Installed

```
C:\Program Files\Visual Programming\
├── main_pyqt.exe           (Your app)
├── resources/              (All your resources)
│   ├── icons/
│   ├── templates/
│   ├── data/
│   └── ... (any structure)
├── uninstall.bat           (Uninstaller)
└── install_info.json       (Metadata)

Desktop:
└── Visual Programming Interface (shortcut)
```

---

## File Sizes

| File | Size |
|------|------|
| `dist/main_pyqt.exe` | 200-300 MB |
| `dist/Visual-Programming-v1.0.0.exe` | 300-400 MB |
| **For Users** | Just 1 file! |

(Larger because it bundles everything inside)

---

## Why This is Better

| Aspect | ZIP Method | Standalone .exe |
|--------|-----------|-----------------|
| Files to send | 3-4 files | **1 file** |
| User steps | Extract → Install | **Just run** |
| Confusing | Extract first | **Never** |
| File size | 60-100 MB | 300-400 MB |
| Professional | Good | **Better** |
| **Best for** | Tech users | **Everyone** |

---

## Complete Workflow

### Your Steps (10 minutes):
```bash
1. python build_exe.py
2. python build_standalone_installer.py
3. Done! Single .exe ready to send
```

### User Steps (2 minutes):
```
1. Download Visual-Programming-v1.0.0.exe
2. Run it
3. Click Install
4. Done!
```

---

## Customization

### Change App Name

Edit `installer_gui.py`:
```python
self.app_name = "Visual Programming Interface"
```

Change to:
```python
self.app_name = "My Cool App"
```

Then rebuild:
```bash
python build_standalone_installer.py
```

### Add Icon

1. Create `icon.ico` (256x256 pixels)
2. Place in project root
3. Run: `python build_standalone_installer.py`

(Auto-detects and uses it)

### Change Default Installation Path

Edit `installer_gui.py`, line ~95:
```python
self.path_input.setText(os.path.expanduser("~\\AppData\\Local\\Visual Programming"))
```

Change to:
```python
self.path_input.setText("C:\\Program Files\\My Cool App")
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "main_pyqt.exe not found" | Run `python build_exe.py` first |
| "Bundle folder error" | Delete `_installer_bundle/` folder, try again |
| "Build fails" | Check PyInstaller: `pip install --upgrade pyinstaller` |
| "Installer too large" | Normal! (300-400 MB is expected) |
| "Resources not included" | Make sure `resources/` folder exists |
| "Installer won't start" | Run as Administrator |

---

## What's Included in the .exe

Inside `Visual-Programming-v1.0.0.exe`:

```
Visual-Programming-v1.0.0.exe
├── installer_gui.py (compiled)
├── PyQt6 libraries
├── Python runtime
└── Bundle:
    ├── main_pyqt.exe
    ├── resources/
    │   ├── icons/
    │   ├── templates/
    │   └── data/
    └── bundle_info.json
```

When user runs it:
1. Extracts to temp folder
2. Runs installer UI
3. User chooses location
4. Copies files to installation folder
5. Creates shortcuts
6. Cleans up temp files
7. Done!

---

## Files You Now Have

```
project/
├── build_exe.py                    (Existing)
├── installer_gui.py                (Existing)
├── build_standalone_installer.py   (NEW!)
├── build_installer.py              (Old way - still works)
├── main_pyqt.py
├── GUI_pyqt.py
├── resources/
└── dist/
    ├── main_pyqt.exe
    └── Visual-Programming-v1.0.0.exe ← Send THIS to users!
```

---

## Distribution

### Before (ZIP way):
- Create ZIP file
- Send multiple files
- User extracts ZIP
- User runs installer
- Confusing for non-technical users

### Now (Standalone way):
```
Send: Visual-Programming-v1.0.0.exe
User: Double-click and run
Done!
```

---

## Key Advantages

✅ **Single file** - No ZIP confusion  
✅ **Professional** - Looks like real Windows software  
✅ **Easy distribution** - Just email one file  
✅ **No technical knowledge** needed from users  
✅ **Everything bundled** - Nothing to forget  
✅ **Clean uninstall** - Just delete folder or run uninstall.bat  

---

## Command Reference

```bash
# Build app
python build_exe.py

# Build standalone installer (no ZIP needed)
python build_standalone_installer.py

# Result: dist/Visual-Programming-v1.0.0.exe

# Test it
dist/Visual-Programming-v1.0.0.exe

# Send to users
Send: dist/Visual-Programming-v1.0.0.exe directly
```

---

## Timeline

| Step | Time |
|------|------|
| Build app | 5 min |
| Build standalone installer | 5 min |
| Test | 2 min |
| **Total** | **12 minutes** |

Done! Your single installer is ready.

---

## For Users

When they receive `Visual-Programming-v1.0.0.exe`:

1. Double-click it
2. Installer UI appears
3. Choose where to install (or accept default)
4. Check "Create desktop shortcut"
5. Click "Install"
6. Wait for progress to complete
7. Click desktop shortcut to run app
8. Everything works!

No technical knowledge needed. Just like installing any Windows app.

---

## Summary

**Old way (ZIP):**
- Create folder structure
- Zip it up
- Users extract
- Users run installer
- Multiple steps

**New way (Standalone .exe):**
- One command: `python build_standalone_installer.py`
- One file: `Visual-Programming-v1.0.0.exe`
- Users run it
- Done!

**Much better! 🎉**

---

*This is the professional way to distribute Windows applications.*  
*Your single installer is production-ready!*
