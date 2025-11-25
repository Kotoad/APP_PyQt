# PyQt6 Version - Visual Programming Interface

## Overview
This is a PyQt6 conversion of the CustomTkinter visual programming interface. The application maintains the same visual style and functionality while using PyQt6's architecture.

## Key Files

### Main Application
- **main_pyqt.py** - Application entry point
- **GUI_pyqt.py** - Main window with menu bar, canvas, and variable panel
- **Utils.py** - Shared utilities (unchanged from original)
- **code_compiler.py** - Code compilation logic (unchanged from original)

### Components
- **Elements_window_pyqt.py** - Tabbed dialog for selecting elements to place
- **spawn_elements_pyqt.py** - Handles element creation and placement
- **Path_manager_pyqt.py** - Manages connections between blocks

## Key Differences from CustomTkinter Version

### Architecture Changes
1. **Widget System**: PyQt uses QWidget hierarchy instead of tkinter/CTk widgets
2. **Event Handling**: PyQt signals/slots instead of tkinter bind()
3. **Painting**: QPainter for custom drawing instead of Canvas
4. **Styling**: QSS (Qt Style Sheets) instead of CTk styling

### Visual Consistency
- **Same color scheme**: #2B2B2B background, #1F538D accent blue
- **Same layout**: Menu bar, grid canvas, side panel
- **Same element shapes**: PIL-generated block images preserved

### Improved Features
1. **Native rendering**: Better antialiasing and scaling
2. **Signal/slot system**: More robust event handling
3. **QSS styling**: More flexible theming
4. **Better DPI handling**: Qt handles DPI automatically

## Installation

```bash
# Install dependencies
pip install PyQt6 pillow

# Run the application
python main_pyqt.py
```

## Usage

1. **Add Elements**: 
   - Menu → Elements → Add Element
   - Or click element buttons in the dialog

2. **Place Elements**: 
   - Click element type in dialog
   - Click on canvas to place
   - Blocks snap to grid

3. **Connect Elements**:
   - Click output circle (right side) to start connection
   - Click input circle (left side) to complete connection
   - Paths automatically route around grid

4. **Move Elements**:
   - Drag blocks to reposition
   - Connections update automatically
   - Releases snap to grid

5. **Variables Panel**:
   - Menu → Variables → Show Variables
   - Add/edit variables for your program

6. **Compile**:
   - Menu → Compile → Compile Code
   - Generates Python code from visual blocks

## Architecture Notes

### GridCanvas (QWidget)
- Custom widget that draws grid and manages draggable blocks
- Overrides paintEvent() for grid rendering
- Handles mouse events for dragging and snapping

### BlockWidget (QWidget)
- Represents individual programming blocks
- Uses PIL to generate block images (same as original)
- Handles connection circle clicks
- Transparent background for non-rectangular shapes

### PathManager
- Manages connection lines between blocks
- Calculates orthogonal grid-aligned paths
- Updates paths when blocks move
- Draws preview during connection creation

### ElementsWindow (QDialog)
- Singleton pattern for element selection
- Tabbed interface (Shapes, Logic, I/O)
- Stays on top, doesn't steal focus

## Style Consistency

The PyQt version maintains exact color matching:
```python
Background:     #2B2B2B (dark gray)
Surface:        #1F1F1F (darker gray)
Accent:         #1F538D (blue)
Hover:          #2667B3 (lighter blue)
Border:         #3A3A3A (medium gray)
Text:           #FFFFFF (white)
```

## Known Limitations

1. **DPI Handling**: Original used Windows-specific DPI calls; PyQt handles this automatically
2. **Global Mouse Listener**: Removed (was Windows-specific with pynput); focus detection simplified
3. **Taskbar Hiding**: Not implemented (was Windows-specific); uses Qt Tool window flag instead

## Future Enhancements

1. **More element types**: Implement While, For Loop, I/O elements
2. **Properties panel**: Edit block properties
3. **Save/Load**: Serialize and restore diagrams
4. **Better path routing**: A* pathfinding for complex layouts
5. **Undo/Redo**: Command pattern for edit history
6. **Zoom**: Canvas zooming and panning

## Migration Guide

If migrating from CustomTkinter version:

| CustomTkinter | PyQt6 | Notes |
|---------------|-------|-------|
| `CTk()` | `QMainWindow` | Main window |
| `CTkCanvas` | `QWidget` + `paintEvent()` | Custom drawing |
| `CTkButton` | `QPushButton` | Buttons |
| `CTkFrame` | `QFrame` / `QWidget` | Containers |
| `CTkLabel` | `QLabel` | Text labels |
| `CTkToplevel` | `QDialog` | Dialogs |
| `.bind()` | signals/slots | Events |
| `.place()` | `.move()` | Positioning |
| `.winfo_x()` | `.x()` | Coordinates |
| `configure()` | `.setStyleSheet()` | Styling |

## License

Same as original project.
