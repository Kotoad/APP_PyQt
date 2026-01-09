from Imports import (QWidget, QDialog, QVBoxLayout, QHBoxLayout,
QPushButton, QLabel, QFrame, QTabWidget, Qt, QFont,
pyqtSignal)

from Imports import get_State_Manager
from Imports import get_spawn_elements, get_utils

Utils = get_utils()
State_manager = get_State_Manager()
# Get the spawning_elements class and other exported items
spawning_elements = get_spawn_elements()[1]

# NOTE: BlockGraphicsItem is now in spawn_elements module
# We import it from there if needed:
# from spawn_elements_pyqt import BlockGraphicsItem


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
        self.setStyleSheet("""
            QDialog {
                background-color: #2B2B2B;
            }
            QTabWidget::pane {
                border: 1px solid #3A3A3A;
                background-color: #2B2B2B;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #1F1F1F;
                color: #FFFFFF;
                padding: 8px 20px;
                border: 1px solid #3A3A3A;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #1F538D;
            }
            QTabBar::tab:hover {
                background-color: #2667B3;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: none;
                padding: 10px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            QPushButton:pressed {
                background-color: #1F538D;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_shapes_tab()
        self.create_logic_tab()
        self.create_io_tab()
        self.create_functions_tab()
    
    def mousePressEvent(self, event):
        """Debug: Track if elements window gets mouse press"""
        super().mousePressEvent(event)
    
    def create_shapes_tab(self):
        """Create shapes tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(5)
        
        # Title
        title = QLabel("Shape Elements")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(10)
        
        # Buttons - MAPPED TO SPAWNING ELEMENTS
        shapes = [
            ("Start", "Start"),
            ("End", "End"),
            ("Timer", "Timer")
        ]
        
        for label, shape_type in shapes:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, s=shape_type: self.spawn_element(s))
            layout.addWidget(btn)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Shapes")
    
    def create_logic_tab(self):
        """Create logic tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(5)
        
        # Title
        title = QLabel("Logic Elements")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(10)
        
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
            btn.clicked.connect(lambda checked, s=logic_type: self.spawn_element(s))
            layout.addWidget(btn)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Logic")
    
    def create_io_tab(self):
        """Create I/O tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(5)
        
        # Title
        title = QLabel("Input/Output Elements")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(10)
        
        # Buttons - MAPPED TO SPAWNING ELEMENTS
        io_elements = ["Button", "Output", "Print", "Read File"]
        
        for element in io_elements:
            btn = QPushButton(element)
            btn.clicked.connect(lambda checked, e=element: self.spawn_element(e))
            layout.addWidget(btn)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "I/O")
    
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
            self.create_functions_tab() 
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
