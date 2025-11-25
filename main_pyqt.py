from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from GUI_pyqt import MainWindow
import sys


def main():
    """Main entry point"""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Visual Programming Interface")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
