from operator import index
from Imports import get_utils
Utils = get_utils()
from Imports import (QDialog, QVBoxLayout, QLabel, QTabWidget, QWidget, QMessageBox, QPushButton, QHBoxLayout,
QComboBox, Qt, QEvent, QFont, QMouseEvent, json, QLineEdit, QApplication, QProgressDialog,
QObject, pyqtSignal, QTimer, sys, os, subprocess, time)
from rpi_autodiscovery import RPiAutoDiscovery, RPiConnectionWizard

models = ["RPI pico/pico W", "RPI zero/zero W", "RPI 2 zero W", "RPI 1 model B/B+", "RPI 2 model B", "RPI 3 model B/B+", "RPI 4 model B", "RPI 5"]

class DetectionWorker(QObject):
    """Emits signals for thread-safe UI updates"""
    result_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, detect_func):
        super().__init__()
        self.detect_func = detect_func
    
    def run(self):
        """Run in background thread"""
        try:
            result = self.detect_func()
            self.result_ready.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))

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

    reload_requested = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_canvas = parent
        self.is_hidden = True
        self.state_manager = Utils.state_manager
        self.translation_manager = Utils.translation_manager
        self.t = self.translation_manager.translate
        self.setup_ui()
    
    @classmethod
    def get_instance(cls, parent):
        """Get or create singleton instance"""
        if cls._instance is not None:
            try:
                _ = cls._instance.isVisible()
                if not cls._instance.is_hidden:
                    if cls._instance.parent_canvas != parent:
                        cls._instance.parent_canvas = parent
                    return cls._instance
            except RuntimeError:
                cls._instance = None
            
            except Exception as e:
                print(f"Error accessing existing DeviceSettingsWindow instance: {e}")
                cls._instance = None
        
        if cls._instance is None:
            cls._instance = cls(parent)
        return cls._instance
    
    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle(self.t("setting_window.title"))
        self.resize(400, 300)
        self.setWindowFlags(Qt.WindowType.Window)
    
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
        
        self.create_basic_tab()
        self.create_device_tab()
        self.create_rpi_settings_section()
    
    def create_basic_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setSpacing(5)

        title = QLabel(self.t("setting_window.basic_settings_tab.title"))
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab_layout.addWidget(title)

        tab_layout.addSpacing(10)

        label = QLabel(self.t("setting_window.basic_settings_tab.select_language"))
        tab_layout.addWidget(label)

        self.language_combo = MaxWidthComboBox(self, max_popup_width=358)

        languages = self.translation_manager.get_available_languages()
        for lang_code, name in languages.items():
            self.language_combo.addItem(name, lang_code)

        current_lang = Utils.app_settings.language
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        tab_layout.addWidget(label)
        tab_layout.addWidget(self.language_combo)
        tab_layout.addStretch()
        self.tab_widget.addTab(tab, self.t("setting_window.basic_settings_tab.title"))

    def create_device_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setSpacing(5)
        
        title = QLabel(self.t("setting_window.device_settings_tab.title"))
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab_layout.addWidget(title)
        
        tab_layout.addSpacing(10)
        
        label = QLabel(self.t("setting_window.device_settings_tab.select_rpi_model"))
        tab_layout.addWidget(label)
        
        self.rpi_model_combo = MaxWidthComboBox(self, max_popup_width=358)
        self.rpi_model_combo.addItems(models)
        self.rpi_model_combo.setCurrentIndex(Utils.app_settings.rpi_model_index if hasattr(Utils.app_settings, 'rpi_model_index') else 0)
        self.rpi_model_combo.currentIndexChanged.connect(self.on_model_changed)
        
        rpi_host_label = QLabel(self.t("setting_window.device_settings_tab.rpi_host"))
        self.rpi_host_input = QLineEdit()
        self.rpi_host_input.setText(Utils.app_settings.rpi_host)
        self.rpi_host_input.setPlaceholderText(self.t("setting_window.device_settings_tab.rpi_host_placeholder"))

        rpi_user_label = QLabel(self.t("setting_window.device_settings_tab.rpi_user"))
        self.rpi_user_input = QLineEdit()
        self.rpi_user_input.setText(Utils.app_settings.rpi_user)
        self.rpi_user_input.setPlaceholderText("pi")

        rpi_password_label = QLabel(self.t("setting_window.device_settings_tab.rpi_password"))
        self.rpi_password_input = QLineEdit()
        self.rpi_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.rpi_password_input.setPlaceholderText(self.t("setting_window.device_settings_tab.rpi_password_placeholder"))

        # Add to layout and connect save signals
        self.rpi_host_input.textChanged.connect(lambda text: self.save_settings())
        self.rpi_user_input.textChanged.connect(lambda text: self.save_settings())
        self.rpi_password_input.textChanged.connect(lambda text: self.save_settings())
        
        tab_layout.addWidget(self.rpi_model_combo)
        tab_layout.addWidget(rpi_host_label)
        tab_layout.addWidget(self.rpi_host_input)
        tab_layout.addWidget(rpi_user_label)
        tab_layout.addWidget(self.rpi_user_input)
        tab_layout.addWidget(rpi_password_label)
        tab_layout.addWidget(self.rpi_password_input)
        tab_layout.addStretch()
        self.tab_widget.addTab(tab, self.t("setting_window.device_settings_tab.title"))
    
    def on_model_changed(self, index):
        """Handle model change"""
        Utils.app_settings.rpi_model = self.rpi_model_combo.itemText(index)
        Utils.app_settings.rpi_model_index = index
        #print(f"Model changed to: {Utils.app_settings.rpi_model}")
    
    def create_rpi_settings_section(self):
        """Create RPI connection settings group"""
        tab = QWidget()
        self.main_layout = QVBoxLayout(tab)
        # Title
        rpi_title = QLabel(self.t("setting_window.rpi_settings_tab.title"))
        rpi_title.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.main_layout.addWidget(rpi_title)
        
        # Auto-Detect Button
        auto_detect_btn = QPushButton(self.t("setting_window.rpi_settings_tab.auto_detect"))
        auto_detect_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F538D;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2667B3;
            }
        """)
        auto_detect_btn.clicked.connect(self.auto_detect_rpi)
        self.main_layout.addWidget(auto_detect_btn)
        
        # Status label
        self.rpi_status_label = QLabel(self.t("setting_window.rpi_settings_tab.status_not_connected"))
        self.rpi_status_label.setStyleSheet("color: #FF9800; font-size: 10px;")
        self.main_layout.addWidget(self.rpi_status_label)
        
        # Manual settings (fallback)
        manual_label = QLabel(self.t("setting_window.rpi_settings_tab.manual_entry"))
        manual_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.main_layout.addWidget(manual_label)
        
        # Host input
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel(self.t("setting_window.rpi_settings_tab.rpi_host")))
        self.rpi_host_input = QLineEdit()
        self.rpi_host_input.setText(Utils.app_settings.rpi_host)
        self.rpi_host_input.setPlaceholderText(self.t("setting_window.rpi_settings_tab.rpi_host_placeholder"))
        self.rpi_host_input.textChanged.connect(lambda: setattr(Utils.app_settings, 'rpi_host', self.rpi_host_input.text()))
        host_layout.addWidget(self.rpi_host_input)
        self.main_layout.addLayout(host_layout)
        
        # Username input
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel(self.t("setting_window.rpi_settings_tab.rpi_user")))
        self.rpi_user_input = QLineEdit()
        self.rpi_user_input.setText(Utils.app_settings.rpi_user)
        self.rpi_user_input.setPlaceholderText(self.t("setting_window.rpi_settings_tab.rpi_user_placeholder"))
        self.rpi_user_input.textChanged.connect(lambda: setattr(Utils.app_settings, 'rpi_user', self.rpi_user_input.text()))
        user_layout.addWidget(self.rpi_user_input)
        self.main_layout.addLayout(user_layout)
        
        # Password input
        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(QLabel(self.t("setting_window.rpi_settings_tab.rpi_password")))
        self.rpi_password_input = QLineEdit()
        self.rpi_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.rpi_password_input.setText(Utils.app_settings.rpi_password)
        self.rpi_password_input.setPlaceholderText(self.t("setting_window.rpi_settings_tab.rpi_password_placeholder"))
        self.rpi_password_input.textChanged.connect(lambda: setattr(Utils.app_settings, 'rpi_password', self.rpi_password_input.text()))
        pwd_layout.addWidget(self.rpi_password_input)
        self.main_layout.addLayout(pwd_layout)
        self.tab_widget.addTab(tab, self.t("setting_window.rpi_settings_tab.title"))
    
    def save_settings(self):
        
        filename = os.path.join(Utils.get_base_path(), 'app_settings.json')

        app_settings_dict = self.build_save_data()

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(app_settings_dict, f, indent=2)
        
        print("Settings saved.")

    def build_save_data(self):
        data = {
            'rpi_model': Utils.app_settings.rpi_model,
            'rpi_model_index': Utils.app_settings.rpi_model_index,
            'rpi_host': Utils.app_settings.rpi_host,
            'rpi_user': Utils.app_settings.rpi_user,
            'rpi_password': Utils.app_settings.rpi_password,
            'language': Utils.app_settings.language
        }
        return data

    def on_language_changed(self):
        lang_code = self.language_combo.currentData()
        self.translation_manager.set_language(lang_code)
        Utils.app_settings.language = lang_code
        self.save_settings()

        self.reload_requested.emit(True)
    

    def auto_detect_rpi(self):
        """Auto-detect Raspberry Pi on network"""
        #print("🔍 Starting auto-detection...")
        self.lower()
        self.process = QProgressDialog(self.t("setting_window.auto_detect_dialog.process"), self.t("setting_window.auto_detect_dialog.cancel"), 0, 0, self)
        self.process.setWindowModality(Qt.WindowModality.WindowModal)
        self.process.show()
        
        try:
            def detect():
                result = RPiConnectionWizard.auto_detect_rpi()
                #print("🔍 Auto-detection result:", result)
                return result
            
            # Create worker
            self.worker = DetectionWorker(detect)
            
            # Connect signals to slots (these run on main thread!)
            self.worker.result_ready.connect(self._on_detection_success)
            self.worker.error_occurred.connect(self._on_detection_error)
            
            # Create thread
            import threading
            thread = threading.Thread(target=self.worker.run, daemon=True)
            thread.start()
            
            #print("Starting auto-detection thread...")
        
        except Exception as e:
            print(f"❌ Error starting thread: {e}")
            self.process.cancel()
            self.lower()
            QMessageBox.critical(
                self,
                self.t("setting_window.auto_detect_dialog.detection_error_title"),
                self.t("setting_window.auto_detect_dialog.detection_error_message"),
                QMessageBox.StandardButton.Ok
            )
            self.raise_()


    def _on_detection_success(self, result):
        """SLOT - Called on main thread when detection succeeds"""
        #print("🔍 Detection completed on main thread")
        
        try:
            # Validate result
            if result is None:
                #print("No Raspberry Pi found")
                self.rpi_status_label.setText(self.t("setting_window.rpi_settings_tab.status_not_detected"))
                self.rpi_status_label.setStyleSheet("color: #F44336; font-size: 10px;")
                self.lower()
                self.process.cancel()
                QMessageBox.warning(
                    self, self.t("setting_window.auto_detect_dialog.fail_title"),
                    self.t("setting_window.auto_detect_dialog.fail_message"),
                    QMessageBox.StandardButton.Ok
                )
                self.raise_()
                return
            
            # Validate result is a dict
            if not isinstance(result, dict):
                #print(f"Invalid result type: {type(result)}")
                self._on_detection_error(self.t("setting_window.auto_detect_dialog.invalid_result"))
                return
            
            if 'ip' not in result or 'hostname' not in result:
                #print("❌ Result missing required keys")
                self.rpi_status_label.setText(self.t("setting_window.rpi_settings_tab.status_incomplete"))
                self.rpi_status_label.setStyleSheet("color: #F44336; font-size: 10px;")
                self.lower()
                self.process.cancel()
                QMessageBox.critical(
                    self,
                    self.t("setting_window.auto_detect_dialog.incomplete_error_title"),
                    self.t("setting_window.auto_detect_dialog.incomplete_error_message"),
                    QMessageBox.StandardButton.Ok
                )
                self.raise_()
                return
            
            # Extract values
            ip = str(result.get('ip', ''))
            hostname = str(result.get('hostname', self.t("setting_window.rpi_settings_tab.unknown_hostname")))
            username = str(result.get('username', 'pi'))
            password = str(result.get('password', ''))
            model = str(result.get('model', self.t("setting_window.rpi_settings_tab.unknown_model")))
            
            #print(f"✓ Got valid result - IP: {ip}, User: {username}")
            
            # Block signals and update UI
            self.rpi_host_input.blockSignals(True)
            self.rpi_user_input.blockSignals(True)
            self.rpi_password_input.blockSignals(True)
            
            self.rpi_host_input.setText(ip)
            self.rpi_user_input.setText(username)
            self.rpi_password_input.setText(password)
            
            self.rpi_host_input.blockSignals(False)
            self.rpi_user_input.blockSignals(False)
            self.rpi_password_input.blockSignals(False)
            
            #print("✓ Updated UI fields")
            
            # Update settings
            Utils.app_settings.rpi_host = ip
            Utils.app_settings.rpi_user = username
            Utils.app_settings.rpi_password = password
            Utils.app_settings.rpi_model_name = model
            Utils.app_settings.auto_detected = True
            
            #print("✓ Updated settings")
            
            # Update status
            status_text = (self.t("setting_window.rpi_settings_tab.status_connected").format(hostname=hostname, ip=ip, model=model))
            self.rpi_status_label.setText(status_text)
            self.rpi_status_label.setStyleSheet("color: #4CAF50; font-size: 10px;")
            
            #print("✓ Updated status label")
            self.process.cancel()
            # Show success message
            self.lower()
            QMessageBox.information(
                self,
                self.t("setting_window.auto_detect_dialog.success_title"),
                self.t("setting_window.auto_detect_dialog.success_message").format(hostname=hostname, ip=ip, model=model),
                QMessageBox.StandardButton.Ok
            )
            self.raise_()
            
            #print("✓✓✓ Auto-detection completed successfully ✓✓✓\n")
        
        except Exception as e:
            print(f"❌ Exception: {type(e).__name__}: {e}")
            self._on_detection_error(str(e))


    def _on_detection_error(self, error_msg):
        """SLOT - Called on main thread when detection fails"""
        print(f"❌ Detection error: {error_msg}")
        
        self.rpi_status_label.setText(self.t("setting_window.rpi_settings_tab.status_error"))
        self.rpi_status_label.setStyleSheet("color: #F44336; font-size: 10px;")
        
        self.lower()
        self.process.cancel()
        QMessageBox.critical(
            self,
            self.t("setting_window.auto_detect_dialog.detection_error_title"),
            self.t("setting_window.auto_detect_dialog.detection_error_message"),
            QMessageBox.StandardButton.Ok
        )
        self.raise_()
    
    def open(self):
        print("Opening DeviceSettingsWindow")
        if self.is_hidden:
            print("DeviceSettingsWindow already open, raising to front")
            self.is_hidden = False
            self.show()
            self.raise_()
            self.activateWindow()
        return self

    def closeEvent(self, event):
        """Handle close event"""
        self.is_hidden = True
        self.state_manager.app_state.on_settings_dialog_close()
        event.accept()