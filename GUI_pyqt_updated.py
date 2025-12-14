"""
GUI_pyqt.py - UPDATED FOR QGraphicsView + QGraphicsScene
Complete refactor for proper zoom/pan/drag handling
"""

from Imports import (
    sys, QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QPushButton, QLabel, QFrame, QScrollArea,
    QLineEdit, QComboBox, QDialog, QPainter, QPen, QColor, QBrush,
    QPalette, QMouseEvent, QRegularExpression, QRegularExpressionValidator,
    QTimer, QMessageBox, QInputDialog, QFileDialog, QFont, Qt, QPoint,
    QRect, QSize, pyqtSignal, AppSettings, ProjectData, QCoreApplication, QAction, math
)

from Imports import (
    get_code_compiler, get_spawn_elements, get_device_settings_window,
    get_file_manager, get_path_manager, get_Elements_Window, get_utils,
    get_Help_Window
)

# Graphics imports
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPathItem, QGraphicsItem
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QPixmap, QImage

Utils = get_utils()
Code_Compiler = get_code_compiler()
spawning_elements = get_spawn_elements()[0]
element_events = get_spawn_elements()[1]
DeviceSettingsWindow = get_device_settings_window()
FileManager = get_file_manager()
PathManager = get_path_manager()
ElementsWindow = get_Elements_Window()

# ============================================================================
# GRAPHICS ITEMS - Core visual elements
# ============================================================================

