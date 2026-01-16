from cProfile import label
from Imports import (QWidget, QDialog, QVBoxLayout, QHBoxLayout,
QPushButton, QLabel, QFrame, QTabWidget, Qt, QFont,
pyqtSignal, QListWidget, QScrollArea)

from Imports import get_State_Manager
from Imports import get_spawn_elements, get_utils

Utils = get_utils()
State_manager = get_State_Manager()
spawning_elements = get_spawn_elements()[1]

background_color = "#2B2B2B"
border_color = "#3A3A3A"

class ElementsWindow(QDialog):
    """Elements selection window with tabs - synced with spawn_elements"""
    
    _instance = None
    
    # Signals for element spawning
    element_requested = pyqtSignal(str)  # element_type
    
    def __init__(self, parent=None):
        super().__init__(parent)
        #print(f"Curent canvas in ElementsWindow init: {parent}")
        self.parent_canvas = parent
        self.state_manager = State_manager.get_instance()
        # Create spawning_elements instance
        # This now handles BlockGraphicsItem creation internally
        
        self.is_hidden = True
        self.f_tab = None
        self.now_created = False

        self.setup_ui()
    
    @classmethod
    def get_instance(cls, parent):
        """Get or create singleton instance"""
        #print(f"ElementsWindow get_instance called with parent: {parent}")
        if cls._instance is not None:
            #print("ElementsWindow instance exists, checking visibility")
            try:
                #print(" Checking if instance is hidden")
                #print(f" Instance is hidden: {cls._instance.is_hidden}")
                if cls._instance.is_hidden:
                    # ✓ FIX: Update parent_canvas when canvas changes
                    #print(f"Current canvas in ElementsWindow get_instance: {parent}")
                    #print(f"Existing ElementsWindow canvas: {cls._instance.parent_canvas}")
                    if cls._instance.parent_canvas != parent:
                        #print(f"Updating ElementsWindow canvas")
                        cls._instance.parent_canvas = parent
                        #print(f"New ElementsWindow canvas set: {cls._instance.parent_canvas}")
                    return cls._instance
            except RuntimeError:
                #print("ElementsWindow instance was deleted, creating new one")
                cls._instance = None

            except Exception as e:
                #print(f"Error checking ElementsWindow instance: {e}")
                cls._instance = None

        if cls._instance is None:
            #print("Creating new ElementsWindow instance")
            #print(f"New ElementsWindow canvas: {parent}")
            cls._instance = cls(parent)
        
        return cls._instance
    
    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle("Add Element")
        self.resize(550, 400)
        self.setWindowFlags(Qt.WindowType.Window)
        
        # Style
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {background_color};
            }}
            QTabWidget::pane {{
                border: 1px solid {border_color};
                background-color: {background_color};
            }}
            QTabWidget::tab-bar {{
                alignment: left;
            }}
            QTabBar::tab {{
                background-color: {background_color};
                color: #FFFFFF;
                padding: 8px 20px;
                border: 1px solid {border_color};
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background-color: #1F538D;
            }}
            QTabBar::tab:hover {{
                background-color: #2667B3;
            }}
            QLabel {{
                color: #FFFFFF;
            }}
            QPushButton {{
                background-color: {background_color};
                color: #FFFFFF;
                border: none;
                padding: 10px;
                border: 1px solid {border_color};
                border-radius: 4px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: #4A4A4A;
            }}
            QPushButton:pressed {{
                background-color: #1F538D;
            }}
            QWidget {{ background-color: {background_color}; }}
            QLabel {{
                background-color: {background_color};
                border: 1px solid {border_color};
                padding: 10px;
            }}
        """)
        
        self.dropdown_menus = []

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_basic_tab()
        self.create_logic_tab()
        self.create_io_tab()
        self.create_math_tab()
        for canvas_id, canvas_info in Utils.canvas_instances.items():
            if canvas_info['canvas'] == self.parent_canvas:
                if canvas_info['ref'] == 'function':
                    print("Creating Functions tab for function canvas")
                    self.create_functions_tab()
                    break
    
    def mousePressEvent(self, event):
        """Debug: Track if elements window gets mouse press"""
        super().mousePressEvent(event)
    #MARK: Basic Tab
    def create_basic_tab(self):
        """Create basic tab"""
        tab = QWidget()

        layout = QHBoxLayout(tab)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        left_widget.setMinimumWidth(200)

        left_label = QLabel("Basic Blocks")
        left_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        left_layout.addWidget(left_label)
        left_layout.addSpacing(10)
        # Buttons - MAPPED TO SPAWNING ELEMENTS
        basic_elements = [
            ("Start", "Start"),
            ("End", "End"),
            ("Timer", "Timer")
        ]

        for label, element_type in basic_elements:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, s=element_type, t='basic': self.on_block_selected(s, t))
            left_layout.addWidget(btn)

        self.basic_description_text = QLabel("")
        self.basic_description_text.setWordWrap(True)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.basic_description_text)
        scroll_area.setWidgetResizable(True)
        right_label = QLabel("Block Details")
        right_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        right_layout.addWidget(right_label)
        right_layout.addSpacing(10)
        right_layout.addWidget(scroll_area)

        add_button = QPushButton("Add Selected Block")
        add_button.clicked.connect(lambda: self.spawn_element(self.basic_description_text.text().split(":\n\n")[0]))
        right_layout.addWidget(add_button)

        left_layout.addStretch()
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)
        self.tab_widget.addTab(tab, "Basic")
        self.show_block_details("Start", 'basic')  # Show default details
    
    #MARK: Logic Tab
    def create_logic_tab(self):
        """Create logic tab"""
        tab = QWidget()

        layout = QHBoxLayout(tab)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setMinimumWidth(200)


        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        
        # Title
        title = QLabel("Logic Blocks")
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(title)
        left_layout.addSpacing(10)
        
        # Buttons - MAPPED TO SPAWNING ELEMENTS
        logic_elements = [
            ("If", "If"),
            ("While", "While"),
            ("While true", "While_true"),
            ("Switch", "Switch"),
            ("For Loop", "For Loop")
        ]
        
        for label, logic_type in logic_elements:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, s=logic_type, t='logic': self.on_block_selected(s, t))
            left_layout.addWidget(btn)
        
        self.logic_description_text = QLabel("")
        self.logic_description_text.setWordWrap(True)
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.logic_description_text)
        scroll_area.setWidgetResizable(True)
        right_label = QLabel("Block Details")
        right_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        right_layout.addWidget(right_label)
        right_layout.addSpacing(10)
        right_layout.addWidget(scroll_area)

        add_button = QPushButton("Add Selected Block")
        add_button.clicked.connect(lambda: self.spawn_element(self.logic_description_text.text().split(":\n\n")[0]))
        right_layout.addWidget(add_button)

        left_layout.addStretch()
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)
        self.tab_widget.addTab(tab, "Logic")
        self.show_block_details("If", 'logic')  # Show default details
    #MARK: I/O Tab
    def create_io_tab(self):
        """Create I/O tab"""
        tab = QWidget()

        layout = QHBoxLayout(tab)

        left_widget = QWidget()
        self.IO_left_layout = QVBoxLayout(left_widget)
        left_widget.setMinimumWidth(200)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        
        # Title
        title = QLabel("Input/Output Blocks")
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.IO_left_layout.addWidget(title)
        self.IO_left_layout.addSpacing(10)
        
        # Buttons - MAPPED TO SPAWNING ELEMENTS

        io_elements = {
            'Button': {'name': 'Button', 'is_dropdown': False},
            'LED': {'name': 'LED', 'is_dropdown': True},
        }
        
        for label, element in io_elements.items():
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, e=element['name'], t='io', is_d=element['is_dropdown']: self.on_block_selected(e, t, is_d))
            self.IO_left_layout.addWidget(btn)
        
        self.IO_description_text = QLabel("")
        self.IO_description_text.setWordWrap(True)
    
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.IO_description_text)
        scroll_area.setWidgetResizable(True)
        right_label = QLabel("Block Details")
        right_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        right_layout.addWidget(right_label)
        right_layout.addSpacing(10)
        right_layout.addWidget(scroll_area)

        add_button = QPushButton("Add Selected Block")
        add_button.clicked.connect(lambda: self.spawn_element(self.IO_description_text.text().split(":\n\n")[0]))
        right_layout.addWidget(add_button)

        self.IO_left_layout.addStretch()
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)
        self.tab_widget.addTab(tab, "I/O")
        self.show_block_details("Button", 'io')  # Show default details
    #MARK: Math Tab
    def create_math_tab(self):
        """Create math tab"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setMinimumWidth(200)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Title
        title = QLabel("Math Blocks")
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(title)
        left_layout.addSpacing(10)
        
        # Buttons - MAPPED TO SPAWNING ELEMENTS
        math_elements = [
            ("Sum", "Sum"),
            ("Subtract", "Subtract"),
            ("Multiply", "Multiply"), 
            ("Divide", "Divide"), 
            ("Modulo", "Modulo"), 
            ("Power", "Power"), 
            ("Square Root", "Square_root"),
            ("Random Number", "Random_number")
        ]
        
        for label, element in math_elements:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, e=element, t='math': self.show_block_details(e, t))
            left_layout.addWidget(btn)
        
        self.math_description_text = QLabel("")
        self.math_description_text.setWordWrap(True)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.math_description_text)
        scroll_area.setWidgetResizable(True)
        right_label = QLabel("Block Details")
        right_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        right_layout.addWidget(right_label)
        right_layout.addSpacing(10)
        right_layout.addWidget(scroll_area)

        add_button = QPushButton("Add Selected Block")
        add_button.clicked.connect(lambda: self.spawn_element(self.math_description_text.text().split(":\n\n")[0]))
        right_layout.addWidget(add_button)

        left_layout.addStretch()
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)
        self.tab_widget.addTab(tab, "Math")
        self.show_block_details("Sum", 'math')  # Show default details
    #MARK: Functions Tab
    def create_functions_tab(self):
        """Create functions tab"""
        #print("Creating Functions tab in ElementsWindow")
        #print(F" Self f_tab: {self.f_tab if hasattr(self, 'f_tab') else 'Not defined'}")
        
        if self.f_tab is not None and self.layout.count() > 0:
            while self.layout.count():
                child = self.layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            for i in range(self.layout.count() - 1, -1, -1):
                item = self.layout.itemAt(i)
                if item and item.spacerItem():
                    self.layout.takeAt(i)

        if self.f_tab is None:
            self.f_tab = QWidget()
            self.layout = QVBoxLayout(self.f_tab)
            self.layout.setSpacing(5)
            self.now_created = True
            # Title
            title = QLabel("Functions")
            title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(title)
            self.layout.addSpacing(10)
            
        

        function_elements = []
            # Buttons - MAPPED TO SPAWNING ELEMENTS
        for f, f_info in Utils.functions.items():
            #print(f"Function available: {f} with info {f_info}")
            function_elements.append(f_info['name'])
        #print(f"Function elements collected: {function_elements}")
        for element in function_elements:
            btn = QPushButton(element)
            element_type = "Function"
            btn.clicked.connect(lambda checked, e=element_type, n=element if element else None: self.spawn_element(e, n))
            self.layout.addWidget(btn)
        self.layout.addStretch()

        if self.now_created:
            #print("Adding Functions tab to ElementsWindow")
            self.tab_widget.addTab(self.f_tab, "Functions")
    #MARK: Block Details
    def on_block_selected(self, element_type, tab_name, is_dropdown=False):
        """Handle selection of basic block from list"""
        if is_dropdown:
            self.open_dropdown_menu(element_type, tab_name)
        else:
            self.show_block_details(element_type, tab_name)

    def open_dropdown_menu(self, element_type, tab_name):

        if element_type == "LED":
            if element_type not in self.dropdown_menus:
                self.dropdown_menus.append(element_type)
                for blocks in (('Blink LED', 'Blink_LED'), ('Toggle LED', 'Toggle_LED'), ('PWM LED control', 'PWM_LED')):
                    label, block_name = blocks
                    btn = QPushButton(label)
                    btn.clicked.connect(lambda checked, e=block_name, t=tab_name: self.on_block_selected(e, t))
                    self.IO_left_layout.insertWidget(self.IO_left_layout.count() - 1, btn)
            elif element_type in self.dropdown_menus:
                # Remove dropdown options
                self.dropdown_menus.remove(element_type)
                for i in range(self.IO_left_layout.count() - 1, -1, -1):
                    item = self.IO_left_layout.itemAt(i)
                    if item and item.widget() and item.widget().text() in ('Blink LED', 'Toggle LED', 'PWM LED control'):
                        widget = item.widget()
                        self.IO_left_layout.removeWidget(widget)
                        widget.deleteLater()
            

    def show_block_details(self, element_type, tab_name):
        """Show details for selected basic block"""
        # Clear previous details
        block_data = {
            "Start": {
                "description": "The starting point of the flow."
            },
            "End": {
                "description": "The endpoint of the flow."
            },
            "Timer": {
                "description": "A timer that triggers after a set duration."
            },
            "Switch": {
                "description": "A control structure that allows branching based on multiple conditions."
            },
            "If": {
                "description": "A conditional statement that executes a block of code if a specified condition is true."
            },
            "While": {
                "description": "A loop that continues to execute a block of code as long as a specified condition is true."
            },
            "While_true": {
                "description": "A loop that continues to execute a block of code indefinitely until manually stopped."
            },
            "For Loop": {
                "description": "A loop that iterates over a sequence of values for a specified number of times."
            },
            "Sum": {
                "description": "Calculates the sum of two or more numbers."
            },
            "Subtract": {
                "description": "Calculates the difference between two numbers."
            },
            "Multiply": {
                "description": "Calculates the product of two or more numbers."
            },
            "Divide": {
                "description": "Calculates the quotient of two numbers."
            },
            "Modulo": {
                "description": "Calculates the remainder of the division of two numbers."
            },
            "Power": {
                "description": "Raises a number to the power of an exponent."
            },
            "Square_root": {
                "description": "Calculates the square root of a number."
            },
            "Random_number": {
                "description": "Generates a random number within a specified range."
            },
            "Button": {
                "description": "An input block that represents a button press."
            },
        }
        # Add details based on element_type
        if element_type in block_data:
            data = block_data[element_type]
            if tab_name == 'basic':
                self.basic_description_text.setText(f"{element_type}:\n\n{data['description']}")
            elif tab_name == 'logic':
                self.logic_description_text.setText(f"{element_type}:\n\n{data['description']}")
            elif tab_name == 'math':
                self.math_description_text.setText(f"{element_type}:\n\n{data['description']}")
            elif tab_name == 'io':
                self.IO_description_text.setText(f"{element_type}:\n\n{data['description']}")
        else:
            data = {"description": "No description available."}
            if tab_name == 'basic':
                self.basic_description_text.setText(f"{element_type}:\n\n{data['description']}")
            elif tab_name == 'logic':
                self.logic_description_text.setText(f"{element_type}:\n\n{data['description']}")
            elif tab_name == 'math':
                self.math_description_text.setText(f"{element_type}:\n\n{data['description']}")
            elif tab_name == 'io':
                self.IO_description_text.setText(f"{element_type}:\n\n{data['description']}")
    #MARK: Spawn Element
    def spawn_element(self, element_type, name=None):
        """
        Spawn a shape/logic/IO element
        
        Args:
            element_type: "Start", "End", "Timer", "If", "While", "Switch", etc.
        """
        
        try:
            #print(f"ElementsWindow spawn_element called: {element_type}")
            
            # Get CURRENT canvas
            #print(f" Parent canvas in ElementsWindow: {self.parent_canvas}, main_window: {getattr(self.parent_canvas, 'main_window', None)}")
            if self.parent and hasattr(self.parent_canvas, 'main_window'):
                #print(" Getting current canvas from main window")
                current_canvas = self.parent_canvas.main_window.current_canvas
            else:
                current_canvas = self.parent_canvas
            
            if current_canvas is None:
                return
            
            # ✓ Use CURRENT canvas's spawner, not stored self.element_spawner!
            if hasattr(current_canvas, 'spawner'):
                print("Current state of canvas before spawning:", self.state_manager.canvas_state.current_state())
                if self.state_manager.canvas_state.on_adding_block():
                    print("Current state of canvas before spawning:", self.state_manager.canvas_state.current_state())
                    current_canvas.spawner.start(current_canvas, element_type, name=name)
                    #print(f"Element spawn initiated on canvas {id(current_canvas)}")
                else:
                    print("Canvas cannot add block right now.")
            else:
                print("ERROR: Canvas has no spawner!")
            
        except Exception as e:
            print(f"Error spawning {element_type}: {e}")
            import traceback
            traceback.print_exc()
    
    def open(self):
        """Show the window"""
        print("ElementsWindow open() called")
        if self.is_hidden:
            print(" Showing ElementsWindow")
            self.is_hidden = False 
            for canvas_id, canvas_info in Utils.canvas_instances.items():
                if canvas_info['canvas'] == self.parent_canvas:
                    if canvas_info['ref'] == 'function':
                        print("Ensuring Functions tab is created for function canvas")
                        self.create_functions_tab()
                        break
            self.show()
            self.raise_()
            self.activateWindow()
        return self
    
    def closeEvent(self, event):
        """Handle close event"""
        #print("ElementsWindow closeEvent called")
        self.is_hidden = True
        self.state_manager.app_state.on_elements_dialog_close()
        event.accept()
