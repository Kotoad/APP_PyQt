from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTabWidget,
                             QWidget, QComboBox)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QFont, QMouseEvent

models = ["RPI pico/pico W", "RPI zero/zero W", "RPI 2 zero W", "RPI 1 model B/B+", "RPI 2 model B", "RPI 3 model B/B+", "RPI 4 model B", "RPI 5"]

class MaxWidthComboBox(QComboBox):
    def __init__(self, parent=None, max_popup_width="", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._max_popup_width = max_popup_width
        self.setStyleSheet("""
            QComboBox::drop-down { width: 0px; border: none; }
            QComboBox::down-arrow { width: 0px; image: none; }
        """)

    def showPopup(self):
        super().showPopup()

        view = self.view()
        popup = view.parentWidget()   # usually the QFrame that draws the background
        # 2) Apply to view (for text)
        view.setFixedWidth(self._max_popup_width)

        # 3) Apply to popup frame (for background)
        if popup is not None:
            geo = popup.geometry()
            geo.setWidth(self._max_popup_width)
            popup.setGeometry(geo)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Open dropdown if clicked anywhere on the widget"""
        if self.rect().contains(event.pos()):
            self.showPopup()
        else:
            super().mousePressEvent(event)


class DeviceSettingsWindow(QDialog):
    _instance = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_hidden = False
        
        
        
        self.setup_ui()
    
    @classmethod
    def get_instance(cls, parent):
        """Get or create singleton instance"""
        if cls._instance is None or not cls._instance.isVisible():
            cls._instance = cls(parent)
        return cls._instance
    
    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle("Settings")
        self.resize(400, 300)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
    
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
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        self.create_device_tab()
    
    def create_device_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setSpacing(5)
        
        title = QLabel("Device Settings")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab_layout.addWidget(title)
        
        tab_layout.addSpacing(10)
        
        label = QLabel("Select your RPI model")
        tab_layout.addWidget(label)
        
        self.rpi_model_combo = MaxWidthComboBox(self, max_popup_width=358)
        self.rpi_model_combo.addItems(models)
        tab_layout.addWidget(self.rpi_model_combo)
        print({self.rpi_model_combo.width()})
        tab_layout.addStretch()
        self.tab_widget.addTab(tab, "Devices")
        
    def open(self):
        if not self.is_hidden:
            self.show()
            self.raise_()
            self.activateWindow()
        return self

    def closeEvent(self, event):
        """Handle close event"""
        self.is_hidden = True
        event.accept()