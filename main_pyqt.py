from Imports import (QApplication, sys)
from GUI_pyqt import MainWindow

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