class BlockGraphicsItem(QGraphicsRectItem):
    """Graphics item representing a block on the canvas"""
    
    def __init__(self, x, y, width, height, block_id, block_type, parent_canvas):
        super().__init__(x, y, width, height)
        
        self.block_id = block_id
        self.block_type = block_type
        self.canvas = parent_canvas
        self.block_widget = None  # Reference to actual block widget if needed
        
        # Make draggable and selectable
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Style
        self.setPen(QPen(QColor("black"), 2))
        self.setBrush(QBrush(QColor("lightblue")))
        
        # Store original size for reference
        self.original_width = width
        self.original_height = height
    
    def itemChange(self, change, value):
        """Handle position/selection changes"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Update stored position in Utils
            pos = self.pos()
            if self.block_id in Utils.top_infos:
                Utils.top_infos[self.block_id]['x'] = pos.x()
                Utils.top_infos[self.block_id]['y'] = pos.y()
            
            # Update connected paths
            if hasattr(self.canvas, 'path_manager'):
                self.canvas.path_manager.update_paths_for_widget(self)
        
        return super().itemChange(change, value)
    
    def mousePressEvent(self, event):
        """Handle block selection"""
        self.setSelected(True)
        super().mousePressEvent(event)
    
    def contextMenuEvent(self, event):
        """Handle right-click context menu"""
        scene_pos = event.scenePos()
        self.canvas.show_block_context_menu(self, scene_pos)
        super().contextMenuEvent(event)


class PathGraphicsItem(QGraphicsPathItem):
    """Graphics item representing a connection path"""
    
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
        """Recalculate path between blocks"""
        from PyQt6.QtGui import QPainterPath
        
        # Get block positions and sizes
        from_rect = self.from_block.rect()
        to_rect = self.to_block.rect()
        
        from_pos = self.from_block.pos() + QPointF(from_rect.width(), from_rect.height() / 2)
        to_pos = self.to_block.pos() + QPointF(0, to_rect.height() / 2)
        
        # Create orthogonal path
        path = QPainterPath()
        path.moveTo(from_pos)
        
        mid_x = (from_pos.x() + to_pos.x()) / 2
        path.lineTo(mid_x, from_pos.y())
        path.lineTo(mid_x, to_pos.y())
        path.lineTo(to_pos)
        
        self.setPath(path)
    
    def contextMenuEvent(self, event):
        """Handle right-click on path"""
        self.canvas.show_path_context_menu(self, event.scenePos())


# ============================================================================
# MAIN CANVAS - QGraphicsView based
# ============================================================================

class GridCanvas(QGraphicsView):
    """Canvas widget using QGraphicsView for proper zoom/pan handling"""
    
    def __init__(self, parent=None, grid_size=25):
        super().__init__(parent)
        
        self.grid_size = grid_size
        self.spawner = None
        self.path_manager = PathManager(self)
        self.elements_events = element_events(self)
        self.file_manager = FileManager()
        
        # Create graphics scene
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        self.setScene(self.scene)
        
        # Zoom setup
        self.zoom_level = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.zoom_speed = 0.1
        
        # Rendering
        self.setRenderHint(QGraphicsView.RenderHint.Antialiasing)
        self.setRenderHint(QGraphicsView.RenderHint.SmoothPixmapTransform)
        
        # Pan mode - middle mouse button
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
        # Draw grid
        self.draw_grid()
        
        # Tracking
        self.main_window = None
        self.dragged_widget = None
        self.offset_x = 0
        self.offset_y = 0
        
        # Style
        self.setStyleSheet("""
            GridCanvas {
                background-color: #2B2B2B;
            }
        """)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def draw_grid(self):
        """Draw grid background"""
        grid_size = self.grid_size
        scene_rect = self.scene.sceneRect()
        
        pen = QPen(QColor("#3A3A3A"), 1)
        
        # Vertical lines
        x = int(scene_rect.left())
        while x < scene_rect.right():
            self.scene.addLine(x, scene_rect.top(), x, scene_rect.bottom(), pen)
            x += grid_size
        
        # Horizontal lines
        y = int(scene_rect.top())
        while y < scene_rect.bottom():
            self.scene.addLine(scene_rect.left(), y, scene_rect.right(), y, pen)
            y += grid_size
    
    def wheelEvent(self, event):
        """Handle zoom with mouse wheel"""
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
        
        event.accept()
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_Home:
            # Reset zoom and pan
            self.resetTransform()
            self.zoom_level = 1.0
            event.accept()
        elif self.spawner and self.spawner.element_placed:
            if event.key() in [Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Enter]:
                self.spawner.stop_placing(self)
                event.accept()
            else:
                event.ignore()
        elif self.path_manager.start_node:
            if event.key() == Qt.Key.Key_Escape:
                self.path_manager.cancel_connection()
                event.accept()
            else:
                event.ignore()
        else:
            super().keyPressEvent(event)
    
    def add_block(self, block_type, x, y, block_id):
        """Add a new block to the canvas"""
        block = BlockGraphicsItem(
            x=x, y=y, width=100, height=36,
            block_id=block_id,
            block_type=block_type,
            parent_canvas=self
        )
        
        self.scene.addItem(block)
        
        # Store in Utils
        Utils.top_infos[block_id] = {
            'widget': block,
            'type': block_type,
            'x': x,
            'y': y,
            'width': 100,
            'height': 36
        }
        
        return block
    
    def add_path(self, from_block, to_block, path_id):
        """Add a connection path between blocks"""
        path = PathGraphicsItem(from_block, to_block, path_id, self)
        self.scene.addItem(path)
        return path
    
    def clear_canvas(self):
        """Clear all blocks and paths from canvas"""
        self.scene.clear()
        Utils.top_infos.clear()
        Utils.paths.clear()
        self.draw_grid()
    
    def remove_block(self, block_id):
        """Remove a block from canvas"""
        if block_id in Utils.top_infos:
            block = Utils.top_infos[block_id]['widget']
            self.scene.removeItem(block)
            del Utils.top_infos[block_id]
    
    def remove_path(self, path_id):
        """Remove a path from canvas"""
        if path_id in Utils.paths:
            path_item = Utils.paths[path_id].get('item')
            if path_item:
                self.scene.removeItem(path_item)
            del Utils.paths[path_id]
    
    def show_block_context_menu(self, block, scene_pos):
        """Show context menu for blocks"""
        menu = QMenu(self)
        
        block_id = block.block_id
        
        edit_action = QAction("Edit Block", self)
        edit_action.triggered.connect(lambda: self.edit_block(block, block_id))
        menu.addAction(edit_action)
        
        duplicate_action = QAction("Duplicate", self)
        duplicate_action.triggered.connect(lambda: self.duplicate_block(block, block_id))
        menu.addAction(duplicate_action)
        
        menu.addSeparator()
        
        delete_action = QAction("Delete Block", self)
        delete_action.triggered.connect(lambda: self.delete_block(block, block_id))
        menu.addAction(delete_action)
        
        # Convert scene coords to screen coords
        screen_pos = self.mapToGlobal(self.mapFromScene(scene_pos))
        menu.exec(screen_pos)
    
    def show_path_context_menu(self, path, scene_pos):
        """Show context menu for paths"""
        menu = QMenu(self)
        
        delete_action = QAction("Delete Connection", self)
        delete_action.triggered.connect(lambda: self.delete_path(path))
        menu.addAction(delete_action)
        
        screen_pos = self.mapToGlobal(self.mapFromScene(scene_pos))
        menu.exec(screen_pos)
    
    def edit_block(self, block, block_id):
        """Edit block properties"""
        print(f"Editing block: {block_id}")
    
    def duplicate_block(self, block, block_id):
        """Create a copy of a block"""
        if block_id not in Utils.top_infos:
            return
        
        block_data = Utils.top_infos[block_id]
        x = block_data['x'] + 50
        y = block_data['y'] + 50
        print(f"Duplicating block {block_id} at ({x}, {y})")
    
    def delete_block(self, block, block_id):
        """Delete a block and its connections"""
        print(f"Deleting block: {block_id}")
        
        if self.path_manager:
            self.path_manager.remove_paths_for_block(block_id)
        
        self.remove_block(block_id)
    
    def delete_path(self, path):
        """Delete a connection path"""
        print(f"Deleting path: {path.path_id}")
        self.remove_path(path.path_id)


# ============================================================================
# MAIN WINDOW
# ============================================================================

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Visual Programming Interface")
        self.resize(1200, 800)
        
        self.code_compiler = Code_Compiler()
        
        self.create_save_shortcut()
        self.setup_auto_save_timer()
        
        # Style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1F1F1F;
            }
            QMenuBar {
                background-color: #2B2B2B;
                color: #FFFFFF;
                padding: 4px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 12px;
            }
            QMenuBar::item:selected {
                background-color: #1F538D;
            }
            QMenu {
                background-color: #2B2B2B;
                color: #FFFFFF;
                border: 1px solid #3A3A3A;
            }
            QMenu::item:selected {
                background-color: #1F538D;
            }
            QLineEdit {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px;
            }
            QComboBox {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px;
            }
            QPushButton {
                background-color: #C74343;
                color: #FFFFFF;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #E05555;
            }
        """)
        
        self.help_window_instance = None
        self.variable_frame = None
        self.variable_frame_visible = False
        self.variable_row_count = 1
        self.Devices_frame = None
        self.devices_frame_visible = False
        self.devices_row_count = 1
        self.blockIDs = {}
        
        self.create_menu_bar()
        self.create_canvas_frame()
    
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = file_menu.addAction("New")
        new_action.triggered.connect(self.on_new_file)
        
        open_action = file_menu.addAction("Open")
        open_action.triggered.connect(self.on_open_file)
        
        save_action = file_menu.addAction("Save")
        save_action.triggered.connect(self.on_save_file)
        
        save_as_action = file_menu.addAction("Save As")
        save_as_action.triggered.connect(self.on_save_file_as)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Elements menu
        elements_menu = menubar.addMenu("Elements")
        add_element = elements_menu.addAction("Add Element")
        add_element.triggered.connect(self.open_elements_window)
        
        # Variables menu
        variables_menu = menubar.addMenu("Variables")
        show_vars = variables_menu.addAction("Show Variables")
        show_vars.triggered.connect(self.toggle_variable_frame)
        
        show_devs = variables_menu.addAction("Show Devices")
        show_devs.triggered.connect(self.toggle_devices_frame)
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        settings_action = settings_menu.addAction("Settings")
        settings_action.triggered.connect(self.open_settings_window)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        get_started = help_menu.addAction("Get Started")
        get_started.triggered.connect(lambda: self.open_help(0))
        
        examples = help_menu.addAction("Examples")
        examples.triggered.connect(lambda: self.open_help(1))
        
        faq = help_menu.addAction("FAQ")
        faq.triggered.connect(lambda: self.open_help(2))
        
        # Compile menu
        compile_menu = menubar.addMenu("Compile")
        compile_action = compile_menu.addAction("Compile Code")
        compile_action.triggered.connect(self.compile_code)
    
    def create_canvas_frame(self):
        """Create the main canvas area"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create canvas with new GraphicsView
        self.canvas = GridCanvas(grid_size=Utils.config['grid_size'])
        self.canvas.main_window = self
        
        main_layout.addWidget(self.canvas, stretch=1)
    
    def toggle_variable_frame(self):
        """Toggle variable panel visibility"""
        if not self.variable_frame_visible:
            if self.devices_frame_visible:
                self.hide_devices_frame()
            self.show_variable_frame()
        else:
            self.hide_variable_frame()
    
    def show_variable_frame(self):
        """Show the variable panel"""
        # Simplified - implement based on your needs
        print("Showing variable frame")
        self.variable_frame_visible = True
    
    def hide_variable_frame(self):
        """Hide the variable panel"""
        self.variable_frame_visible = False
    
    def toggle_devices_frame(self):
        """Toggle devices panel visibility"""
        if not self.devices_frame_visible:
            if self.variable_frame_visible:
                self.hide_variable_frame()
            self.show_devices_frame()
        else:
            self.hide_devices_frame()
    
    def show_devices_frame(self):
        """Show the devices panel"""
        print("Showing devices frame")
        self.devices_frame_visible = True
    
    def hide_devices_frame(self):
        """Hide the devices panel"""
        self.devices_frame_visible = False
    
    def open_elements_window(self):
        """Open the elements window"""
        elements_window = ElementsWindow.get_instance(self.canvas)
        elements_window.open()
    
    def open_settings_window(self):
        """Open the settings window"""
        device_settings_window = DeviceSettingsWindow.get_instance(self.canvas)
        device_settings_window.open()
    
    def open_help(self, which):
        """Open the help window"""
        HelpWindow = get_Help_Window()
        self.help_window_instance = HelpWindow.get_instance(self.canvas, which)
        self.help_window_instance.open()
    
    def compile_code(self):
        """Compile the visual code"""
        try:
            print("Starting code compilation...")
            self.code_compiler.compile()
            print("Code compiled successfully")
        except Exception as e:
            print(f"Compilation error: {e}")
    
    def create_save_shortcut(self):
        """Create Ctrl+S keyboard shortcut"""
        from PyQt6.QtGui import QKeySequence, QShortcut
        save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        save_shortcut.activated.connect(self.on_save_file)
    
    def setup_auto_save_timer(self):
        """Setup auto-save timer"""
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_project)
        self.auto_save_timer.start(300000)  # 5 minutes
    
    def auto_save_project(self):
        """Auto-save the project"""
        name = Utils.project_data.metadata.get('name', 'Untitled')
        try:
            if FileManager.save_project(name, is_autosave=True):
                print(f"✓ Auto-saved '{name}'")
        except Exception as e:
            print(f"✗ Auto-save error: {e}")
    
    def on_save_file(self):
        """Save current project"""
        name = Utils.project_data.metadata.get('name', 'Untitled')
        if name == 'Untitled':
            self.on_save_file_as()
            return
        
        try:
            if FileManager.save_project(name):
                print(f"✓ Project '{name}' saved")
        except Exception as e:
            print(f"Error saving: {e}")
    
    def on_save_file_as(self):
        """Save with new name"""
        text, ok = QInputDialog.getText(
            self, "Save Project As",
            "Enter project name:",
            QLineEdit.EchoMode.Normal,
            Utils.project_data.metadata.get('name', '')
        )
        
        if ok and text:
            Utils.project_data.metadata['name'] = text
            try:
                if FileManager.save_project(text):
                    print(f"✓ Saved as '{text}'")
            except Exception as e:
                print(f"Error: {e}")
    
    def on_open_file(self):
        """Open saved project"""
        projects = FileManager.list_projects()
        if not projects:
            QMessageBox.information(self, "No Projects", "No saved projects found")
            return
        
        items = [p['name'] for p in projects]
        item, ok = QInputDialog.getItem(
            self, "Open Project",
            "Select project:", items, 0, False
        )
        
        if ok and item:
            try:
                if FileManager.load_project(item):
                    self.rebuild_from_data()
                    print(f"✓ Loaded '{item}'")
            except Exception as e:
                print(f"Error loading: {e}")
    
    def on_new_file(self):
        """Create new project"""
        self.canvas.clear_canvas()
        FileManager.new_project()
        QCoreApplication.processEvents()
    
    def rebuild_from_data(self):
        """Rebuild UI from saved data"""
        print("Rebuilding UI from saved data...")
        # Load blocks
        for block_id, block_data in Utils.project_data.blocks.items():
            block_type = block_data.get('type')
            x = block_data.get('x', 0)
            y = block_data.get('y', 0)
            
            self.canvas.add_block(block_type, x, y, block_id)
        
        # Load paths
        for path_id, path_data in Utils.project_data.paths.items():
            from_id = path_data.get('from')
            to_id = path_data.get('to')
            
            if from_id in Utils.top_infos and to_id in Utils.top_infos:
                from_block = Utils.top_infos[from_id]['widget']
                to_block = Utils.top_infos[to_id]['widget']
                self.canvas.add_path(from_block, to_block, path_id)
    
    def closeEvent(self, event):
        """Handle window close"""
        reply = QMessageBox.question(
            self, "Close",
            "Save before closing?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.on_save_file()
        
        event.accept()
