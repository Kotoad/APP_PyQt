from Imports import (QApplication, sys, get_Translation_Manager)
from GUI_pyqt import MainWindow

TranlationManager = get_Translation_Manager()

def main():
    """Main entry point"""
    # Create application
    Tranlation_Manager = get_Translation_Manager().get_instance()
    t = Tranlation_Manager.translate
    app = QApplication(sys.argv)
    app.setApplicationName(t("_metadata.app_title"))
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
