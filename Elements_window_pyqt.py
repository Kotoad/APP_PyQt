from Imports import (QWidget, QDialog, QVBoxLayout, QHBoxLayout,
QPushButton, QLabel, QFrame, QTabWidget, Qt, QFont,
pyqtSignal)

from Imports import get_spawn_elements

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
        
        self.parent_canvas = parent
        
        # Create spawning_elements instance
        # This now handles BlockGraphicsItem creation internally
        self.element_spawner = spawning_elements(self.parent_canvas)
        self.element_spawner.elements_window = self
        
        self.is_hidden = False
        
        # Store spawner reference on canvas
        if hasattr(parent, 'spawner'):
            parent.spawner = self.element_spawner
        
        self.setup_ui()
    
    @classmethod
    def get_instance(cls, parent):
        """Get or create singleton instance"""
        if cls._instance is None or not cls._instance.isVisible():
            cls._instance = cls(parent)
        return cls._instance
    
    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle("Add Element")
        self.resize(550, 400)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        
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
        io_elements = ["Input", "Output", "Print", "Read File"]
        
        for element in io_elements:
            btn = QPushButton(element)
            btn.clicked.connect(lambda checked, e=element: self.spawn_element(e))
            layout.addWidget(btn)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "I/O")
    
    def spawn_element(self, element_type):
        """
        Spawn a shape/logic/IO element
        
        Args:
            element_type: "Start", "End", "Timer", "If", "While", "Switch", etc.
        """
        try:
            print(f"\n[ElementsWindow] spawn_element called: {element_type}")
            
            # Emit signal for external listeners
            self.element_requested.emit(element_type)
            
            # Start the spawning process via element_spawner
            # element_spawner.start() will wait for mouse click to place the element
            self.element_spawner.start(self.parent_canvas, element_type)
            
            print(f"  ✓ Element spawn initiated: {element_type}")
            
        except Exception as e:
            print(f"  ✗ Error spawning {element_type}: {e}")
            import traceback
            traceback.print_exc()
    
    def open(self):
        """Show the window"""
        if not self.is_hidden:
            self.show()
            self.raise_()
            self.activateWindow()
        return self
    
    def closeEvent(self, event):
        """Handle close event"""
        self.is_hidden = True
        event.accept()
