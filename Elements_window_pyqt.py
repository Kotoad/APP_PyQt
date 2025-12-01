from PyQt6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from spawn_elements_pyqt import spawning_elements


class ElementsWindow(QDialog):
    """Elements selection window with tabs"""
    
    _instance = None
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_canvas = parent
        self.element_spawner = spawning_elements(self.parent_canvas)
        self.element_spawner.elements_window = self
        self.is_hidden = False
        
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
        #print("⚠ ElementsWindow.mousePressEvent fired!")
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
        
        # Buttons
        shapes = [
            ("Start", "Start"),
            ("End", "End"),
            ("Timer", "Timer")
        ]
        
        for label, shape_type in shapes:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, s=shape_type: self.spawn_shape(s))
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
        
        # Buttons
        logic_elements = [
            ("If", "If"),
            ("While", "While"),
            ("For Loop", "For Loop")
        ]
        
        for label, logic_type in logic_elements:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, s=logic_type: self.spawn_shape(s))
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
        
        # Buttons
        io_elements = ["Input", "Output", "Print", "Read File"]
        
        for element in io_elements:
            btn = QPushButton(element)
            layout.addWidget(btn)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "I/O")
    
    def spawn_shape(self, shape_type):
        """Spawn a shape element"""
        try:
            self.element_spawner.start(self.parent_canvas, shape_type)
            print(f"Spawned: {shape_type}")
        except Exception as e:
            print(f"Error spawning {shape_type}: {e}")
    
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
