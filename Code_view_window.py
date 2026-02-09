from Imports import (QDialog, QMainWindow, QTextEdit, QVBoxLayout, QWidget, Qt, QScrollArea,
                     get_utils, QScroller)

Utils = get_utils()

class CodeViewerWindow(QDialog):
    _instance = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_canvas = parent
        self.is_hidden = True
        self._layout = None
        self.text_edit = None
        self.scroll_widget = None
        self.state_manager = Utils.state_manager
        self.translation_manager = Utils.translation_manager
        self.t = self.translation_manager.translate
        self.create_window()

    @classmethod
    def get_instance(cls, canvas):
        if cls._instance is not None:
            try:
                _ = cls._instance.isVisible()
                if not cls._instance.is_hidden:
                    if cls._instance.parent_canvas != canvas:
                        cls._instance.parent_canvas = canvas
                    return cls._instance
            except RuntimeError:
                cls._instance = None
            
            except Exception:
                cls._instance = None

        if cls._instance is None:
            cls._instance = cls(canvas)
        return cls._instance

    def create_window(self):

        self.setWindowTitle(self.t("code_view_window.window_title"))
        self.resize(600, 400)
        self.setWindowFlag(Qt.WindowType.Window)

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
        if self._layout is None:
            self._layout = QVBoxLayout()
            self._layout.setContentsMargins(10, 10, 10, 10)

            self.scroll_widget = QScrollArea()
            QScroller.grabGesture(
                self.scroll_widget.viewport(),
                QScroller.ScrollerGestureType.LeftMouseButtonGesture
            )
            self.scroll_widget.setWidgetResizable(True)

            self.text_edit = QTextEdit()
            self.text_edit.setReadOnly(True)
            self.text_edit.setText(self.generate_code())
            
            self.scroll_widget.setWidget(self.text_edit)
            self._layout.addWidget(self.scroll_widget)
            self.setLayout(self._layout)
        
        self.refresh_content()

    def generate_code(self):
        try:
            with open("File.py", "r") as file:
                content = file.read()
                if content.strip():
                    return content
                else:
                    return self.t("code_view_window.file_empty")
                    
        except FileNotFoundError:
            return self.t("code_view_window.file_not_found")
        except Exception as e:
            return  self.t("code_view_window.error_reading_file").format(error_type=type(e).__name__, error_message=str(e))

    def refresh_content(self):
        """Update the code display without recreating the window"""
        if self.text_edit:
            self.text_edit.setText(self.generate_code())

    def open(self):
        if self.is_hidden:
            print("Opening CodeViewerWindow")
            self.is_hidden = False
            self.refresh_content()
            self.show()
            self.raise_()
            self.activateWindow()
        return self
    
    def reject(self):
        """Redirect Esc key (reject) to close() so closeEvent fires"""
        self.close()

    def closeEvent(self, event):
        self.is_hidden = True
        self.state_manager.app_state.on_code_viewer_dialog_close()
        event.accept()