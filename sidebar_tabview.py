"""
SIDEBAR TABVIEW STRUCTURE FOR PyQt6

Using QVBoxLayout instead of QListWidget for better control over separator height.
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QStackedWidget, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal

from Imports import get_utils

Utils = get_utils()

class SidebarTabView(QWidget):
    """
    Professional sidebar with tab navigation.
    
    Structure:
    ┌──────────────┬─────────────────┐
    │ Canvas       │                 │
    │ ──────────── │ Content Area    │
    │ Variables    │ (One page at    │
    │ Devices      │ a time)         │
    │ Inspector    │                 │
    └──────────────┴─────────────────┘
    """
    
    tab_changed = pyqtSignal(int)
    
    def __init__(self, parent=None, canvas_class=None):
        super().__init__(parent)
        self.GridCanvasClass = canvas_class  # Store the class for later use
        self.Grid_canvas = None  # Will be set in init_ui if canvas_class provided
        self.init_ui()
    
    def init_ui(self):
        """Initialize sidebar and content areas"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ===== LEFT SIDEBAR =====
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setMinimumWidth(120)
        self.sidebar_frame.setMaximumWidth(150)
        self.sidebar_frame.setStyleSheet("""
            QFrame {
                background-color: #2B2B2B;
                border-right: 1px solid #3A3A3A;
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Tab buttons container (using QVBoxLayout instead of QListWidget)
        self.tab_container = QWidget()
        self.tab_layout = QVBoxLayout(self.tab_container)
        self.tab_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_layout.setSpacing(0)
        
        sidebar_layout.addWidget(self.tab_container)
        sidebar_layout.addStretch()
        
        main_layout.addWidget(self.sidebar_frame)
        
        # ===== RIGHT CONTENT AREA =====
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("""
            QStackedWidget {
                background-color: #1F1F1F;
            }
        """)
        
        main_layout.addWidget(self.content_area, stretch=1)
        
        if self.GridCanvasClass:
            self.Grid_canvas = self.GridCanvasClass()
        else:
            self.Grid_canvas = None
        
        # Storage
        self.pages = {}
        self.page_count = 0
        self.canvas_count = 0
        self.tab_buttons = []  # Track tab buttons
        
    def set_canvas_class(self, canvas_class):
        """
        Set the GridCanvas class after initialization.
        Useful if canvas_class wasn't available at __init__ time.
        """
        self.GridCanvasClass = canvas_class
        if self.Grid_canvas is None and canvas_class:
            self.Grid_canvas = canvas_class()
    
    def add_tab(self, tab_name, content_widget=None, icon=None, reference=None):
        """
        Add a tab to the sidebar
        
        Args:
            tab_name: Name of the tab
            content_widget: Widget to show when tab is active
            icon: Optional QIcon for the tab
            
        Returns:
            Index of the new tab
        """
        if content_widget is None:
            content_widget = QWidget()
            layout = QVBoxLayout(content_widget)
            layout.addWidget(QLabel(f"Content for {tab_name}"))
            layout.addStretch()
        
        self.content_area.addWidget(content_widget)
        self.pages[tab_name] = content_widget
        
        # Create tab button
        tab_button = QPushButton(tab_name)
        tab_button.setStyleSheet("""
            QPushButton {
                background-color: #2B2B2B;
                color: #FFFFFF;
                border: none;
                padding: 12px;
                text-align: left;
            }
            
            QPushButton:hover {
                background-color: #3A3A3A;
            }
            
            QPushButton:pressed {
                background-color: #1F538D;
                border-left: 3px solid #4CAF50;
            }
        """)
        
        tab_index = self.page_count
        tab_button.clicked.connect(lambda: self._on_tab_clicked(tab_index, reference))
        if reference == "canvas":
            self.tab_layout.insertWidget(self.canvas_count, tab_button)
        else:
            self.tab_layout.addWidget(tab_button)
        self.tab_buttons.append({
            'button': tab_button,
            'index': tab_index,
            'name': tab_name
        })
        
        self.page_count += 1
        if reference == "canvas":
            self.canvas_count += 1
        return tab_index - 1
    
    def add_new_canvas_tab_button(self):
        """Add a special button to create a new canvas tab"""
        new_canvas_button = QPushButton("+ New Canvas")
        new_canvas_button.setStyleSheet("""
            QPushButton {
                background-color: #2B2B2B;
                color: #FFFFFF;
                border: none;
                padding: 12px;
                text-align: left;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
            }
            QPushButton:pressed {
                background-color: #1F538D;
                border-left: 3px solid #4CAF50;
            }
        """)
        new_canvas_button.clicked.connect(self._on_new_canvas_clicked)
        self.tab_layout.addWidget(new_canvas_button)
    
    def _on_new_canvas_clicked(self):
        """Handler for new canvas tab button click"""
        if self.Grid_canvas is None:
            print("Warning: Grid_canvas not initialized")
            return
        new_canvas = self.GridCanvasClass()
        
        new_tab_index = self.add_tab(
            f"Canvas {self.canvas_count + 1}",
            new_canvas,
            reference="canvas"
        )
        Utils.canvas_instances.append(new_canvas)
        print(f"Utils.canvas_instances count: {len(Utils.canvas_instances)}")
        print(f"Utils.canvas_instances: {Utils.canvas_instances}")
        self.set_current_tab(new_tab_index)
    
    def add_separator(self):
        """Add a visual separator line with exactly 5px height"""
        
        # Create a container for the separator
        separator_container = QFrame()
        separator_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)
        separator_container.setFixedHeight(5)
        
        # Create the actual line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Plain)
        separator.setLineWidth(1)
        separator.setStyleSheet("background-color: #555555;")
        
        # Layout for container
        layout = QVBoxLayout(separator_container)
        layout.setContentsMargins(0, 2, 0, 2)  # Vertical padding: 2px top + 2px bottom + 1px line = 5px total
        layout.setSpacing(0)
        layout.addWidget(separator)
        
        self.tab_layout.addWidget(separator_container)
    
    def set_current_tab(self, tab_index):
        """Switch to a specific tab by index"""
        if 0 <= tab_index < len(self.tab_buttons):
            self._on_tab_clicked(tab_index)
    
    def get_current_tab_index(self):
        """Get currently active tab index"""
        return self.content_area.currentIndex()
    
    def get_tab_widget(self, tab_name):
        """Get the widget for a specific tab"""
        return self.pages.get(tab_name)
    
    def _on_tab_clicked(self, tab_index, reference=None):
        """Internal handler for tab clicks"""
        if 0 <= tab_index < len(self.tab_buttons):
            self.content_area.setCurrentIndex(tab_index)
            
            # Update button styles
            for tb in self.tab_buttons:
                if tb['index'] == tab_index:
                    tb['button'].setStyleSheet("""
                        QPushButton {
                            background-color: #1F538D;
                            color: #FFFFFF;
                            border-left: 3px solid #4CAF50;
                            padding: 12px;
                            text-align: left;
                        }
                    """)
                else:
                    tb['button'].setStyleSheet("""
                        QPushButton {
                            background-color: #2B2B2B;
                            color: #FFFFFF;
                            border: none;
                            padding: 12px;
                            text-align: left;
                        }
                        
                        QPushButton:hover {
                            background-color: #3A3A3A;
                        }
                    """)
            if reference == "canvas":
                print(f"Setting Utils.courent_canvas to canvas tab index {tab_index}")
                print(f"Utils.canvas_instances: {Utils.canvas_instances}")
                #if tab_index - self.canvas_count < 0:
                    #tab_index = 0
                    #print(f"Courent canvas index: {tab_index}")
                    #Utils.courent_canvas = Utils.canvas_instances[tab_index]
                    #print(f"Set Utils.courent_canvas to tab '{Utils.courent_canvas}'")
                #else:
                    #print(f"Setting Utils.courent_canvas to index {tab_index - self.canvas_count+1}")
                    #Utils.courent_canvas = Utils.canvas_instances[tab_index-self.canvas_count+1]
                    #print(f"Set Utils.courent_canvas to tab '{Utils.courent_canvas}'")
            self.tab_changed.emit(tab_index)


# Example usage
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Sidebar TabView Example")
    window.resize(800, 600)
    
    sidebar = SidebarTabView()
    
    # Add example tabs
    sidebar.add_tab("Canvas", None)
    sidebar.add_tab("Canvas 2", None)
    sidebar.add_separator()  # Add separator with 5px height
    sidebar.add_tab("Variables", None)
    sidebar.add_tab("Devices", None)
    sidebar.add_tab("Inspector", None)
    
    window.setCentralWidget(sidebar)
    window.show()
    
    sys.exit(app.exec())