# Migrating from Custom Canvas to QGraphicsView + QGraphicsScene

## Why Switch?

Your current approach:
- ❌ Manual zoom/pan management
- ❌ Widget positioning conflicts with painter transformations
- ❌ Complex coordinate conversion logic
- ❌ Manual dragging implementation

QGraphicsView approach:
- ✅ Automatic zoom/pan for all items
- ✅ Built-in dragging with `ItemIsMovable`
- ✅ Automatic coordinate system management
- ✅ Simple geometry: everything in scene coordinates
- ✅ Handles selection, focus, events automatically

---

## Step-by-Step Migration

### Step 1: Replace GridCanvas with QGraphicsView

**BEFORE (Current):**
```python
class GridCanvas(QWidget):
    def __init__(self, parent=None, grid_size=25):
        super().__init__(parent)
        self.pan_x = 0
        self.pan_y = 0
        self.zoom_level = 1.0
        # ... manual drag handling
```

**AFTER (Graphics View):**
```python
class GridCanvas(QGraphicsView):
    def __init__(self, parent=None, grid_size=25):
        super().__init__(parent)
        
        # Create scene
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        self.setScene(self.scene)
        
        # Grid setup
        self.grid_size = grid_size
        self.draw_grid()
        
        # Zoom setup
        self.zoom_level = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        
        # Enable smooth rendering
        self.setRenderHint(QGraphicsView.RenderHint.Antialiasing)
        self.setRenderHint(QGraphicsView.RenderHint.SmoothPixmapTransform)
        
        # Enable middle-click panning
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
```

---

### Step 2: Create Custom Graphics Items

**Replace BlockWidget with BlockGraphicsItem:**

```python
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QPen, QBrush, QColor

class BlockGraphicsItem(QGraphicsRectItem):
    """Custom graphics item for blocks"""
    
    def __init__(self, x, y, width, height, block_id, block_type, parent_canvas):
        super().__init__(x, y, width, height)
        
        self.block_id = block_id
        self.block_type = block_type
        self.canvas = parent_canvas
        
        # Make draggable and selectable
        self.setAcceptHoverEvents(True)
        self.setFlag(self.ItemIsMovable, True)  # ← Automatic dragging!
        self.setFlag(self.ItemIsSelectable, True)
        self.setFlag(self.ItemSendsGeometryChanges, True)
        
        # Style
        self.setPen(QPen(QColor("black"), 2))
        self.setBrush(QBrush(QColor("lightblue")))
        
        # Add custom children (like inputs, dropdowns, etc.)
        self.block_inputs = {}
        
    def itemChange(self, change, value):
        """Called when item position/selection changes"""
        from PyQt6.QtWidgets import QGraphicsItem
        
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Update stored position
            pos = self.pos()
            Utils.top_infos[self.block_id]['x'] = pos.x()
            Utils.top_infos[self.block_id]['y'] = pos.y()
            
            # Update connected paths
            if hasattr(self.canvas, 'path_manager'):
                self.canvas.path_manager.update_paths_for_widget(self)
        
        return super().itemChange(change, value)
    
    def mousePressEvent(self, event):
        """Handle selection"""
        self.setSelected(True)
        super().mousePressEvent(event)
    
    def contextMenuEvent(self, event):
        """Handle right-click menu"""
        # Get scene pos (in scene coordinates)
        scene_pos = event.scenePos()
        
        # Show context menu (similar to current implementation)
        # self.canvas.show_block_context_menu(self, scene_pos)
        
        super().contextMenuEvent(event)
```

---

### Step 3: Update Paths to Use Graphics Items

**Path Graphics Item:**

```python
from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtGui import QPainterPath, QPen, QColor

class PathGraphicsItem(QGraphicsPathItem):
    """Visual representation of a connection"""
    
    def __init__(self, from_block, to_block, path_id, parent_canvas):
        super().__init__()
        
        self.from_block = from_block
        self.to_block = to_block
        self.path_id = path_id
        self.canvas = parent_canvas
        
        # Style
        pen = QPen(QColor(31, 83, 141))
        pen.setWidth(2)
        self.setPen(pen)
        
        # Update path
        self.update_path()
    
    def update_path(self):
        """Update path when blocks move"""
        from_pos = self.from_block.pos() + QPointF(self.from_block.rect().width(), self.from_block.rect().height() / 2)
        to_pos = self.to_block.pos() + QPointF(0, self.to_block.rect().height() / 2)
        
        path = QPainterPath()
        path.moveTo(from_pos)
        # Create orthogonal path
        mid_x = (from_pos.x() + to_pos.x()) / 2
        path.lineTo(mid_x, from_pos.y())
        path.lineTo(mid_x, to_pos.y())
        path.lineTo(to_pos)
        
        self.setPath(path)
```

