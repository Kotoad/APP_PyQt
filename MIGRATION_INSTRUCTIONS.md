# COMPLETE MIGRATION GUIDE - QGraphicsView Implementation

## Files Created/Updated:

1. **GUI_pyqt_updated.py** - Complete rewrite ✓
2. **Path_manager_pyqt_updated.py** - Updated for graphics items ✓
3. **spawn_elements_pyqt.py** - NEEDS MINOR UPDATES (see below)

---

## STEP-BY-STEP MIGRATION INSTRUCTIONS

### Step 1: Backup Your Current Files
```bash
# Create backups
cp GUI_pyqt.py GUI_pyqt_backup.py
cp Path_manager_pyqt.py Path_manager_pyqt_backup.py
cp spawn_elements_pyqt.py spawn_elements_pyqt_backup.py
```

### Step 2: Replace Main Files
```bash
# Replace with updated versions
cp GUI_pyqt_updated.py GUI_pyqt.py
cp Path_manager_pyqt_updated.py Path_manager_pyqt.py
```

### Step 3: Update Imports in spawn_elements_pyqt.py

**FIND THIS LINE** (around line 1800):
```python
def add_draggable_widget(self, widget):
    """Make a widget draggable on the canvas"""
    widget.setParent(self)
    widget.show()
    widget.raise_()
    # ... old dragging code
```

**REPLACE WITH:**
```python
def add_draggable_widget(self, canvas, block_widget):
    """Add widget as block to canvas (now handled by graphics view)"""
    # The block is already a graphics item in the canvas
    # No need for custom drag handling - QGraphicsView handles it
    block_widget.raise_()
    print(f"Block {block_widget.block_id} added to canvas")
```

### Step 4: Update create_block_from_data() in spawn_elements_pyqt.py

**FIND THIS METHOD** (around line 1600):
```python
def create_block_from_data(self, block_id, block_type, x, y, ...):
    # Old code creating BlockWidget
    blockwidget = BlockWidget(self.parent, block_type, block_id=block_id)
    blockwidget.move(x, y)
    return blockwidget
```

**UPDATE TO:**
```python
def create_block_from_data(self, block_id, block_type, x, y, value_1='', value_2='', combo_value='', switch_value=False):
    """Create a block from saved data and add to canvas"""
    # Canvas will handle graphics item creation
    canvas = self.parent  # parent is now the canvas
    
    # Add block to canvas as graphics item
    block_graphics = canvas.add_block(block_type, x, y, block_id)
    
    # Create actual widget with custom inputs
    # (This depends on your BlockWidget implementation)
    block_widget = BlockWidget(canvas, block_type, block_id=block_id)
    block_widget.move(x, y)
    block_widget.show()
    
    # Store reference
    block_graphics.block_widget = block_widget
    
    return block_graphics
```

### Step 5: Update custom_shape_spawn() method

**FIND THIS METHOD** (around line 2000):
```python
def custom_shape_spawn(self, parent, element_type, event):
    # Old code
    block = BlockWidget(parent, element_type, block_id=block_id)
    parent.add_draggable_widget(block)
```

**UPDATE TO:**
```python
def custom_shape_spawn(self, parent, element_type, event):
    """Spawn a new block element"""
    block_id = f"{element_type}_{int(time.time() * 1000)}"
    
    # Get mouse position from canvas
    scene_pos = parent.mapToScene(event.pos())
    x, y = scene_pos.x(), scene_pos.y()
    
    # Create graphics item block
    block_graphics = parent.add_block(element_type, x, y, block_id)
    
    # Create widget with custom controls
    block_widget = BlockWidget(parent, element_type, block_id=block_id)
    block_widget.move(x, y)
    block_widget.show()
    
    block_graphics.block_widget = block_widget
    
    print(f"Spawned {element_type} at ({x}, {y})")
```

---

## KEY ARCHITECTURAL CHANGES

### OLD APPROACH:
```
Canvas (QWidget with manual paintEvent)
├── BlockWidget (physical QWidget)
│   ├── Timer input, If inputs, etc.
│   └── Custom drag handling
├── Manual pan_x, pan_y, zoom_level
└── Manual painter.translate(), painter.scale()
```

### NEW APPROACH:
```
Canvas (QGraphicsView)
├── BlockGraphicsItem (scene item - automatic drag!)
│   ├── block_widget (reference to custom widget if needed)
│   └── Automatic zoom/pan via view transforms
└── Automatic everything via Qt graphics system!
```

---

## TESTING CHECKLIST

After migration, test:

- [ ] **Dragging blocks** - Click and drag a block, should move smoothly
- [ ] **Zoom in** - Mouse wheel up, blocks scale larger
- [ ] **Zoom out** - Mouse wheel down, blocks scale smaller
- [ ] **Pan** - Middle mouse button drag to pan around
- [ ] **Reset zoom** - Press Home key to reset zoom level
- [ ] **Add block** - Right-click → Add Block (should appear at click position)
- [ ] **Delete block** - Right-click block → Delete Block
- [ ] **Create connections** - Draw lines between blocks
- [ ] **Move block with connections** - Paths should update automatically
- [ ] **Save/Load** - Save project, load it back
- [ ] **Performance** - Zoom/pan should be smooth even with many blocks

---

## COMMON ISSUES & FIXES

### Issue: "BlockGraphicsItem has no attribute 'height()'"
**Fix:** Use `block_graphics.rect().height()` instead

### Issue: Blocks not visible after spawn
**Fix:** Make sure `canvas.add_block()` is called AND block is added to scene

### Issue: Paths don't update when moving blocks
**Fix:** Ensure `itemChange()` in BlockGraphicsItem calls `path_manager.update_paths_for_widget()`

### Issue: Zoom doesn't work
**Fix:** Make sure you're using `wheelEvent()` in QGraphicsView (not QWidget)

### Issue: Custom inputs (If block inputs) not visible
**Fix:** You may need to manually position input widgets relative to graphics items

---

## OPTIONAL: Keep Custom Block Widgets

If you want to keep your custom BlockWidget controls (If inputs, Timer input, etc.), you can:

```python
class BlockGraphicsItem(QGraphicsRectItem):
    def __init__(self, ...):
        # ... existing code ...
        
        # Create custom widget if needed
        if block_type in ["If", "While", "Timer"]:
            self.block_widget = BlockWidget(parent_canvas, block_type, self.block_id)
            self.block_widget.move(x, y)
            self.block_widget.show()
```

This way you get:
- ✅ Automatic graphics item dragging
- ✅ Custom input widgets (If, Timer, etc.)
- ✅ Automatic zoom/pan for graphics items
- ✅ Best of both worlds!

---

## SUMMARY OF CHANGES

| Component | Before | After | Benefit |
|-----------|--------|-------|---------|
| Base class | QWidget | QGraphicsView | Native zoom/pan support |
| Dragging | Manual (100 lines) | Automatic (1 flag) | Simpler, more reliable |
| Zoom | Manual transformations | `self.scale()` | Native support |
| Pan | Manual offset management | Built-in ScrollHandDrag | Natural interaction |
| Grid | Custom paintEvent | scene.addLine() | Cleaner code |
| Item positioning | Coordinate conversion | Direct scene coords | No math needed |
| Performance | Manual rendering | Qt optimizations | Faster, smoother |

---

## MIGRATION TIME: ~2 hours total

1. Backup files: 5 min
2. Replace core files: 5 min
3. Update spawn_elements.py: 30 min
4. Test functionality: 30 min
5. Fix any issues: 30 min
6. Optimize/polish: 20 min

**Total: ~2 hours**

**Result: Cleaner, faster, more maintainable code!** ✨