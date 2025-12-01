from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QMenuBar, QMenu, QPushButton, QLabel,
                             QFrame, QScrollArea, QLineEdit, QComboBox)
from PyQt6.QtCore import Qt, QPoint, QRect, QSize, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPalette, QMouseEvent
import sys
import Utils
from Path_manager_pyqt import PathManager
from Elements_window_pyqt import ElementsWindow
import code_compiler
from spawn_elements_pyqt import spawning_elements, Elements_events

class GridCanvas(QWidget):
    """Canvas widget with grid and draggable widgets"""
    
    def __init__(self, parent=None, grid_size=25):
        super().__init__(parent)
        self.grid_size = grid_size
        self.dragged_widget = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.spawner = spawning_elements(self)
        self.path_manager = PathManager(self)
        self.elements_events = Elements_events(self)
        # Setup widget
        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Style
        self.setStyleSheet("""
            GridCanvas {
                background-color: #2B2B2B;
            }
        """)
        
        # Path manager

        
    def paintEvent(self, event):
        """Draw grid lines and connection paths"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw grid
        pen = QPen(QColor("#3A3A3A"))
        pen.setWidth(1)
        painter.setPen(pen)
        
        width = self.width()
        height = self.height()
        
        # Vertical lines
        x = 0
        while x < width:
            painter.drawLine(x, 0, x, height)
            x += self.grid_size
        
        # Horizontal lines
        y = 0
        while y < height:
            painter.drawLine(0, y, width, y)
            y += self.grid_size
        
        # **Draw all connection paths**
        self.path_manager.draw_all_paths(painter)
        
        # **Draw preview path while connecting**
        if self.path_manager.preview_points:
            self.path_manager.draw_path(
                painter,
                self.path_manager.preview_points,
                QColor(100, 149, 237),  # Light blue
                width=2,
                dashed=True
            )
    
    """def mouseMoveEvent(self, event):
        Handle mouse movement - update connection preview
        super().mouseMoveEvent(event)
        
        # Update connection preview if creating a connection
        if self.path_manager.start_node:
            self.path_manager.update_preview_path(event.pos())
            self.update()"""
    
    def mousePressEvent(self, event):
        """Debug: Track if canvas gets mouse press"""
        #print("✓ GridCanvas.mousePressEvent fired!")
        #print(f"  Position: {event.pos()}")
        # Call the existing one if you had it, or let it propagate
        print(f"Canvas mousePressEvent at {event.pos()}")
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        #print(f"Canvas.mouseMoveEvent fired at {event.pos()}")
        #print(f"start_node is: {self.path_manager.start_node}")
        
        if self.path_manager.start_node:
            #print("Updating preview from CANVAS mouseMoveEvent")
            self.path_manager.update_preview_path(event.pos())
            self.update()
    
    def keyPressEvent(self, event):
        #print(f"Spawner ID in Canvas: {id(self.spawner)}")
        #print(f"Spawner in Canvas has placing_active: {self.spawner.placing_active if self.spawner else 'None'}")
        #print(f"Element placed: {self.spawner.element_placed if self.spawner else 'None'}")

        if self.spawner and self.spawner.element_placed:
            #print(f"Key pressed: {event.key()}")
            #print(f"Element placed before: {self.spawner.element_placed}")
            
            if event.key() in [Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Enter]:
                self.spawner.stop_placing(self)
                event.accept()
            else:
                event.ignore()
        elif self.path_manager.start_node:
            #print(f"Key pressed during path creation: {event.key()}")
            if event.key() == Qt.Key.Key_Escape:
                self.path_manager.cancel_connection()
                self.update()
                event.accept()
            else:
                event.ignore()
        else:
            super().keyPressEvent(event)

    
    def snap_to_grid(self, x, y, widget=None, during_drag=False):
        """Snap coordinates to nearest grid intersection"""
        if widget and not during_drag:
            height = widget.height()
            grid_height = round(height / self.grid_size) * self.grid_size
            
            if height > grid_height:
                grid_height += self.grid_size
            elif height < self.grid_size:
                grid_height = self.grid_size
                
            if height == self.grid_size:
                height_offset = grid_height / 2
            else:
                height_offset = (grid_height - height) / 2
        else:
            height_offset = 0
            
        snapped_x = int(round(x / self.grid_size) * self.grid_size)
        snapped_y = int(round(y / self.grid_size) * self.grid_size + height_offset)
        
        return snapped_x, snapped_y
    
    def add_draggable_widget(self, widget):
        """Make a widget draggable on the canvas"""
        widget.setParent(self)
        widget.show()
        widget.raise_()
        
        # Store original mouse press handler
        original_press = widget.mousePressEvent
        original_move = widget.mouseMoveEvent
        original_release = widget.mouseReleaseEvent
        
        def on_press(event):
            if event.button() == Qt.MouseButton.LeftButton:
                # ← NEW: Check if on circle BEFORE setting dragged_widget
                circle_type = self.elements_events.check_click_on_circle(widget, event.pos())
                if not circle_type:  # Only set dragged_widget if NOT on circle
                    self.on_canvas_click(event, widget)
            
            original_press(event)
        
        def on_move(event):
            if event.buttons() & Qt.MouseButton.LeftButton:
                self.on_canvas_drag(event, widget)
            
            original_move(event)
                
        def on_release(event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.on_canvas_release(event, widget)
            original_release(event)
        
        widget.mousePressEvent = on_press
        widget.mouseMoveEvent = on_move
        widget.mouseReleaseEvent = on_release
    
    def on_canvas_click(self, event, widget):
        #print(f"Pressed {type(self).__name__}")
        """Handle mouse click on widget"""
        for block_id, widget_info in Utils.top_infos.items():
            if widget_info['widget'] is widget:
                self.offset_x = event.pos().x()
                self.offset_y = event.pos().y()
                self.dragged_widget = widget_info
                self.is_dragging = True
                widget.raise_()
                #print(f"Click {self.mousePressEvent}")
                break
    
    def on_canvas_drag(self, event, widget):
        """Handle dragging of widgets"""
        if self.dragged_widget and self.dragged_widget['widget'] is widget:
            global_pos = widget.mapToGlobal(event.pos())
            canvas_pos = self.mapFromGlobal(global_pos)
            
            new_x = canvas_pos.x() - self.offset_x
            new_y = canvas_pos.y() - self.offset_y
            
            widget.move(new_x, new_y)
            self.dragged_widget['x'] = new_x
            self.dragged_widget['y'] = new_y
            
            # Update paths
            self.path_manager.update_paths_for_widget(widget)
            self.update()
            #print(f"Drag {self.mousePressEvent}")
    
    def on_canvas_release(self, event, widget):
        """Handle mouse release - snap to grid"""
        if self.dragged_widget and self.dragged_widget['widget'] is widget:
            snapped_x, snapped_y = self.snap_to_grid(
                self.dragged_widget['x'], 
                self.dragged_widget['y'], 
                widget, 
                during_drag=False
            )
            
            widget.move(snapped_x, snapped_y)
            self.dragged_widget['x'] = snapped_x
            self.dragged_widget['y'] = snapped_y
            self.dragged_widget = None
            self.is_dragging = False
            self.update()
            self.path_manager.update_paths_for_widget(widget)
            #print(f"Release {self.mousePressEvent}")


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visual Programming Interface")
        self.resize(1200, 800)
        
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
        
        self.variable_frame = None
        self.variable_frame_visible = False
        self.variable_row_count = 1
        self.blockIDs = {}
        
        self.create_menu_bar()
        self.create_canvas_frame()
    
    def mousePressEvent(self, event):
        """Debug: Track if main window gets mouse press"""
        #print("⚠ MainWindow.mousePressEvent fired!")
        super().mousePressEvent(event)
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        print(f"Menubar Height: {menubar.height()}")
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = file_menu.addAction("New")
        new_action.triggered.connect(self.on_new_file)
        
        open_action = file_menu.addAction("Open")
        open_action.triggered.connect(self.on_open_file)
        
        save_action = file_menu.addAction("Save")
        save_action.triggered.connect(self.on_save_file)
        
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
        
        # Compile menu
        compile_menu = menubar.addMenu("Compile")
        
        compile_action = compile_menu.addAction("Compile Code")
        compile_action.triggered.connect(self.compile_code)
    
    def create_canvas_frame(self):
        """Create the main canvas area"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Canvas
        self.canvas = GridCanvas(grid_size=Utils.config['grid_size'])
        self.canvas.main_window = self
        self.canvas.spawner = None
        main_layout.addWidget(self.canvas, stretch=1)
    
    def toggle_variable_frame(self):
        """Toggle the variable panel visibility"""
        if not self.variable_frame_visible:
            self.show_variable_frame()
        else:
            self.hide_variable_frame()
    
    def show_variable_frame(self):
        """Show the variable panel"""
        if self.variable_frame is None:
            self.variable_frame = QFrame()
            self.variable_frame.setMinimumWidth(250)
            self.variable_frame.setMaximumWidth(300)
            self.variable_frame.setStyleSheet("""
                QFrame {
                    background-color: #2B2B2B;
                    border-left: 1px solid #3A3A3A;
                }
            """)
            
            
            main_layout = QVBoxLayout(self.variable_frame)
            
            
            header = QWidget()
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)

            title = QLabel("Variables")
            hide_btn = QPushButton("×")
            hide_btn.setFixedWidth(24)
            hide_btn.clicked.connect(self.hide_variable_frame)

            header_layout.addWidget(title)
            header_layout.addStretch()
            header_layout.addWidget(hide_btn)
            main_layout.addWidget(header)
            
            # Add button
            add_btn = QPushButton("Add Variable")
            add_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1F538D;
                    color: #FFFFFF;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #2667B3;
                }
            """)
            add_btn.clicked.connect(self.add_variable_row)
            main_layout.addWidget(add_btn)
            
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)

            # Content widget inside scroll area
            self.var_content_widget = QWidget()
            self.var_content_layout = QVBoxLayout(self.var_content_widget)
            self.var_content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            # Add stretch at end if you want padding at the bottom:
            self.var_content_layout.addStretch()

            scroll_area.setWidget(self.var_content_widget)
            main_layout.addWidget(scroll_area)
                        # Add to main layout
            central_widget = self.centralWidget()
            if central_widget:
                main_layout = central_widget.layout()
                if main_layout:
                    main_layout.addWidget(self.variable_frame)
        
        self.variable_frame.show()
        self.variable_frame_visible = True
    
    def hide_variable_frame(self):
        """Hide the variable panel"""
        if self.variable_frame:
            self.variable_frame.hide()
        self.variable_frame_visible = False
    
    def remove_variable_row(self, row_widget, var_id):
        """Remove a variable row"""
        
        del Utils.var_items[var_id]
            
        if var_id in Utils.variables:
            #print(f"Deleting {var_id}")
            del Utils.variables[var_id]
            for imput, var_ids in Utils.vars_same.items():
                if var_id in var_ids:
                    var_ids.remove(var_id)
                    #print(f"Vars_same {var_ids}")
        
        for imput2, var in Utils.vars_same.items():
            #print(f"Var {var}, len var {len(var)}")
            if len(var) <= 1:
                for var_id in var:
                    Utils.variables[var_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
            
        self.refresh_all_if_blocks()
        
        panel_layout = self.variable_frame.layout()
        panel_layout.removeWidget(row_widget)
        
        row_widget.setParent(None)
        row_widget.deleteLater()
        
        self.variable_row_count -= 1
        
        #print(f"Deleted variable: {var_id}")
    
    def name_changed(self, text, var_id, name_imput):
        Utils.variables[var_id]['name'] = text

        if var_id in Utils.var_items:
            Utils.var_items[var_id] = text
        else:
            Utils.var_items.setdefault(var_id, text)
        # Step 1: Group all var_ids by their name value
        Utils.vars_same.clear()
        Utils.variables[var_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
        for v_id, v_info in Utils.variables.items():
            name = v_info['name_imput'].text().strip()
            if name:
                Utils.vars_same.setdefault(name, []).append(v_id)
        
        # Step 2: Color red if duplicate
        for name, id_list in Utils.vars_same.items():
            #print(id_list)
            border_col = "border-color: #ff0000;" if len(id_list) > 1 else "border-color: #3F3F3F;"
            for v_id in id_list:
                Utils.variables[v_id]['name_imput'].setStyleSheet(border_col)
        
        self.refresh_all_if_blocks()
    
    def refresh_all_if_blocks(self):
        """Find all If blocks on canvas and refresh their dropdowns"""
        for block_id, block_info in Utils.top_infos.items():
            widget = block_info['widget']
            
            # Check if it's an If block with the refresh method
            if hasattr(widget, 'refresh_if_dropdown'):
                widget.refresh_if_dropdown()
                #print(f"Refreshed If block dropdown for {block_id}")
    
    def type_changed(self, imput):
        #print(f"Updating variable {imput}")
        
        if self.var_id in Utils.variables:
            Utils.variables[self.var_id]['type_imput'] = imput
            #print(f"Type {self.var_id} value changed to: {imput}")
    
    def value_changed(self, imput):
        #print(f"Updating variable {imput}")
        
        if self.var_id in Utils.variables:
            Utils.variables[self.var_id]['value_imput'] = imput
            #print(f"Value {self.var_id} value changed to: {imput}")
    
    def add_variable_row(self):
        """Add a new variable row"""
        var_id = f"var_{self.variable_row_count}"
        self.var_id = var_id
        #print(f"Adding variable row {self.var_id}")
        
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(5, 5, 5, 5)
 
        name_imput = QLineEdit()
        name_imput.setPlaceholderText("Variable Name")
        
        name_imput.textChanged.connect(lambda text, v_id=var_id, n_i=name_imput: self.name_changed(text, v_id, n_i))
        
        type_input = QComboBox()
        type_input.addItems(["Int", "Float", "String", "Boo"])
        
        type_input.currentTextChanged.connect(self.type_changed)
        
        value_input = QLineEdit()
        value_input.setPlaceholderText("Initial Value")
        
        value_input.textChanged.connect(self.value_changed)
        
        delete_btn = QPushButton("×")
        delete_btn.setFixedWidth(30)
        
        row_layout.addWidget(name_imput)
        row_layout.addWidget(type_input)
        row_layout.addWidget(value_input)
        row_layout.addWidget(delete_btn)
        
        delete_btn.clicked.connect(lambda _, v_id=var_id, rw=row_widget: self.remove_variable_row(rw, v_id))
        
        Utils.variables[var_id] = {
            'name': '',
            'type': 'int',
            'value': '',
            'PIN': None,
            'widget': row_widget,
            'name_imput': name_imput,
            'type_input': type_input,
            'value_input': value_input
        } 
        
        panel_layout = self.variable_frame.layout()
        self.var_content_layout.insertWidget(self.var_content_layout.count() - 1, row_widget)
        
        self.variable_row_count += 1
        
        #print(f"Added variable: {self.var_id}")
        
    def open_elements_window(self):
        """Open the elements window"""
        elements_window = ElementsWindow.get_instance(self.canvas)
        elements_window.open()
    
    def block_management(self, block_id, window):
        """Track block windows"""
        self.blockIDs[block_id] = window
    
    def compile_code(self):
        """Compile the visual code"""
        try:
            code_compiler.Codecompiler.Start()
            #print("Code compiled successfully")
        except Exception as e:
            #print(f"Compilation error: {e}")
            pass
    
    # Menu actions
    def on_new_file(self):
        """Create new file"""
        #print("New file")
        Utils.top_infos.clear()
        Utils.paths.clear()
        Utils.variables.clear()
        self.canvas.update()
    
    def on_open_file(self):
        """Open file"""
        #print("Open file")
        # TODO: Implement file opening
    
    def on_save_file(self):
        """Save file"""
        #print("Save file")
        # TODO: Implement file saving


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(31, 31, 31))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(43, 43, 43))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(58, 58, 58))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(43, 43, 43))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(31, 83, 141))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(31, 83, 141))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
