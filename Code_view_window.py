from Imports import (QDialog, QMainWindow, QTextEdit, QVBoxLayout, QWidget, Qt, QScrollArea, QRect,
                     get_utils, QScroller, QIcon, QPropertyAnimation, QEasingCurve, QTimer)

Utils = get_utils()

class CodeViewerWindow(QDialog):
    _instance = None

    def __init__(self, parent=None):
        super().__init__()
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
    def get_instance(cls, parent=None):
        if cls._instance is not None:
            try:
                _ = cls._instance.isVisible()
                if not cls._instance.is_hidden:
                    return cls._instance
            except RuntimeError:
                cls._instance = None
            
            except Exception:
                cls._instance = None

        if cls._instance is None:
            cls._instance = cls(parent)
        return cls._instance

    def create_window(self):

        self.setWindowTitle(self.t("code_view_window.window_title"))
        self.setWindowIcon(QIcon('resources/images/APPicon.ico'))
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
            QTextEdit {
                background-color: #1F1F1F;
                color: #FFFFFF;
                border: 1px solid #3A3A3A;
                padding: 10px;
            }
             QScrollBar:vertical {
                background-color: #2B2B2B;
                width: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #3A3A3A;
                min-height: 20px;
                border-radius: 6px;
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

    def pulse_window(self):
        if hasattr(self, "_pulse_animation") and self._pulse_animation.state() == QPropertyAnimation.State.Running:
            return

        self._pulse_animation = QPropertyAnimation(self, b"geometry")
        self._pulse_animation.setDuration(100)
        self._pulse_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        # Get current geometry
        orig = self.geometry()
        
        # Calculate a larger geometry (expanding from the center)
        offset = 5  # Pixels to expand
        expanded = QRect(
            orig.x() - offset, 
            orig.y() - offset, 
            orig.width() + (offset * 2), 
            orig.height() + (offset * 2)
        )

        # Define keyframes: Start -> Expanded -> Original
        self._pulse_animation.setStartValue(orig)
        self._pulse_animation.setKeyValueAt(0.5, expanded)
        self._pulse_animation.setEndValue(orig)

        self._pulse_animation.start()

    def flash_window(self):
        original_style = self.styleSheet()
        highlight_style = original_style + "QDialog { background-color: #696969; }"
        
        def toggle_style(step):
            if step >= 8:  # 4 flashes = 8 toggles (on/off)
                self.setStyleSheet(original_style)
                return
            
            # If step is even, show highlight; if odd, show original
            if step % 2 == 0:
                self.setStyleSheet(highlight_style)
                self.pulse_window()  # Add pulse effect on highlight
            else:
                self.setStyleSheet(original_style)
            
            # Schedule the next toggle in 150ms
            QTimer.singleShot(100, lambda: toggle_style(step + 1))

        # Start the sequence
        toggle_style(0)

    def open(self):
        #print("Opening CodeViewerWindow")
        if self.is_hidden:
            #print("Initially hidden, showing window")
            self.is_hidden = False
            self.refresh_content() 
            self.show()
            self.raise_()
            self.activateWindow()
        else:
            #print("CodeViewerWindow already open, raising to front")
            self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
            self.raise_()           # Brings the widget to the top of the stack
            self.activateWindow()    # Gives the window keyboard focus   
            self.flash_window()
        return self
    
    def reject(self):
        """Redirect Esc key (reject) to close() so closeEvent fires"""
        self.close()

    def closeEvent(self, event):
        self.is_hidden = True
        self.state_manager.app_state.on_code_viewer_dialog_close()
        event.accept()