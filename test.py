import sys
import ctypes
from PyQt6.QtCore import Qt, QEvent, QPoint, QObject
from PyQt6.QtWidgets import (QApplication, QWidget, QLineEdit, QVBoxLayout, 
                             QListWidget, QLabel, QFrame)

class PassivePopup(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 1. WINDOW FLAGS
        # Qt.Tool: Hides from taskbar, tells OS it's a utility window.
        # FramelessWindowHint: Removes title bar/borders.
        # WindowStaysOnTopHint: Ensures it floats above the main app.
        self.setWindowFlags(
            Qt.WindowType.Tool | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )

        # 2. QT ATTRIBUTES
        # Critical: Tells Qt to ask the OS *not* to activate this window when shown.
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # 3. FOCUS POLICY
        # Ensure Qt itself doesn't try to give it logical focus.
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Style for visibility
        self.setStyleSheet("background-color: #ffffff; border: 1px solid #a0a0a0;")
        self.addItems(["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"])

        # Install global event filter to handle "click outside"
        QApplication.instance().installEventFilter(self)

    def showEvent(self, event):
        """
        Apply platform-specific overrides when the window is mapped.
        """
        self._apply_windows_no_activate()
        super().showEvent(event)

    def _apply_windows_no_activate(self):
        """
        Windows-Specific Hardening:
        Even with WA_ShowWithoutActivating, clicking the popup on Windows 
        can still transfer activation. We use the Win32 API to set 
        WS_EX_NOACTIVATE, which makes the window permanently passive.
        """
        if sys.platform == "win32":
            GWL_EXSTYLE = -20
            WS_EX_NOACTIVATE = 0x08000000
            
            # Get the underlying window handle (HWND)
            hwnd = int(self.winId())
            
            # Helper to handle 32/64-bit API differences
            user32 = ctypes.windll.user32
            set_window_long = user32.SetWindowLongPtrW if hasattr(user32, "SetWindowLongPtrW") else user32.SetWindowLongW
            get_window_long = user32.GetWindowLongPtrW if hasattr(user32, "GetWindowLongPtrW") else user32.GetWindowLongW

            # Fetch current extended style and add NOACTIVATE
            ex_style = get_window_long(hwnd, GWL_EXSTYLE)
            set_window_long(hwnd, GWL_EXSTYLE, ex_style | WS_EX_NOACTIVATE)

    def eventFilter(self, source, event):
        """
        Re-implements 'Click-Outside-to-Close' behavior.
        Since we are not a Qt.Popup, we don't get this for free.
        """
        if self.isVisible() and event.type() == QEvent.Type.MouseButtonPress:
            # Check if the click is outside the popup's geometry
            global_pos = event.globalPosition().toPoint()
            if not self.geometry().contains(global_pos):
                # Optional: Don't close if clicking the "activator" (the line edit)
                # You can pass the activator widget to this class to check specifically.
                self.hide()
                
        return super().eventFilter(source, event)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Non-Stealing Focus Demo")
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        self.label = QLabel("Type below. The popup will appear, but the cursor will keep blinking.")
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        
        self.line_edit = QLineEdit()
        layout.addWidget(self.line_edit)
        layout.addStretch()

        # Instantiate the popup (no parent, so it's a window)
        self.popup = PassivePopup()
        
        # Connect signals
        self.line_edit.textEdited.connect(self.update_popup)

    def update_popup(self, text):
        if not text:
            self.popup.hide()
            return

        # Position popup exactly below the line edit
        rect = self.line_edit.rect()
        bottom_left = self.line_edit.mapToGlobal(rect.bottomLeft())
        
        self.popup.move(bottom_left)
        self.popup.setFixedWidth(self.line_edit.width())
        self.popup.setFixedHeight(100)
        
        # SHOW the popup. Thanks to our flags, this will NOT steal focus.
        self.popup.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())