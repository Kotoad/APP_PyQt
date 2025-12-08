from Imports import (
    sys, QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QPushButton, QLabel, QFrame, QScrollArea,
    QLineEdit, QComboBox, QDialog, QPainter, QPen, QColor, QBrush,
    QPalette, QMouseEvent, QRegularExpression, QRegularExpressionValidator,
    QTimer, QMessageBox, QInputDialog, QFileDialog, QFont, Qt, QPoint,
    QRect, QSize, pyqtSignal, AppSettings, ProjectData, QCoreApplication
)
from Imports import (
    get_code_compiler, get_spawn_elements, get_device_settings_window,
    get_file_manager, get_path_manager, get_Elements_Window, get_utils,
    get_Help_Window
)
Utils = get_utils()
Code_Compiler = get_code_compiler()
spawning_elements = get_spawn_elements()[0]
element_events = get_spawn_elements()[1]
DeviceSettingsWindow = get_device_settings_window()
FileManager = get_file_manager()
PathManager = get_path_manager()
ElementsWindow = get_Elements_Window()
#MARK: - GridCanvas
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
        self.elements_events = element_events(self)
        self.file_manager = FileManager()
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
    
    def mousePressEvent(self, event):
        """Debug: Track if canvas gets mouse press"""
        print("✓ GridCanvas.mousePressEvent fired!")
        print(f"  Position: {event.pos()}")
        # Call the existing one if you had it, or let it propagate
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

    #MARK: - Dragging and Snapping    
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
                    event.accept()
            
            original_press(event)
        
        def on_move(event):
            if event.buttons() & Qt.MouseButton.LeftButton:
                self.on_canvas_drag(event, widget)
                event.accept()
            
            original_move(event)
                
        def on_release(event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.on_canvas_release(event, widget)
            original_release(event)
        
        widget.mousePressEvent = on_press
        widget.mouseMoveEvent = on_move
        widget.mouseReleaseEvent = on_release
    
    def on_canvas_click(self, event, widget):
        print(f"Pressed {type(self).__name__}")
        """Handle mouse click on widget"""
        for block_id, widget_info in Utils.top_infos.items():
            if widget_info['widget'] is widget:
                self.offset_x = event.pos().x()
                self.offset_y = event.pos().y()
                self.dragged_widget = widget_info
                self.is_dragging = True
                widget.raise_()
                print(f"Click {self.mousePressEvent}")
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
            print(f"Release {self.mousePressEvent}")

#MARK: - MainWindow
class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visual Programming Interface")
        self.resize(1200, 800)
        self.code_compiler = Code_Compiler()
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
    
    def mousePressEvent(self, event):
        """Debug: Track if main window gets mouse press"""
        print("⚠ MainWindow.mousePressEvent fired!")
        super().mousePressEvent(event)
    #MARK: - UI Creation Methods
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
        
        show_divs = variables_menu.addAction("Show Devices")
        show_divs.triggered.connect(self.toggle_devices_frame)
        
        
        settings_menu = menubar.addMenu("Settings")
        settings_menu_action = settings_menu.addAction("Settings")
        settings_menu_action.triggered.connect(self.open_settings_window)
        
        Help_menu = menubar.addMenu("Help")
        
        Get_stared = Help_menu.addAction("Get Started")
        Get_stared.triggered.connect(lambda: self.open_help(0))
        
        examples = Help_menu.addAction("Examples")
        examples.triggered.connect(lambda: self.open_help(1))
        
        FAQ = Help_menu.addAction("FAQ")
        FAQ.triggered.connect(lambda: self.open_help(2))
        
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
        #self.canvas.spawner = None
        main_layout.addWidget(self.canvas, stretch=1)
    #MARK: - Variable Panel Methods
    def toggle_variable_frame(self):
        """Toggle the variable panel visibility"""
        if not self.variable_frame_visible:
            if self.devices_frame_visible:
                self.hide_devices_frame()
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
    
    def add_variable_row(self):
        """Add a new variable row"""
        var_id = f"var_{self.variable_row_count}"
        self.var_id = var_id
        #print(f"Adding variable row {self.var_id}")
        
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(5, 5, 5, 5)
 
        name_imput = QLineEdit()
        name_imput.setPlaceholderText("Name")
        
        name_imput.textChanged.connect(lambda text, v_id=var_id, t="Variable": self.name_changed(text, v_id, t))
        
        type_input = QComboBox()
        type_input.addItems(["Int", "Float", "String", "Bool"])
        
        type_input.currentTextChanged.connect(lambda  text, t="Variable": self.type_changed(text, t))
        
        self.value_var_input = QLineEdit()
        self.value_var_input.setPlaceholderText("Initial Value")
        regex = QRegularExpression(r"^\d*$")
        validator = QRegularExpressionValidator(regex, self)
        self.value_var_input.setValidator(validator)
        self.value_var_input.textChanged.connect(lambda text, t="Variable": self.value_changed(text, t))
        
        delete_btn = QPushButton("×")
        delete_btn.setFixedWidth(30)
        
        row_layout.addWidget(name_imput)
        row_layout.addWidget(type_input)
        row_layout.addWidget(self.value_var_input)
        row_layout.addWidget(delete_btn)
        
        delete_btn.clicked.connect(lambda _, v_id=var_id, rw=row_widget, t="Variable": self.remove_row(rw, v_id, t))
        
        Utils.variables[var_id] = {
            'name': '',
            'type': 'Out',
            'value': '',
            'widget': row_widget,
            'name_imput': name_imput,
            'type_input': type_input,
            'value_input': self.value_var_input
        } 
        
        panel_layout = self.variable_frame.layout()
        self.var_content_layout.insertWidget(self.var_content_layout.count() - 1, row_widget)
        
        self.variable_row_count += 1
        
        #print(f"Added variable: {self.var_id}")
    
    def Clear_All_Variables(self):
        print("Clearing all variables")
        
        # Get a SNAPSHOT of variable IDs BEFORE modifying anything
        var_ids_to_remove = list(Utils.variables.keys())
        print(f"Variable IDs to remove: {var_ids_to_remove}")
        
        # Now remove them
        for varid in var_ids_to_remove:
            if varid in Utils.variables:
                print(f"Removing varid: {varid}")
                rowwidget = Utils.variables[varid]['widget']
                self.remove_row(rowwidget, varid, 'Variable')
            else:
                print(f"WARNING: varid {varid} not found in Utils.variables")

    #MARK: - Devices Panel Methods
    def toggle_devices_frame(self):
        """Toggle the devices panel visibility"""
        if not self.devices_frame_visible:
            if self.variable_frame_visible:
                self.hide_variable_frame()
            self.show_devices_frame()
        else:
            self.hide_devices_frame()
        
    def show_devices_frame(self):
        """Show the devices panel"""
        if self.Devices_frame is None:
            self.Devices_frame = QFrame()
            self.Devices_frame.setMinimumWidth(250)
            self.Devices_frame.setMaximumWidth(300)
            self.Devices_frame.setStyleSheet("""
                QFrame {
                    background-color: #2B2B2B;
                    border-left: 1px solid #3A3A3A;
                }
            """)
            
            main_layout = QVBoxLayout(self.Devices_frame)
            
            header = QWidget()
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)

            title = QLabel("Devices")
            hide_btn = QPushButton("×")
            hide_btn.setFixedWidth(24)
            hide_btn.clicked.connect(self.hide_devices_frame)

            header_layout.addWidget(title)
            header_layout.addStretch()
            header_layout.addWidget(hide_btn)
            main_layout.addWidget(header)
            
            # Add button
            add_btn = QPushButton("Add Device")
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
            add_btn.clicked.connect(self.add_device_row)
            main_layout.addWidget(add_btn)
            
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)

            # Content widget inside scroll area
            self.dev_content_widget = QWidget()
            self.dev_content_layout = QVBoxLayout(self.dev_content_widget)
            self.dev_content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            # Add stretch at end if you want padding at the bottom:
            self.dev_content_layout.addStretch()
            scroll_area.setWidget(self.dev_content_widget)
            main_layout.addWidget(scroll_area)
                        # Add to main layout
            central_widget = self.centralWidget()
            if central_widget:
                main_layout = central_widget.layout()
                if main_layout:
                    main_layout.addWidget(self.Devices_frame)
        
        self.Devices_frame.show()
        self.devices_frame_visible = True
    
    def hide_devices_frame(self):
        """Hide the devices panel"""
        if self.Devices_frame:
            self.Devices_frame.hide()
        self.devices_frame_visible = False
    
    def add_device_row(self):
        """Add a new device row"""
        device_id = f"device_{self.devices_row_count}"
        self.device_id = device_id
        #print(f"Adding device row {self.device_id}")
        
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(5, 5, 5, 5)
 
        name_imput = QLineEdit()
        name_imput.setPlaceholderText("Name")
        
        name_imput.textChanged.connect(lambda text, d_id=device_id, t="Device": self.name_changed(text, d_id, t))
        
        type_input = QComboBox()
        type_input.addItems(["Output", "Input", "PWM"])
        
        type_input.currentTextChanged.connect(lambda text, t="Device": self.type_changed(text, t))
        
        self.value_dev_input = QLineEdit()
        self.value_dev_input.setPlaceholderText("PIN")
        regex = QRegularExpression(r"^\d*$")
        validator = QRegularExpressionValidator(regex, self)
        self.value_dev_input.setValidator(validator)
        self.value_dev_input.textChanged.connect(lambda text, t="Device": self.value_changed(text, t))
        
        delete_btn = QPushButton("×")
        delete_btn.setFixedWidth(30)
        
        row_layout.addWidget(name_imput)
        row_layout.addWidget(type_input)
        row_layout.addWidget(self.value_dev_input)
        row_layout.addWidget(delete_btn)
        
        delete_btn.clicked.connect(lambda _, d_id=device_id, rw=row_widget, t="Device": self.remove_row(rw, d_id, t))
        
        Utils.devices[device_id] = {
            'name': '',
            'type': 'Output',
            'PIN': None,
            'widget': row_widget,
            'name_imput': name_imput,
            'type_input': type_input,
            'value_input': self.value_dev_input
        } 
        
        panel_layout = self.Devices_frame.layout()
        self.dev_content_layout.insertWidget(self.dev_content_layout.count() - 1, row_widget)
        
        self.devices_row_count += 1

    def Clear_All_Devices(self):
        print("Clearing all devices")
        
        # Get a SNAPSHOT of device IDs BEFORE modifying anything
        device_ids_to_remove = list(Utils.devices.keys())
        print(f"Device IDs to remove: {device_ids_to_remove}")
        
        # Now remove them
        for device_id in device_ids_to_remove:
            if device_id in Utils.devices:
                print(f"Removing device_id: {device_id}")
                rowwidget = Utils.devices[device_id]['widget']
                self.remove_row(rowwidget, device_id, 'Device')
            else:
                print(f"WARNING: device_id {device_id} not found in Utils.devices")
    
    #MARK: - Common Methods
    def remove_row(self, row_widget, var_id, type):
        """Remove a variable row"""
        print(f"Removing row {var_id} of type {type}")
        if type == "Variable":
            if var_id in Utils.var_items:
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
                
            self.refresh_all_blocks()
            
            panel_layout = self.variable_frame.layout()
            panel_layout.removeWidget(row_widget)
            
            row_widget.setParent(None)
            row_widget.deleteLater()
            
            self.variable_row_count -= 1
        elif type == "Device":
            if var_id in Utils.dev_items:
                del Utils.dev_items[var_id]
                
            if var_id in Utils.devices:
                #print(f"Deleting {var_id}")
                del Utils.devices[var_id]
                for imput, dev_ids in Utils.devs_same.items():
                    if var_id in dev_ids:
                        dev_ids.remove(var_id)
                        #print(f"Devs_same {dev_ids}")
            
            for imput2, dev in Utils.devs_same.items():
                #print(f"Dev {dev}, len dev {len(dev)}")
                if len(dev) <= 1:
                    for dev_id in dev:
                        Utils.devices[dev_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
                
            self.refresh_all_blocks()
            
            panel_layout = self.Devices_frame.layout()
            panel_layout.removeWidget(row_widget)
            
            row_widget.setParent(None)
            row_widget.deleteLater()
            
            self.devices_row_count -= 1
        #print(f"Deleted variable: {var_id}")
    
    def name_changed(self, text, var_id, type):
        if type == "Variable":
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
            print("Utils.variables:", Utils.variables)
            self.refresh_all_blocks()
        
        elif type == "Device":
            Utils.devices[var_id]['name'] = text

            if var_id in Utils.dev_items:
                Utils.dev_items[var_id] = text
            else:
                Utils.dev_items.setdefault(var_id, text)
            print(f"dev_items: {Utils.dev_items}")
            # Step 1: Group all dev_ids by their name value
            Utils.devs_same.clear()
            Utils.devices[var_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
            for d_id, d_info in Utils.devices.items():
                name = d_info['name_imput'].text().strip()
                if name:
                    Utils.devs_same.setdefault(name, []).append(d_id)
            
            # Step 2: Color red if duplicate
            for name, id_list in Utils.devs_same.items():
                #print(id_list)
                border_col = "border-color: #ff0000;" if len(id_list) > 1 else "border-color: #3F3F3F;"
                for d_id in id_list:
                    Utils.devices[d_id]['name_imput'].setStyleSheet(border_col)
            print("Calling refresh_all_blocks from name_changed")
            print(f"Utils.devices: {Utils.devices}")
            self.refresh_all_blocks()
        
    
    def refresh_all_blocks(self):
        """Find all If blocks on canvas and refresh their dropdowns"""
        print("Refreshing all blocks' dropdowns")
        print(f"Total blocks to check: {len(Utils.top_infos)}")
        print(f"Utils.top_infos: {Utils.top_infos}")
        print(f"Variables dict: {Utils.variables}")
        print(f"Devices dict: {Utils.devices}")
        print(f"Variables: {Utils.var_items}")
        print(f"Devices: {Utils.dev_items}")
        for block_id, block_info in Utils.top_infos.items():
            widget = block_info['widget']
            print(f"Refreshing block {block_id} of type {block_info['type']}")
            # Check if it's an If block with the refresh method
            if hasattr(widget, 'refresh_dropdown'):
                print(f"Found block {block_id}, refreshing dropdown")
                widget.refresh_dropdown()
                #print(f"Refreshed If block dropdown for {block_id}")
    
    def type_changed(self, imput, type):
        #print(f"Updating variable {imput}")
        if type == "Variable":
            if self.var_id in Utils.variables:
                Utils.variables[self.var_id]['type'] = imput
                print(f"Type {self.var_id} value changed to: {imput}")
        elif type == "Device":
            if self.device_id in Utils.devices:
                Utils.devices[self.device_id]['type'] = imput
                print(f"Type {self.device_id} value changed to: {imput}")
    
    def value_changed(self, imput, type):
        #print(f"Updating variable {imput}")
        
        if type == "Variable":
            try:
                value = len(imput)
                
                if value > 4:
                    self.value_var_input.blockSignals(True)
                    imput = imput[:4]
                    self.value_var_input.setText(imput)
                    self.value_var_input.blockSignals(False)
                
                elif value < 0:
                    self.value_var_input.blockSignals(True)
                    self.value_var_input.setText("0")
                    self.value_var_input.blockSignals(False)
            except ValueError:
                    # Text is empty or can't convert (shouldn't happen with regex)
                    pass
            if self.var_id in Utils.variables:
                Utils.variables[self.var_id]['value'] = imput
                print(f"Value {self.var_id} value changed to: {imput}")
        elif type == "Device":
            try:
                value = len(imput)
                
                if value > 4:
                    self.value_dev_input.blockSignals(True)
                    imput = imput[:4]
                    self.value_dev_input.setText(imput)
                    self.value_dev_input.blockSignals(False)
                
                elif value < 0:
                    self.value_dev_input.blockSignals(True)
                    self.value_dev_input.setText("0")
                    self.value_dev_input.blockSignals(False)
            except ValueError:
                    # Text is empty or can't convert (shouldn't happen with regex)
                    pass
            if self.device_id in Utils.devices:
                Utils.devices[self.device_id]['PIN'] = imput
                print(f"device {self.device_id} PIN changed to: {imput}")   
    #MARK: - Other Methods
    def open_elements_window(self):
        """Open the elements window"""
        elements_window = ElementsWindow.get_instance(self.canvas)
        elements_window.open()
    
    def open_settings_window(self):
        """Open the device settings window"""
        device_settings_window = DeviceSettingsWindow.get_instance(self.canvas)
        device_settings_window.open()
    
    def open_help(self, which):
        """Open the help window"""
        HelpWindow = get_Help_Window()
        self.help_window_instance = HelpWindow.get_instance(self.canvas, which)
        self.help_window_instance.open()
    
    
    def block_management(self, block_id, window):
        """Track block windows"""
        self.blockIDs[block_id] = window
    
    def compile_code(self):
        """Compile the visual code"""
        try:
            print("Starting code compilation...")
            self.code_compiler.compile()
            print("Code compiled successfully")
        except Exception as e:
            print(f"Compilation error: {e}")
            pass
    
    # Menu actions
    def on_save_file(self):
        """Save current project"""
        
        name, ok = QInputDialog.getText(self, "Save Project", "Project name:")
        if ok and name:
            if FileManager.save_project(name):
                print(f"✓ Project '{name}' saved")

    def on_open_file(self):
        """Open saved project"""
        
        projects = FileManager.list_projects()
        if not projects:
            QMessageBox.information(self, "No Projects", "No saved projects found")
            return
        
        items = [p['name'] for p in projects]
        item, ok = QInputDialog.getItem(self, "Open Project", 
            "Select project:", items, 0, False)
        
        if ok and item:
            if FileManager.load_project(item):
                self.rebuild_from_data()
                print(f"✓ Project '{item}' loaded")

    def on_new_file(self):
        """Create new project"""
        self.Clear_All_Variables()
        self.Clear_All_Devices()
        self.canvas.path_manager.clear_all_paths()
        widget_ids_to_remove = list(Utils.top_infos.keys())
        
        for block_id in widget_ids_to_remove:
            if block_id in Utils.top_infos:
                widget = Utils.top_infos[block_id]['widget']
                widget.setParent(None)  # Remove from parent
                widget.deleteLater()     # Schedule for deletion
        
        FileManager.new_project()
        
        QCoreApplication.processEvents()
        
        self.canvas.update()
    
    def closeEvent(self, event):
        """Close all child windows before closing main window"""
        # Close Help window if it exists
        if self.help_window_instance is not None and self.help_window_instance.isVisible():
            self.help_window_instance.close()
        
        # Close Elements window if it exists
        try:
            elements_window = ElementsWindow.get_instance(self.canvas)
            if elements_window.isVisible():
                elements_window.close()
        except:
            pass
        
        # Close Device Settings window if it exists
        try:
            device_settings_window = DeviceSettingsWindow.get_instance(self.canvas)
            if device_settings_window.isVisible():
                device_settings_window.close()
        except:
            pass
        
        # Accept the close event
        event.accept()

    #MARK: - Rebuild UI from Saved Data
    def rebuild_from_data(self):
        """
        Reconstruct the entire UI from Utils.project_data
        
        Called after loading a project file.
        
        Rebuilds:
        1. All blocks on canvas with their positions
        2. All connections between blocks
        3. Variables in the side panel
        4. Devices in the side panel
        """
        print("Starting rebuild from saved data...")
        
        self._rebuild_settings()
        
        # Rebuild variable panel
        self._rebuild_variables_panel()
        
        # Rebuild devices panel
        self._rebuild_devices_panel()
        
        # Clear canvas and rebuild blocks
        self._rebuild_blocks()
        
        # Rebuild connections
        self._rebuild_connections()
        
        
        
        print("✓ Project rebuild complete")

    def _rebuild_settings(self):
        """Rebuild settings from project_data"""
        print(f"Rebuilding {len(Utils.project_data.settings)} settings...")
        print(f" RPi Model: {Utils.app_settings.rpi_model} (Index: {Utils.app_settings.rpi_model_index})")
        Utils.app_settings.rpi_model = Utils.project_data.settings.get('rpi_model', "RPI 4 model B")
        Utils.app_settings.rpi_model_index = Utils.project_data.settings.get('rpi_model_index', 6)
        print(f" RPi Model: {Utils.app_settings.rpi_model} (Index: {Utils.app_settings.rpi_model_index})")
        self.canvas.update()
        print(" Settings rebuilt")

    def _rebuild_blocks(self):
        """Recreate all block widgets on canvas from project_data"""
        print(f"Rebuilding {len(Utils.project_data.blocks)} blocks...")
        # Clear existing blocks from canvas
        for block_id in list(Utils.top_infos.keys()):
            if block_id in Utils.top_infos:
                widget = Utils.top_infos[block_id]['widget']
                widget.setParent(None)
                widget.deleteLater()
        
        Utils.top_infos.clear()
        
        # Recreate each block

        for block_id, block_data in Utils.project_data.blocks.items():
            block_id = str(block_id)
            print(f" Recreating block {block_id} of type {block_data['type']}...")
            try:
                # Create the block widget
                block_widget = self.canvas.spawner.create_block_from_data(
                    block_id=block_id,
                    block_type=block_data['type'],
                    x=block_data['x'],
                    y=block_data['y'],
                    value_1=block_data.get('value_1', ''),
                    value_2=block_data.get('value_2', ''),
                    combo_value=block_data.get('combo_value', ''),
                    switch_value=block_data.get('switch_value', False),
                )
                
                # Add to canvas
                self.canvas.add_draggable_widget(block_widget)
                
                # Store in Utils
                Utils.top_infos[block_id] = {
                    'widget': block_widget,
                    'id': block_id,
                    'type': block_data['type'],
                    'x': block_data['x'],
                    'y': block_data['y'],
                    'width': block_data['width'],
                    'height': block_data['height'],
                    'value_1': block_data.get('value_1', ''),
                    'value_2': block_data.get('value_2', ''),
                    'combo_value': block_data.get('combo_value', ''),
                    'switch_value': block_data.get('switch_value', False),
                    'in_connections': block_data.get('in_connections', []),
                    'out_connections': block_data.get('out_connections', []),
                }
                print(f" Utils.top_infos updated with block {block_id}")
                print(f" Utils.top_infos now has {len(Utils.top_infos)} blocks")
                print(f" Block data: {Utils.top_infos[block_id]}")
                print(f"  ✓ Block {block_id} ({block_data['type']}) recreated")
                
            except Exception as e:
                print(f"  ✗ Error recreating block {block_id}: {e}")


    def _rebuild_connections(self):
        """Recreate all connection paths from projectdata"""
        print(f"Rebuilding {len(Utils.project_data.connections)} connections...")
        
        # Don't clear! The blocks should already be in Utils.top_infos from rebuild_blocks()
        # Utils.paths.clear()  # KEEP THIS
        self.canvas.path_manager.clear_all_paths()
        
        print(f"Utils.top_infos contains: {list(Utils.top_infos.keys())}")
        print(f"Project connections: {list(Utils.project_data.connections.keys())}")
        
        for conn_id, conn_data in Utils.project_data.connections.items():
            try:
                from_block_id = str(conn_data.get("from_block"))
                to_block_id = str(conn_data.get("to_block"))
                
                print(f"Processing connection {conn_id}: {from_block_id} -> {to_block_id}")
                
                # DEBUG: Check what's actually in Utils.top_infos
                print(f"Available block IDs in Utils.top_infos: {list(Utils.top_infos.keys())}")
                print(f"Is {from_block_id} in top_infos? {from_block_id in Utils.top_infos}")
                print(f"Is {to_block_id} in top_infos? {to_block_id in Utils.top_infos}")
                
                if from_block_id not in Utils.top_infos or to_block_id not in Utils.top_infos:
                    print(f"❌ Connection {conn_id}: Missing block reference!")
                    print(f"  from_block_id ({from_block_id}) exists: {from_block_id in Utils.top_infos}")
                    print(f"  to_block_id ({to_block_id}) exists: {to_block_id in Utils.top_infos}")
                    continue
                
                from_block = Utils.top_infos[from_block_id]
                to_block = Utils.top_infos[to_block_id]
                
                from_blockwidget = from_block.get("widget")
                to_blockwidget = to_block.get("widget")
                
                # Recreate connection
                Utils.paths[conn_id] = {
                    "line": None,  # Will be drawn by pathmanager
                    "waypoints": conn_data.get("waypoints", []),
                    "from": from_blockwidget,
                    "to": to_blockwidget,
                    "from_circle": conn_data.get("from_circle", "out"),
                    "to_circle": conn_data.get("to_circle", "in"),
                    "color": None,  # Will use default
                }
                
                # Update block connection references
                from_block.get("out_connections", []).append(conn_id)
                to_block.get("in_connections", []).append(conn_id)
                
                print(f"✓ Connection {conn_id} recreated")
                
            except Exception as e:
                print(f"❌ Error recreating connection {conn_id}: {e}")
                import traceback
                traceback.print_exc()
        
        self.canvas.update()

    def _rebuild_variables_panel(self):
        """Recreate variables in the side panel"""
        print(f"Rebuilding {len(Utils.project_data.variables)} variables...")
        
        if not self.variable_frame:
            self.show_variable_frame()
        
        panel_layout = self.variable_frame.layout()
        
        # Clear existing variable rows
        for var_id in list(Utils.variables.keys()):
            if var_id in Utils.variables:
                widget = Utils.variables[var_id].get('widget')
                if widget:
                    panel_layout.removeWidget(widget)
                    widget.setParent(None)
                    widget.deleteLater()
        
        Utils.variables.clear()
        Utils.var_items.clear()
        Utils.vars_same.clear()
        self.variable_row_count = 1
        
        # Recreate each variable
        for var_id, var_data in Utils.project_data.variables.items():
            try:
                # Add variable row to UI
                self._add_variable_row_from_data(var_id, var_data)
                
                print(f"  ✓ Variable {var_id} ({var_data['name']}) recreated")
                
            except Exception as e:
                print(f"  ✗ Error recreating variable {var_id}: {e}")
        if self.variable_frame:
            self.hide_variable_frame()
        
    def _add_variable_row_from_data(self, var_id, var_data):
        """Add a single variable row to the panel from saved data"""
        print(f"Adding variable row from data: {var_id} with data {var_data}")
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(5, 5, 5, 5)
        
        # Name input
        name_input = QLineEdit()
        name_input.setText(var_data['name'])
        name_input.textChanged.connect(lambda text, v_id=var_id, t="Variable": self.name_changed(text, v_id, t))
        
        # Type input
        type_input = QComboBox()
        type_input.addItems(["int", "float", "bool", "string"])
        type_input.setCurrentText(var_data['type'])
        type_input.currentTextChanged.connect(lambda text, t="Variable": self.type_changed(text, t))
        
        # Value input
        value_input = QLineEdit()
        value_input.setText(str(var_data['value']))
        value_input.setPlaceholderText("Value")
        regex = QRegularExpression(r"^[0-9.\-]*$")
        validator = QRegularExpressionValidator(regex, self)
        value_input.setValidator(validator)
        value_input.textChanged.connect(lambda text, t="Variable": self.value_changed(text, t))
        
        # Delete button
        delete_btn = QPushButton("×")
        delete_btn.setFixedWidth(30)
        
        row_layout.addWidget(name_input)
        row_layout.addWidget(type_input)
        row_layout.addWidget(value_input)
        row_layout.addWidget(delete_btn)
        
        delete_btn.clicked.connect(lambda _, v_id=var_id, rw=row_widget, t="Variable": self.remove_row(rw, v_id, t))
        
        # Store in Utils
        Utils.variables[var_id] = {
            'name': var_data['name'],
            'type': var_data['type'],
            'value': str(var_data['value']),
            'widget': row_widget,
            'name_imput': name_input,
            'type_input': type_input,
            'value_input': value_input,
        }
        
        # Update UI maps
        Utils.var_items[var_id] = var_data['name']
        
        # Add to panel
        panel_layout = self.variable_frame.layout()
        if panel_layout:
            panel_layout.insertWidget(panel_layout.count() - 1, row_widget)
        
        self.variable_row_count += 1


    def _rebuild_devices_panel(self):
        """Recreate devices in the side panel"""
        print(f"Rebuilding {len(Utils.project_data.devices)} devices...")
        
        if not self.Devices_frame:
            self.show_devices_frame()
            
        panel_layout = self.Devices_frame.layout()
        
        # Clear existing device rows
        for dev_id in list(Utils.devices.keys()):
            if dev_id in Utils.devices:
                widget = Utils.devices[dev_id].get('widget')
                if widget:
                    panel_layout.removeWidget(widget)
                    widget.setParent(None)
                    widget.deleteLater()
        
        Utils.devices.clear()
        Utils.dev_items.clear()
        Utils.devs_same.clear()
        self.devices_row_count = 0
        
        # Recreate each device
        for dev_id, dev_data in Utils.project_data.devices.items():
            try:
                # Add device row to UI
                self._add_device_row_from_data(dev_id, dev_data)
                
                print(f"  ✓ Device {dev_id} ({dev_data['name']}) recreated")
                
            except Exception as e:
                print(f"  ✗ Error recreating device {dev_id}: {e}")

        if self.Devices_frame:
            self.hide_devices_frame()

    def _add_device_row_from_data(self, dev_id, dev_data):
        """Add a single device row to the panel from saved data"""
        
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(5, 5, 5, 5)
        
        # Name input
        name_input = QLineEdit()
        name_input.setText(dev_data['name'])
        name_input.textChanged.connect(lambda text, d_id=dev_id, t="Device": self.name_changed(text, d_id, t))
        
        # Type input
        type_input = QComboBox()
        type_input.addItems(["Output", "Input", "PWM"])
        type_input.setCurrentText(dev_data['type'])
        type_input.currentTextChanged.connect(lambda text, t="Device": self.type_changed(text, t))
        
        # PIN input
        pin_input = QLineEdit()
        if dev_data['pin']:
            pin_input.setText(str(dev_data['pin']))
        pin_input.setPlaceholderText("PIN")
        regex = QRegularExpression(r"^\\d*$")
        validator = QRegularExpressionValidator(regex, self)
        pin_input.setValidator(validator)
        pin_input.textChanged.connect(lambda text, t="Device": self.value_changed(text, t))
        
        # Delete button
        delete_btn = QPushButton("×")
        delete_btn.setFixedWidth(30)
        
        row_layout.addWidget(name_input)
        row_layout.addWidget(type_input)
        row_layout.addWidget(pin_input)
        row_layout.addWidget(delete_btn)
        
        delete_btn.clicked.connect(lambda _, d_id=dev_id, rw=row_widget, t="Device": self.remove_row(rw, d_id, t))
        
        # Store in Utils
        Utils.devices[dev_id] = {
            'name': dev_data['name'],
            'type': dev_data['type'],
            'PIN': dev_data['pin'],
            'widget': row_widget,
            'name_imput': name_input,
            'type_input': type_input,
            'value_input': pin_input,
        }
        
        # Update UI maps
        Utils.dev_items[dev_id] = dev_data['name']
        
        # Add to panel
        panel_layout = self.Devices_frame.layout()
        if panel_layout:
            panel_layout.insertWidget(panel_layout.count() - 1, row_widget)
        
        self.devices_row_count += 1
        
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
