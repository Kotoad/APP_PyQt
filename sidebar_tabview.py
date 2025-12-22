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