---

### Step 4: Update Canvas Methods

**Zoom with mouse wheel:**

```python
def wheelEvent(self, event):
    """Zoom with mouse wheel"""
    factor = 1.15
    if event.angleDelta().y() > 0:
        new_zoom = self.zoom_level * factor
    else:
        new_zoom = self.zoom_level / factor
    
    # Clamp to min/max
    new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))
    
    # Zoom toward mouse position
    self.centerOn(self.mapToScene(event.pos()))
    self.scale(new_zoom / self.zoom_level, new_zoom / self.zoom_level)
    self.zoom_level = new_zoom
```

**Add block to canvas:**

```python
def add_block(self, block_type, x, y, block_id):
    """Add a block to the scene"""
    block = BlockGraphicsItem(
        x=x, y=y, width=100, height=36,
        block_id=block_id,
        block_type=block_type,
        parent_canvas=self
    )
    
    self.scene.addItem(block)
    
    # Store in Utils
    Utils.top_infos[block_id] = {
        'widget': block,  # Now it's a graphics item
        'type': block_type,
        'x': x,
        'y': y,
        'width': 100,
        'height': 36
    }
    
    return block
```

**Clear canvas:**

```python
def clear_canvas(self):
    """Clear all items"""
    for item in self.scene.items():
        self.scene.removeItem(item)
    Utils.top_infos.clear()
    Utils.paths.clear()
```

---

### Step 5: Update PathManager

**Since graphics items auto-update positions:**

```python
def update_paths_for_widget(self, widget):
    """Update all paths connected to this widget"""
    for path_id, path_item in self.scene_paths.items():
        if path_item.from_block == widget or path_item.to_block == widget:
            path_item.update_path()  # Simple one-liner!
```

---

### Step 6: Remove Manual Geometry Management

**DELETE THIS:**
```python
def update_widgets_for_zoom_pan(self):
    # NO LONGER NEEDED!
    # Graphics view handles this automatically
    pass
```

---

## Key Differences Summary

| Feature | Custom Widget | QGraphicsView |
|---------|---------------|---------------|
| Zoom/Pan | Manual `painter.scale()`, `painter.translate()` | Automatic with `scale()` |
| Dragging | Manual `mouseMoveEvent()` | Built-in `ItemIsMovable` flag |
| Widget Size | Manual `setGeometry()` | Automatic with scene rect |
| Coordinate System | Mix of screen/logical coords | All in scene coordinates |
| Selection | Manual tracking | Built-in with `ItemIsSelectable` |
| Grid Drawing | Manual in `paintEvent()` | `scene.addLine()` in scene |
| Performance | Slower (manual rendering) | Faster (Qt optimizations) |

---

## Migration Checklist

- [ ] Replace `GridCanvas(QWidget)` → `GridCanvas(QGraphicsView)`
- [ ] Create `BlockGraphicsItem(QGraphicsRectItem)`
- [ ] Create `PathGraphicsItem(QGraphicsPathItem)`
- [ ] Update `add_draggable_widget()` → `add_block()`
- [ ] Remove `update_widgets_for_zoom_pan()`
- [ ] Update `wheelEvent()` for zoom
- [ ] Remove all manual `move()` calls
- [ ] Update PathManager to use graphics items
- [ ] Test drag, zoom, pan, path updates
- [ ] Test save/load with new item positions

---

## Code Structure After Migration

```
GUI_pyqt.py
├── GridCanvas(QGraphicsView)          ← Main canvas
│   ├── BlockGraphicsItem(QGraphicsRectItem)  ← Individual blocks
│   └── PathGraphicsItem(QGraphicsPathItem)   ← Connections
├── PathManager
│   └── update_paths_for_widget()  ← Auto-called when blocks move
└── MainWindow
    └── spawn_elements()
        └── create_block_from_data()  ← Creates BlockGraphicsItem
```

This eliminates all the zoom/pan coordinate conversion nightmares!