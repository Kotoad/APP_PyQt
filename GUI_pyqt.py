from os import name
from random import random
from Imports import (
    sys, QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, threading,
    QMenuBar, QMenu, QPushButton, QLabel, QFrame, QScrollArea, QListWidget,
    QLineEdit, QComboBox, QDialog, QPainter, QPen, QColor, QBrush, pyqtProperty,
    QPropertyAnimation, QEasingCurve, QStyledItemDelegate, os, QThread, paramiko,
    QPalette, QMouseEvent, QRegularExpression, QRegularExpressionValidator, time,
    QTimer, QMessageBox, QInputDialog, QFileDialog, QFont, Qt, QPoint, ctypes,
    QRect, QSize, pyqtSignal, AppSettings, ProjectData, QCoreApplication, QSizePolicy,
    QAction, math, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPathItem,
    QGraphicsItem, QPointF, QRectF, QPixmap, QImage, QGraphicsPixmapItem, QPainterPath, QEvent,
    QStackedWidget, QSplitter, QIcon
)
import typing
from PyQt6 import QtGui
from Imports import (
    get_code_compiler, get_spawn_elements, get_device_settings_window,
    get_file_manager, get_path_manager, get_Elements_Window, get_utils,
    get_Help_Window, get_State_Manager, get_CodeViewer_Window
)
Utils = get_utils()
Code_Compiler = get_code_compiler()
BlockGraphicsItem = get_spawn_elements()[0]
spawningelements = get_spawn_elements()[1]
elementevents = get_spawn_elements()[2]
DeviceSettingsWindow = get_device_settings_window()
FileManager = get_file_manager()
PathManager = get_path_manager()[0]
PathGraphicsItem = get_path_manager()[1]
ElementsWindow = get_Elements_Window()
HelpWindow = get_Help_Window()
StateManager = get_State_Manager()
CodeViewerWindow = get_CodeViewer_Window()
    
#MARK: - RPiExecutionThread
class RPiExecutionThread(QThread):
    """
    Background thread for executing code on Raspberry Pi via SSH.
    
    This thread can be stopped gracefully from the main GUI thread.
    """
    
    # Signals emitted to main GUI
    finished = pyqtSignal()  # Execution completed successfully
    error = pyqtSignal(str)  # Execution error
    output = pyqtSignal(str)  # Command output
    status = pyqtSignal(str)  # Status messages
    execution_completed = pyqtSignal(bool)  # Success/failure status
    
    def __init__(self, ssh_config):
        """
        Initialize the execution thread.
        
        Args:
            ssh_config: dict with keys: filepath, rpi_host, rpi_user, rpi_password
        """
        super().__init__()
        self.ssh_config = ssh_config
        self.should_stop = False  # Flag to stop execution
        self.ssh = None  # SSH connection reference
        self.channel = None  # SSH channel reference
        self.stop_lock = threading.Lock()  # Thread-safe stop flag
    
    def stop(self):
        """
        Signal thread to stop gracefully.
        This is called from the main GUI thread.
        """
        print("[RPiExecutionThread] ⚠️  Stop signal received")
        
        with self.stop_lock:
            self.should_stop = True
        
        # CRITICAL: Close SSH connection immediately to interrupt blocking operations
        if self.ssh is not None:
            try:
                print("[RPiExecutionThread] 🔌 Closing SSH connection...")
                self.ssh.close()
            except Exception as e:
                print(f"[RPiExecutionThread] Error closing SSH: {e}")
        
        # Close channel if it exists
        if self.channel is not None:
            try:
                print("[RPiExecutionThread] 🔌 Closing SSH channel...")
                self.channel.close()
            except Exception as e:
                print(f"[RPiExecutionThread] Error closing channel: {e}")
    
    def should_continue(self):
        """
        Thread-safe check if execution should continue.
        Use this instead of checking self.should_stop directly.
        """
        with self.stop_lock:
            return not self.should_stop
    
    def run(self):
        """
        Main execution method. This runs in background thread.
        """
        try:
            # ===== STEP 1: Check if stop was called before execution =====
            if not self.should_continue():
                self.status.emit("⏹️  Execution cancelled before start")
                return
            
            # ===== STEP 2: Connect to RPi =====
            self.status.emit("🔌 Connecting to RPi...")
            
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh = ssh  # Store reference for cleanup
                
                # Set timeout for connection attempt
                ssh.connect(
                    self.ssh_config['rpi_host'],
                    username=self.ssh_config['rpi_user'],
                    password=self.ssh_config['rpi_password'],
                    timeout=10,  # Connection timeout
                    allow_agent=False,
                    look_for_keys=False
                )
            except Exception as e:
                self.error.emit(f"Failed to connect to RPi: {str(e)}")
                self.execution_completed.emit(False)
                return
            
            # ===== STEP 3: Check if stop was called during connection =====
            if not self.should_continue():
                ssh.close()
                self.status.emit("⏹️  Execution cancelled during connection")
                return
            
            self.status.emit("✓ Connected to RPi")
            
            # ===== STEP 4: Upload file via SFTP =====
            try:
                self.status.emit("📤 Uploading File.py...")
                sftp = ssh.open_sftp()
                
                # Get home directory
                stdin, stdout, stderr = ssh.exec_command("echo $HOME")
                home_dir = stdout.read().decode().strip()
                if not home_dir:
                    home_dir = f"/home/{self.ssh_config['rpi_user']}"
                
                remote_path = f"{home_dir}/File.py"
                
                # ===== STEP 5: Check if stop was called before upload =====
                if not self.should_continue():
                    sftp.close()
                    ssh.close()
                    self.status.emit("⏹️  Execution cancelled before upload")
                    return
                
                # Upload file
                sftp.put(self.ssh_config['filepath'], remote_path)
                sftp.close()
                
                self.status.emit(f"✓ Uploaded to {remote_path}")
            
            except Exception as e:
                self.error.emit(f"Failed to upload file: {str(e)}")
                self.execution_completed.emit(False)
                ssh.close()
                return
            
            # ===== STEP 6: Check if stop was called before execution =====
            if not self.should_continue():
                ssh.close()
                self.status.emit("⏹️  Execution cancelled before code execution")
                return
            
            # ===== STEP 7: Execute code on RPi =====
            self.status.emit("🔪 Killing old processes...")

            self.kill_process(ssh)
            # Check if stop was called while killing
            if not self.should_continue():
                ssh.close()
                self.status.emit("⏹️  Execution stopped by user")
                self.execution_completed.emit(False)
                return

            # Give the old process time to die
            time.sleep(0.5)

            self.status.emit("🚀 Executing code...")
            
            
            try:
                # Execute Python file with timeout
                stdin, stdout, stderr = ssh.exec_command(
                    f"python3 {remote_path}",
                    timeout=30  # Overall timeout for command
                )
                
                # Store channel for potential interruption
                self.channel = stdout.channel
                
                # ===== CRITICAL: Non-blocking read with stop checks =====
                # Wait for command completion while checking stop flag
                
                while not stdout.channel.exit_status_ready():
                    # Check if stop was called (every 100ms)
                    if not self.should_continue():
                        # Close channel to interrupt remote process
                        try:
                            stdout.channel.close()
                            ssh.close()
                        except:
                            pass
                        return
                    
                    # Check timeout
                    
                    # Sleep briefly to avoid busy-waiting
                    time.sleep(0.1)
                
                # Get exit code
                exit_code = stdout.channel.recv_exit_status()
                
                # ===== STEP 8: Check if stop was called during execution =====
                if not self.should_continue():
                    ssh.close()
                    self.status.emit("⏹️  Execution cancelled after completion")
                    return
                
                # Read output with timeout
                output = ""
                error_output = ""
                
                try:
                    # Set a read timeout
                    stdout.channel.settimeout(5)
                    output = stdout.read().decode('utf-8', errors='ignore')
                except:
                    pass
                
                try:
                    stderr.channel.settimeout(5)
                    error_output = stderr.read().decode('utf-8', errors='ignore')
                except:
                    pass
                
                # Close SSH connection
                ssh.close()
                
                # ===== STEP 9: Handle results =====
                if exit_code == 0:
                    self.status.emit("✓ Execution successful!")
                    if output:
                        self.output.emit(f"Output:\n{output}")
                    self.execution_completed.emit(True)
                    self.finished.emit()
                else:
                    self.status.emit(f"✗ Execution failed (exit code: {exit_code})")
                    self.error.emit(f"Execution failed:\n{error_output}")
                    self.execution_completed.emit(False)
            
            except Exception as e:
                if self.should_continue():  # Only report error if not stopped by user
                    self.error.emit(f"Execution error: {str(e)}")
                    self.execution_completed.emit(False)
                try:
                    ssh.close()
                except:
                    pass
        
        except Exception as e:
            if self.should_continue():
                self.error.emit(f"Thread error: {str(e)}")
                self.execution_completed.emit(False)

    def kill_process(self, ssh):
        try:
            # Kill any existing python processes that might be running old code
            # This ensures old code stops before new code starts
            kill_command = "pkill -f 'python3.*File.py' || true"
            stdin, stdout, stderr = ssh.exec_command(kill_command, timeout=5)
            kill_status = stdout.channel.recv_exit_status()
            print(f"[RPiExecutionThread] Kill command executed (exit code: {kill_status})")
        except Exception as e:
            print(f"[RPiExecutionThread] Warning: Could not kill old processes: {e}")


class GridScene(QGraphicsScene):
    def __init__(self, grid_size=25):
        super().__init__()
        self.grid_size = grid_size
        self.grid_color = QColor("#3A3A3A")
        self.grid_pen = QPen(self.grid_color, 1)
    
    def drawBackground(self, painter, rect):
        """
        Draw grid only for visible area - HUGE performance improvement!
        Called automatically by Qt when rendering, and only for visible region
        """
        super().drawBackground(painter, rect)
        
        # Only draw grid lines within the visible rect
        # This means only ~10-30 lines needed instead of 160,000
        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)
        right = int(rect.right())
        bottom = int(rect.bottom())
        
        painter.setPen(self.grid_pen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        # Draw vertical lines
        x = left
        while x < right:
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
            x += self.grid_size
        
        # Draw horizontal lines
        y = top
        while y < bottom:
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            y += self.grid_size
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

class CustomSwitch(QWidget):
    """
    YOUR CustomSwitch - Has FULL control over circle size!
    """
    
    toggled = pyqtSignal(bool)
    clicked = pyqtSignal(bool)
    
    def __init__(self, parent=None, 
                 width=80, height=40,
                 bg_off_color="#e0e0e0",
                 bg_on_color="#4CAF50",
                 circle_color="#ffffff",
                 border_color="#999999",
                 animation_speed=300):
        super().__init__(parent)
        
        # State management
        self._is_checked = False
        self._circle_x = 0.0
        self._is_enabled = True
        
        self.base_width = width
        self.base_height = height
        self.circle_diameter = height - 8 
        self.padding = 4
        self.border_width = 2
        
        # Color configuration
        self.bg_off_color = bg_off_color
        self.bg_on_color = bg_on_color
        self.circle_color = circle_color
        self.border_color = border_color
        self.disabled_alpha = 0.5
        
        # Animation setup
        self.animation = QPropertyAnimation(self, b"circle_x")
        self.animation.setDuration(animation_speed)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._is_animating = False
        self.animation.stateChanged.connect(self.animation_state_changed)
        
        # Widget configuration
        self.setFixedSize(self.base_width, self.base_height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Initialize circle position
        self._update_circle_position(animate=False)
    
    @pyqtProperty(float)
    def circle_x(self):
        return self._circle_x
    
    @circle_x.setter
    def circle_x(self, value):
        self._circle_x = value
        self.update()
    
    def animation_state_changed(self, state):
        from PyQt6.QtCore import QAbstractAnimation
    
        if state == QAbstractAnimation.State.Running:
            self._is_animating = True
        else:  # Stopped
            self._is_animating = False

    
    def on_switch_changed(self):
        return self._is_checked
    
    def set_checked(self, state, emit_signal=True):
        if self._is_checked != state:
            self._is_checked = state
            self._update_circle_position(animate=True)
            if emit_signal:
                self.toggled.emit(self._is_checked)
            self.clicked.emit(self._is_checked)
    
    def toggle(self):
        self.set_checked(not self._is_checked)
    
    def set_enabled_custom(self, enabled):
        self._is_enabled = enabled
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if enabled 
            else Qt.CursorShape.ForbiddenCursor
        )
        self.update()
    
    def _update_circle_position(self, animate=True):
        if self._is_checked:
            end_pos = self.base_width - self.circle_diameter - self.padding
        else:
            end_pos = self.padding
        
        if animate:
            self.animation.setStartValue(self._circle_x)
            self.animation.setEndValue(end_pos)
            self.animation.start()
        else:
            self._circle_x = end_pos
    
    def mousePressEvent(self, event):
        if self._is_animating:
            event.ignore()
            return
        
        if event.button() == Qt.MouseButton.LeftButton and self._is_enabled:
            self.toggle()
    
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.update()
    
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self._is_enabled:
            painter.setOpacity(self.disabled_alpha)
        
        radius = self.base_height / 2
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.base_width, self.base_height, radius, radius)
        painter.setClipPath(path)

        # 2) BACKGROUND: USE SAME OUTER RECT (NO INSET)
        bg_rect = QRectF(0, 0, self.base_width, self.base_height)
        bg_color = QColor(self.bg_on_color if self._is_checked else self.bg_off_color)
        painter.fillRect(bg_rect, bg_color)

        # 3) BORDER: DRAW ON SAME RECT & RADIUS
        border_pen = QPen(QColor(self.border_color), self.border_width)
        painter.setPen(border_pen)
        painter.drawRoundedRect(bg_rect, radius, radius)

        # 4) FOCUS RECT: SLIGHTLY INSET, SAME SHAPE
        if self.hasFocus():
            focus_pen = QPen(QColor("#2196f3"), 2, Qt.PenStyle.SolidLine)
            painter.setPen(focus_pen)
            focus_margin = 2
            focus_rect = QRectF(
                focus_margin,
                focus_margin,
                self.base_width - 2 * focus_margin,
                self.base_height - 2 * focus_margin,
            )
            painter.drawRoundedRect(focus_rect, radius - focus_margin, radius - focus_margin)

        # 5) CIRCLE
        circle_rect = QRectF(
            self._circle_x,
            self.padding,
            self.circle_diameter,
            self.circle_diameter,
        )
        painter.setBrush(QBrush(QColor(self.circle_color)))
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.drawEllipse(circle_rect)

        shadow_pen = QPen(QColor("#000000"), 1)
        shadow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(shadow_pen)
        painter.setOpacity(0.15)
        painter.drawEllipse(circle_rect.adjusted(1, 1, 1, 1))

class PassiveListPopup(QListWidget):
    """
    A list widget designed to float as a tool window without stealing focus.
    """
    selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        # 1. Window Flags: Tool (no taskbar) + Frameless + Always on Top
        self.setWindowFlags(
            Qt.WindowType.Tool | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # 2. Attribute: Tell Qt NOT to activate this window when showing it
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # 3. Focus Policy: logical focus should never be here
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Styling
        self.setStyleSheet("""
            QListWidget { 
                border: 1px solid gray; 
                background: white; 
                font-size: 10px;
                color: #000000;
            }
            QListWidget::item:selected { 
                background: #0078d7; 
                color: white; 
            }
            QScrollBar:horizontal {
                height: 0px;
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                width: 0px;
                border: none;
                background: transparent;
            }
        """)
        
        # Handle item clicks
        self.itemClicked.connect(self._on_item_clicked)
        
        # Install global filter to handle clicking outside
        QApplication.instance().installEventFilter(self)

    def showEvent(self, event):
        # Windows-specific fix to prevent activation on click
        if sys.platform == "win32":
            self._apply_windows_no_activate()
        super().showEvent(event)

    def _apply_windows_no_activate(self):
        # Set WS_EX_NOACTIVATE (0x08000000)
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        try:
            hwnd = int(self.winId())
            user32 = ctypes.windll.user32
            # Handle 64-bit vs 32-bit API naming
            set_window_long = user32.SetWindowLongPtrW if hasattr(user32, "SetWindowLongPtrW") else user32.SetWindowLongW
            get_window_long = user32.GetWindowLongPtrW if hasattr(user32, "GetWindowLongPtrW") else user32.GetWindowLongW
            
            ex_style = get_window_long(hwnd, GWL_EXSTYLE)
            set_window_long(hwnd, GWL_EXSTYLE, ex_style | WS_EX_NOACTIVATE)
        except Exception:
            pass

    def eventFilter(self, source, event):
        # Close popup if user clicks anywhere else
        if self.isVisible() and event.type() == QEvent.Type.MouseButtonPress:
            global_pos = event.globalPosition().toPoint()
            # If click is NOT inside the popup, close it.
            # Note: We don't check the LineEdit here because the LineEdit will 
            # likely have its own logic or just keep focus naturally.
            if not self.geometry().contains(global_pos):
                self.hide()
        return super().eventFilter(source, event)

    def _on_item_clicked(self, item):
        self.selected.emit(item.text())
        self.hide()


class SearchableLineEdit(QLineEdit):
    """
    A QLineEdit that mimics a ComboBox. 
    It manages a passive popup list that filters based on input.
    """
    
    selected = pyqtSignal(str)
    MAX_WIDTH = 245  # Max width for popup
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.popup = PassiveListPopup()
        self.popup.selected.connect(self.set_text_and_hide)
        
        self.setStyleSheet("""
        QLineEdit {
            background-color: white;
            border: 1px solid #333;
            border-radius: 3px;
            font-size: 10px;
            color: #333;
        }
        """)
        self.all_items = []
        
        # Connect typing events
        self.textEdited.connect(self.update_popup)
        
        self.setFixedWidth(self.MAX_WIDTH)  # Optional: set a fixed width for the line edit

    def addItem(self, text):
        self.all_items.append(str(text))

    def addItems(self, texts):
        self.all_items.clear()
        self.all_items.extend([str(t) for t in texts])
        #print(f"All items added: {self.all_items}")

    def set_text_and_hide(self, text):
        self.setText(text)
        self.popup.hide()

    def update_popup(self, text):
        """Filter items and show popup."""
        self.popup.clear()
        
        if not text:
            self.popup.hide()
            return

        # Simple case-insensitive filter
        filtered = [item for item in self.all_items if text.lower() in item.lower()]
        
        if not filtered:
            self.popup.hide()
            return

        self.popup.addItems(filtered)
        
        # Select the first item by default for easy navigation
        self.popup.setCurrentRow(0)
        
        # Position the popup
        self._move_popup()
        self.popup.show()

    def _move_popup(self):
        """Align popup geometry to the bottom of the line edit."""
        rect = self.rect()
        bottomleft = self.mapToGlobal(rect.bottomLeft())
        
        # Calculate popup width based on content (max 150px)
        fm = self.fontMetrics()
        max_text_width = 0
        for item_text in range(self.popup.count()):
            item = self.popup.item(item_text)
            if item:
                w = fm.horizontalAdvance(item.text())
                max_text_width = max(max_text_width, w)
        
        # Add padding and cap at max width
        popup_width = min(max_text_width + 20, self.MAX_WIDTH)
        popup_width = max(popup_width, 30)  # Minimum 30px
        
        self.popup.setFixedWidth(popup_width)  # ← Now dynamic!
        
        itemheight = self.popup.sizeHintForRow(0)
        #print(f"Item height: {itemheight}")
        count = self.popup.count()
        #print(f"Item count: {count}")
        h = min(count * itemheight, itemheight * 5)  # Max 5 items visible
        #print(f"Popup height: {h}")
        self.popup.setFixedHeight(h)
        self.popup.updateGeometry()
        self.popup.move(bottomleft)
        
    def keyPressEvent(self, event):
        """Forward navigation keys to the popup."""
        if not self.popup.isVisible():
            super().keyPressEvent(event)
            return

        if event.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up):
            # Forward arrow keys to list
            current_row = self.popup.currentRow()
            count = self.popup.count()
            
            if event.key() == Qt.Key.Key_Down:
                new_row = (current_row + 1) % count
            else:
                new_row = (current_row - 1 + count) % count
                
            self.popup.setCurrentRow(new_row)
            return
        
        elif event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            # Select current item on Enter
            if self.popup.currentItem():
                self.set_text_and_hide(self.popup.currentItem().text())
            return
        
        elif event.key() == Qt.Key.Key_Escape:
            self.popup.hide()
            return

        super().keyPressEvent(event)

#MARK: - GridCanvas
class GridCanvas(QGraphicsView):
    """Canvas widget using QGraphicsView for proper zoom/pan handling"""
    
    def __init__(self, parent=None, grid_size=25):
        super().__init__(parent)
        #print(f"Self in GridCanvas init: {self}")
        self.grid_size = grid_size
        elements_window = ElementsWindow.get_instance(self)
        self.spawner = spawningelements(self, elements_window)
        self.state_manager = StateManager.get_instance()
        self.path_manager = PathManager(self)
        self.elements_events = elementevents(self)
        self.file_manager = FileManager()
        
        # Create graphics scene
        self.scene = GridScene(grid_size=grid_size)  # ✅ Use custom scene
        self.scene.setSceneRect(-5000, -5000, 5000, 5000)
        self.setScene(self.scene)
        
        # Zoom setup
        self.zoom_level = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 4.0
        self.zoom_speed = 0.1
        
        # Rendering
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Pan mode - middle mouse button
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.middle_mouse_pressed = False
        self.middle_mouse_start = QPoint()
        
        # Tracking
        self.main_window = None
        self.dragged_widget = None
        self.offset_x = 0
        self.offset_y = 0
        
        # Style
        self.setStyleSheet("""
            GridCanvas {
                background-color: #2B2B2B;
            }
        """)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def draw_grid(self):
        """Draw grid background"""
        grid_size = self.grid_size
        scene_rect = self.scene.sceneRect()
        
        pen = QPen(QColor("#3A3A3A"), 1)
        
        # Vertical lines
        x = int(scene_rect.left())
        while x < scene_rect.right():
            self.scene.addLine(x, scene_rect.top(), x, scene_rect.bottom(), pen)
            x += grid_size
        
        # Horizontal lines
        y = int(scene_rect.top())
        while y < scene_rect.bottom():
            self.scene.addLine(scene_rect.left(), y, scene_rect.right(), y, pen)
            y += grid_size
    
    def wheelEvent(self, event):
        """Handle zoom with mouse wheel"""
        factor = 1.15
        if event.angleDelta().y() > 0:
            new_zoom = self.zoom_level * factor
        else:
            new_zoom = self.zoom_level / factor
        
        # Clamp to min/max
        new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))
        
        # Zoom toward mouse position
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.scale(new_zoom / self.zoom_level, new_zoom / self.zoom_level)
        self.zoom_level = new_zoom
        
        event.accept()
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        #print(f"[GridCanvas.keyPressEvent] Key: {event.key()}")
        if event.key() == Qt.Key.Key_Home:
            # Reset zoom and pan
            self.resetTransform()
            self.zoom_level = 1.0
            event.accept()
        #print(f"Spawner state: {self.spawner}, element_placed: {getattr(self.spawner, 'element_placed', None)}")
        if self.spawner and self.spawner.element_placed:
            #print(f"Key pressed: {event.key()}")
            #print(f"Element placed before: {self.spawner.element_placed}")
            if event.key() in [Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Enter]:
                self.spawner.stop_placing(self)
                event.accept()
            else:
                event.ignore()
        elif self.path_manager.start_node:
            print(f"Key pressed during path creation: {event.key()}")
            if event.key() == Qt.Key.Key_Escape:
                self.path_manager.cancel_connection()
                event.accept()
            else:
                event.ignore()
        else:
            super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press - check for middle-click panning"""
        #print(f"[GridCanvas.mousePressEvent] Button: {event.button()}")
        
        # Handle middle-click panning
        if event.button() == Qt.MouseButton.MiddleButton:
            #print("[GridCanvas] Middle mouse pressed - starting pan")
            self.middle_mouse_pressed = True
            self.middle_mouse_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        
        # Handle right-click context menu
        if event.button() == Qt.MouseButton.RightButton:
            #print("[GridCanvas] Right mouse pressed - checking for context menu")
            scene_pos = self.mapToScene(event.position().toPoint())
            items = self.scene.items(scene_pos)
            #print(f"[GridCanvas] Items under cursor: {items}")
            
            for item in items:
                #print(f"[GridCanvas] Checking item: {item}")
                if isinstance(item, BlockGraphicsItem):
                    #print(f"[GridCanvas] Showing block context menu")
                    self.show_block_context_menu(item, scene_pos)
                    event.accept()
                    return  # ← Return ONLY if we showed context menu
                elif isinstance(item, PathGraphicsItem):
                    print(f"[GridCanvas] Showing path context menu")
                    self.show_path_context_menu(item, scene_pos)
                    event.accept()
                    return  # ← Return ONLY if we showed context menu
            # ← If NO menu shown, fall through to super()
        
        # ✅ CRITICAL: Pass all other events to parent so blocks can receive them
        #print(f"[GridCanvas] Passing event to super() for block handling")
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move - pan if middle-mouse pressed"""
        if self.middle_mouse_pressed:
            # Middle-mouse is held down: pan using scroll bars instead of translate
            delta = event.pos() - self.middle_mouse_start
            
            # Use scrollbars to pan - this keeps everything in sync
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            
            self.middle_mouse_start = event.pos()
            event.accept()
        if self.path_manager.start_node:
            # Update preview path as mouse moves
            scene_pos = self.mapToScene(event.position().toPoint())
            self.path_manager.update_preview_path(scene_pos)
            event.accept()
        else:
            # Normal mouse movement
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release - end panning"""
        if event.button() == Qt.MouseButton.MiddleButton:
            # Release middle-click
            self.middle_mouse_pressed = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            # Other buttons
            super().mouseReleaseEvent(event)
    
    def add_block(self, block_type, x, y, block_id, name=None):
        """Add a new block to the canvas"""
        print(f"Adding block of type {block_type} at ({x}, {y}) with ID {block_id} to canvas {self}, name: {name if name else 'N/A'}")
        block = BlockGraphicsItem(
            x=x, y=y,
            block_id=block_id,
            block_type=block_type,
            parent_canvas=self,
            main_window=self.main_window,
            name=name
        )
        
        self.scene.addItem(block)

        # Store in Utils
        if block_type in ('If', 'While', 'Button'):
            info = {
                'type': block_type.split('_')[0],
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'value_1_name': None,
                'value_1_type': None,
                'value_2_name': None,
                'value_2_type': None,
                'operator': "==",
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == 'Timer':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'sleep_time': "1000",
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == 'Switch':
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'value_1_name': None,
                'switch_state': False,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type in ('Start', 'End', 'While_true'):
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == "Function":
            info = {
                'type': 'Function',
                'id': block_id,
                'name': name,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'internal_vars': {
                    'main_vars': {},
                    'ref_vars': {},
                },
                'internal_devs': {
                    'main_devs': {},
                    'ref_devs': {},
                },
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type in ("Basic_operations", "Exponential_operations", "Random_number"):
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'value_1_name': None,
                'value_1_type': None,
                'value_2_name': None,
                'value_2_type': None,
                'operator': None,
                'result_var_name': None,
                'result_var_type': None,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == "Blink_LED":
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'value_1_name': None,
                'value_1_type': None,
                'sleep_time': "1000",
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == "Toggle_LED":
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'value_1_name': None,
                'value_1_type': None,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        elif block_type == "PWM_LED":
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'value_1_name': None,
                'value_1_type': None,
                'PWM_value': "128",
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        else:
            print(f"Error: Unknown block type {block_type}")
            info = {
                'type': block_type,
                'id': block_id,
                'widget': block,
                'width': block.boundingRect().width(),
                'height': block.boundingRect().height(),
                'x': x,
                'y': y,
                'in_connections': {},
                'out_connections': {},
                'canvas': self
            }
        if self.reference == 'canvas':
            Utils.main_canvas['blocks'].setdefault(block_id, info)
        elif self.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                #print(f"Utils.functions key: {f_id}, value: {f_info}")
                if self == f_info.get('canvas'):
                    #print(f"Matched function canvas for block addition: {f_id}")
                    Utils.functions[f_id]['blocks'].setdefault(block_id, info)
                    break
        #print(f"Added block: {info}")
        if self.reference == 'canvas':
            #print(f"Current Utils.main_canvas blocks: {Utils.main_canvas['blocks']}")
            pass
        elif self.reference == 'function':
            #print(f"Current Utils.functions[{f_id}] blocks: {Utils.functions[f_id]['blocks']}")
            pass
        block.connect_graphics_signals()
        return block
    
    def clear_canvas(self):
        """Clear all blocks and paths from canvas"""
        #TODO: complete clearing logic
        self.scene.clear()
        Utils.top_infos.clear()
        Utils.paths.clear()
        self.draw_grid()
    
    def remove_block(self, block_id):
        """Remove a block from canvas"""
        try:
            current_canvas = self.main_window.current_canvas
            if not current_canvas:
                return
            
            reference = current_canvas.reference
            
            if reference == "canvas":
                block_data = Utils.main_canvas['blocks'].get(block_id)
                if block_data:
                    widget = block_data.get('widget')
                    if widget:
                        # ✅ Properly remove from scene
                        widget.setParent(None)
                        self.scene.removeItem(widget)
                        # ✅ Explicitly delete
                        widget.deleteLater()
                    
                    del Utils.main_canvas['blocks'][block_id]
            
            elif reference == "function":
                for fid, finfo in Utils.functions.items():
                    if current_canvas == finfo.get('canvas'):
                        block_data = Utils.functions[fid]['blocks'].get(block_id)
                        if block_data:
                            widget = block_data.get('widget')
                            if widget:
                                widget.setParent(None)
                                self.scene.removeItem(widget)
                                widget.deleteLater()
                            
                            del Utils.functions[fid]['blocks'][block_id]
                        break
        
        except Exception as e:
            print(f"Error removing block {block_id}: {e}")
            
    def remove_path(self, path_id):
        """Remove a path from canvas"""
        if self.main_window.current_canvas.reference == "canvas":
            paths = Utils.main_canvas.get('paths', {})
        elif self.main_window.current_canvas.reference == "function":
            for f_id, f_info in Utils.functions.items():
                if self.main_window.current_canvas == f_info.get('canvas'):
                    paths = Utils.functions[f_id].get('paths', {})
                    break
        print(f"paths {paths}")

        if path_id in paths:
            print(f"Removing path: {path_id}")
            path_item = paths[path_id].get('item')
            print(f"Path item to remove: {path_item}")
            if path_item:
                self.scene.removeItem(path_item)
                print(f"Path item {path_id} removed from scene.")
                out_part, in_part = path_id.split("-")
                print(f"Path connects {in_part} to {out_part}")
                if self.main_window.current_canvas.reference == "canvas":
                    if in_part in Utils.main_canvas['blocks']:
                        del Utils.main_canvas['blocks'][in_part]['in_connections'][path_id]
                    if out_part in Utils.main_canvas['blocks']:
                        del Utils.main_canvas['blocks'][out_part]['out_connections'][path_id]
                elif self.main_window.current_canvas.reference == "function":
                    for f_id, f_info in Utils.functions.items():
                        if self.main_window.current_canvas == f_info.get('canvas'):
                            if in_part in Utils.functions[f_id]['blocks']:
                                del Utils.functions[f_id]['blocks'][in_part]['in_connections'][path_id]
                            if out_part in Utils.functions[f_id]['blocks']:
                                del Utils.functions[f_id]['blocks'][out_part]['out_connections'][path_id]
                            break
                del paths[path_id]
    
    def show_block_context_menu(self, block, scene_pos):
        """Show context menu for blocks"""
        menu = QMenu(self)
        
        block_id = block.block_id
        
        edit_action = QAction("Edit Block", self)
        edit_action.triggered.connect(lambda: self.edit_block(block, block_id))
        menu.addAction(edit_action)
        
        duplicate_action = QAction("Duplicate", self)
        duplicate_action.triggered.connect(lambda: self.duplicate_block(block, block_id))
        menu.addAction(duplicate_action)
        
        inspector_action = QAction("Show Inspector", self)

        inspector_action.triggered.connect(lambda: self.main_window.toggle_inspector_frame(block))
        menu.addAction(inspector_action)
        
        menu.addSeparator()
        
        delete_action = QAction("Delete Block", self)
        delete_action.triggered.connect(lambda: self.delete_block(block, block_id))
        menu.addAction(delete_action)
        
        # Convert scene coords to screen coords
        screen_pos = self.mapToGlobal(self.mapFromScene(scene_pos))
        menu.exec(screen_pos)
    
    def show_path_context_menu(self, path, scene_pos):
        """Show context menu for paths"""
        menu = QMenu(self)
        
        delete_action = QAction("Delete Connection", self)
        delete_action.triggered.connect(lambda: self.delete_path(path))
        menu.addAction(delete_action)
        
        screen_pos = self.mapToGlobal(self.mapFromScene(scene_pos))
        menu.exec(screen_pos)
    
    def edit_block(self, block, block_id):
        """Edit block properties"""
        #print(f"Editing block: {block_id}")
    
    def duplicate_block(self, block, block_id):
        """Create a copy of a block"""
        #TODO : Implement duplication logic
        if block_id not in Utils.top_infos:
            return
        
        block_data = Utils.top_infos[block_id]
        x = block_data['x'] + 50
        y = block_data['y'] + 50
        #print(f"Duplicating block {block_id} at ({x}, {y})")
    
    def delete_block(self, block, block_id):
        """Delete a block and its connections"""
        #print(f"Deleting block: {block_id}")
        
        if self.path_manager:
            self.path_manager.remove_paths_for_block(block_id)
        
        self.remove_block(block_id)
    
    def delete_path(self, path):
        """Delete a connection path"""
        print(f"Deleting path: {path.path_id}")
        self.remove_path(path.path_id)
#MARK: - MainWindow
class MainWindow(QMainWindow):
    """Main application window"""
    
    tab_changed = pyqtSignal(int)
    
    @property
    def current_canvas(self):
        """Get the currently active canvas from the sidebar"""
        try:
            index = self.get_current_tab_index()
            for canvas, info in Utils.canvas_instances.items():
                #print(f"Canvas in Utils.canvas_instances: {canvas}, info: {info}")
                if info['index'] == index:
                    #print(f"✓ Found current canvas in Utils.canvas_instances: {canvas}")
                    widget = info['canvas']
            #print(f"Current sidebar tab index: {index}, widget: {widget}")
            
            # Check if it's a GridCanvas instance
            if isinstance(widget, GridCanvas):
                #print("✓ Current canvas found.")
                return widget
        except Exception as e:
            print(f"⚠️ Error getting current canvas: {e}")
        
        # Fallback to main canvas if property fails
        if hasattr(self, 'canvas') and self.canvas is not None:
            #print("✓ Using main canvas as fallback.")
            return self.canvas
        
        print("❌ No canvas available.")
        return None
        
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visual Programming Interface")
        self.setWindowIcon(QIcon('resources/images/APPicon.ico'))
        self.resize(1200, 800)
        self.code_compiler = Code_Compiler()
        self.state_manager = StateManager.get_instance()
        self.path_manager = PathManager(self)
        self.create_save_shortcut()
        self.setup_auto_save_timer()
        # Style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1F1F1F;
            }
            QMenuBar {
                background-color: #2B2B2B;
                color: #FFFFFF;
                border-bottom: 1px solid #3A3A3A;
                padding: 4px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 12px;
            }
            QMenuBar::item:selected {
                background-color: #1F538D;
            }
            QMenu {
                background-color: #2B2B2B;
                color: #FFFFFF;
                border: 1px solid #3A3A3A;
            }
            QMenu::item:selected {
                background-color: #1F538D;
            }

            QToolBar {
                background-color: #2B2B2B;
                border-bottom: 1px solid #3A3A3A;
            }
            
            QLineEdit {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px;
            }
            QComboBox {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px;
            }
        """)
        self.help_window_instance = None
        self.variable_frame = None
        self.variable_frame_visible = False
        self.variable_row_count = 1
        self.Devices_frame = None
        self.devices_frame_visible = False
        self.devices_row_count = 1
        self.last_canvas = None
        self.blockIDs = {}
        self.execution_thread = None
        self.canvas_added = None
        self.pages = {}
        self.page_count = 0
        self.count_w_separator = 0
        self.canvas_count = 0
        self.tab_buttons = []  # Track tab buttons
        self.last_m_dev = None
        self.last_m_var = None
        self.last_f_dev = None
        self.last_f_var = None
        self.last_type_var = None
        self.last_type_dev = None

        self.reset_file()

        self.create_menu_bar()
        self.create_toolbar()
        self.create_canvas_frame()
    
    def mousePressEvent(self, event):
        """Debug: Track if main window gets mouse press"""
        #print("⚠ MainWindow.mousePressEvent fired!")
        super().mousePressEvent(event)
    
    def reset_file(self):
        try:
            with open("File.py", "w") as f:
                f.write("")
        except Exception as e:
            print(f"Error resetting File.py: {e}")

    #MARK: - UI Creation Methods
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        #print(f"Menubar Height: {menubar.height()}")
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = file_menu.addAction("New")
        new_action.triggered.connect(self.on_new_file)
        
        open_action = file_menu.addAction("Open")
        open_action.triggered.connect(self.on_open_file)
        
        save_action = file_menu.addAction("Save")
        save_action.triggered.connect(self.on_save_file)
        
        save_as_action = file_menu.addAction("Save As")
        save_as_action.triggered.connect(self.on_save_file_as)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Elements menu
        elements_menu = menubar.addMenu("Elements")
        
        add_element = elements_menu.addAction("Add Element")
        add_element.triggered.connect(self.open_elements_window)
        
        # Variables menu
        view_menu = menubar.addMenu("View")

        canvas_action = view_menu.addAction("Show Canvas")
        canvas_action.triggered.connect(lambda: self.set_current_tab(0, 'canvas'))

        variables_action = view_menu.addAction("Show Variables")
        variables_action.triggered.connect(lambda: self.set_current_tab(1, 'variables'))

        devices_action = view_menu.addAction("Show Devices")
        devices_action.triggered.connect(lambda: self.set_current_tab(2, 'devices'))
        
        settings_menu = menubar.addMenu("Settings")
        settings_menu_action = settings_menu.addAction("Settings")
        settings_menu_action.triggered.connect(self.open_settings_window)
        
        Help_menu = menubar.addMenu("Help")
        
        Get_stared = Help_menu.addAction("Get Started")
        Get_stared.triggered.connect(lambda: self.open_help(0))
        
        examples = Help_menu.addAction("Examples")
        examples.triggered.connect(lambda: self.open_help(1))
        
        FAQ = Help_menu.addAction("FAQ")
        FAQ.triggered.connect(lambda: self.open_help(2))
        
        # Compile menu
        compile_menu = menubar.addMenu("Compile")
        
        compile_action = compile_menu.addAction("Compile Code")
        compile_action.triggered.connect(self.compile_and_upload)

        view_code_action = compile_menu.addAction("View Generated Code")
        view_code_action.triggered.connect(self.view_generated_code)
    
    def create_toolbar(self):

        icon_path = "resources/images/Tool_bar/"

        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))

        save_icon = QAction(QIcon(icon_path+"Save.png"), "Save", self)
        save_icon.triggered.connect(self.on_save_file)
        toolbar.addAction(save_icon)

        open_icon = QAction(QIcon(icon_path+"Open_file.png"), "Open", self)
        open_icon.triggered.connect(self.on_open_file)
        toolbar.addAction(open_icon)

        new_icon = QAction(QIcon(icon_path+"New_file.png"), "New", self)
        new_icon.triggered.connect(self.on_new_file)
        toolbar.addAction(new_icon)

        toolbar.addSeparator()

        add_block_icon = QAction(QIcon(icon_path+"Add_block.png"), "Add block", self)
        add_block_icon.triggered.connect(self.open_elements_window)
        toolbar.addAction(add_block_icon)

        toolbar.addSeparator()

        settings_icon = QAction(QIcon(icon_path+"Settings.png"), "Settings", self)
        settings_icon.triggered.connect(self.open_settings_window)
        toolbar.addAction(settings_icon)

        toolbar.addSeparator()

        run_and_compile_icon = QAction(QIcon(icon_path+"Run_and_compile.png"), "Compile and Upload", self)
        run_and_compile_icon.triggered.connect(self.compile_and_upload)
        toolbar.addAction(run_and_compile_icon)

        run_icon = QAction(QIcon(icon_path+"Run.png"), "Run", self)
        run_icon.triggered.connect(self.execute_on_rpi_ssh_background)
        toolbar.addAction(run_icon)

        stop_execution_icon = QAction(QIcon(icon_path+"Stop_execution.png"), "Stop Execution", self)
        stop_execution_icon.triggered.connect(self.stop_execution)
        toolbar.addAction(stop_execution_icon)

    def stop_execution(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_config = {
            'filepath': 'File.py',  # Your compiled file
            'rpi_host': Utils.app_settings.rpi_host,
            'rpi_user': Utils.app_settings.rpi_user,
            'rpi_password': Utils.app_settings.rpi_password,
        }
        
        self.execution_thread = RPiExecutionThread(ssh_config)

        self.execution_thread.kill_process(ssh)
    def create_canvas_frame(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.sidebar = self.create_sidebar()
        
        # Create a splitter for canvas + inspector
        
        self.canvas = GridCanvas()
        try:
            self.canvas.main_window = self
        except Exception as e:
            print(f"Error setting mainwindow on canvas: {e}")
        
        Utils.canvas_instances[self.canvas] = {
            'name': "Canvas",
            'canvas': self.canvas,
            'index': 0,
            'ref': 'canvas'
        }
        
        # Add splitter to main layout
        main_layout.addWidget(self.sidebar)
        
        # Rest of your code...
        self.add_tab(tab_name="Canvas", content_widget=self.canvas, reference="canvas")
        self.last_canvas = self.canvas
        self.tab_changed.connect(self.on_tab_changed)
        self.set_current_tab(0, 'canvas')
    
    def on_tab_changed(self, index):
        if index not in [info['index'] for info in Utils.canvas_instances.values()]:
            #print(f"Tab index {index} not in Utils.canvas_instances indices.")
            return
        if self.current_canvas != self.last_canvas:
            #print(f"Sidebar tab changed to index: {index}, widget: {self.current_canvas}")
            try:
                for canvas, info in Utils.canvas_instances.items():
                    canvas.var_button.hide()
                    canvas.dev_button.hide()
                    canvas.separator_container.hide()
                    if info['ref'] == 'canvas' or canvas == self.current_canvas:
                        #print("Showing variable and device buttons for main or current canvas.")
                        canvas.var_button.show()
                        canvas.dev_button.show()
                        canvas.separator_container.show()
            except Exception as e:
                print(f"Error showing/hiding buttons on tab change: {e}")
            self.last_canvas = self.current_canvas
            
    def create_variables_panel(self, canvas_reference=None):
        """Create Variables panel"""
        canvas_reference.variable_row_count = 0
        canvas_reference.widget = QWidget()
        canvas_reference.layout = QVBoxLayout(canvas_reference.widget)
        canvas_reference.layout.setContentsMargins(10, 10, 10, 10)
        
        header = QLabel("Variables")
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
        canvas_reference.layout.addWidget(header)
        
        add_btn = QPushButton("Add Variable")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F538D;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
        """)
        canvas_reference.layout.addWidget(add_btn)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        canvas_reference.var_content = QWidget()
        canvas_reference.var_layout = QVBoxLayout(canvas_reference.var_content)
        canvas_reference.var_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        canvas_reference.var_layout.addStretch()
        scroll.setWidget(canvas_reference.var_content)
        canvas_reference.layout.addWidget(scroll)
        add_btn.clicked.connect(lambda: self.add_variable_row(None, None, canvas_reference))
        canvas_reference.widget.setStyleSheet("""
            QWidget { background-color: #2B2B2B; }
        """)
        return canvas_reference.widget

    def create_devices_panel(self, canvas_reference=None):
        """Create Devices panel"""
        canvas_reference.devices_row_count = 0
        canvas_reference.widget = QWidget()
        canvas_reference.layout = QVBoxLayout(canvas_reference.widget)
        canvas_reference.layout.setContentsMargins(10, 10, 10, 10)
        
        header = QLabel("Devices")
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
        canvas_reference.layout.addWidget(header)
        
        add_btn = QPushButton("Add Device")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F538D;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
        """)
        add_btn.clicked.connect(lambda: self.add_device_row(None, None, canvas_reference))
        canvas_reference.layout.addWidget(add_btn)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        canvas_reference.dev_content = QWidget()
        canvas_reference.dev_layout = QVBoxLayout(canvas_reference.dev_content)
        canvas_reference.dev_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        canvas_reference.dev_layout.addStretch()
        scroll.setWidget(canvas_reference.dev_content)
        canvas_reference.layout.addWidget(scroll)
        
        canvas_reference.widget.setStyleSheet("""
            QWidget { background-color: #2B2B2B; }
        """)
        return canvas_reference.widget
    
    def create_internal_vars_panel(self, canvas_reference=None):
        """Create Internal Variables panel"""
        canvas_reference.internal_vars_rows_count = 0
        canvas_reference.internal_devs_rows_count = 0
        canvas_reference.internal_rows_count = 0
        canvas_reference.widget = QWidget()
        canvas_reference.layout = QVBoxLayout(canvas_reference.widget)
        canvas_reference.layout.setContentsMargins(10, 10, 10, 10)
        
        header = QLabel("Internal Variables")
        header.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
        canvas_reference.layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        canvas_reference.internal_content = QWidget()
        canvas_reference.internal_layout = QVBoxLayout(canvas_reference.internal_content)
        canvas_reference.internal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        canvas_reference.internal_layout.addStretch()
        add_internal_var_btn = QPushButton("Add Internal Variable")
        add_internal_var_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F538D;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
        """)
        add_internal_var_btn.clicked.connect(lambda: self.add_internal_variable_row(None, None, canvas_reference))
        canvas_reference.internal_layout.insertWidget(canvas_reference.internal_layout.count() - 1, add_internal_var_btn)
        
        add_internal_dev_btn = QPushButton("Add Internal Device")
        add_internal_dev_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F538D;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
        """)
    
        add_internal_dev_btn.clicked.connect(lambda: self.add_internal_device_row(None, None, canvas_reference))
        canvas_reference.internal_layout.insertWidget(canvas_reference.internal_layout.count() - 1, add_internal_dev_btn)
        scroll.setWidget(canvas_reference.internal_content)
        canvas_reference.layout.addWidget(scroll)

        canvas_reference.widget.setStyleSheet("""
            QWidget { background-color: #2B2B2B; }
        """)

        return canvas_reference.widget

    def create_sidebar(self):
        """Initialize sidebar and content areas"""
        widget = QWidget()
        main_layout = QHBoxLayout(widget)
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
        # Storage
        
        
        return widget

    def add_tab(self, tab_name, content_widget=None, icon=None, reference=None, function_id=None):
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
        
        if reference in ["canvas", "function"]:
            #print(f"Adding canvas tab: {tab_name}")
            canvas_splitter = QSplitter(Qt.Orientation.Vertical)
            canvas_splitter.addWidget(content_widget)
            canvas_splitter.setSizes([600, 400])  # Initial sizes (canvas, inspector)
            canvas_splitter.setCollapsible(0, False)  # Canvas cannot collapse
            content_widget.canvas_splitter = canvas_splitter
            content_widget.inspector_frame = None
            content_widget.inspector_layout = None
            content_widget.inspector_frame_visible = False
            content_widget.last_inspector_block = None
            content_widget.reference = reference
            if reference == "function":
                if not function_id:
                    #print("Generating new function ID")
                    self.function_id = 'Function_'+str(int(random()*100000))
                    #print(f"Generated function ID: {self.function_id}")
                else:
                    self.function_id = function_id
                #print(f"Function ID for tab '{tab_name}': {self.function_id}")
                Utils.functions[self.function_id] = {
                    'name': tab_name,
                    'id': self.function_id,
                    'canvas': content_widget,
                    'blocks': {},
                    'paths': {}
                }
                Utils.variables['function_canvases'][self.function_id] = {}
                Utils.devices['function_canvases'][self.function_id] = {}
            elif reference == "canvas":
                Utils.main_canvas = {
                    'name': tab_name,
                    'id': 'main_canvas',
                    'canvas': content_widget,
                    'blocks': {},
                    'paths': {}
                }
            self.content_area.addWidget(canvas_splitter)
            
        else: 
            self.content_area.addWidget(content_widget)
        self.pages[tab_name] = content_widget
        
        # Create tab button
        if reference == 'variable':
            #print("Adding Variable tab button")
            #print(f"Content widget in variable tab: {content_widget}")
            self.canvas_added.var_button = QPushButton(tab_name)
            tab_button = self.canvas_added.var_button
        elif reference == 'device':
            #print("Adding Device tab button")
            #print(f"Content widget in device tab: {content_widget}")
            self.canvas_added.dev_button = QPushButton(tab_name)
            tab_button = self.canvas_added.dev_button
        elif reference == 'internal_variable':
            #print("Adding Internal Variable tab button")
            #print(f"Content widget in internal variable tab: {content_widget}")
            self.canvas_added.internal_var_button = QPushButton(tab_name)
            tab_button = self.canvas_added.internal_var_button
        elif reference in ('canvas', 'function'):
            self.canvas_added = content_widget
            self.canvas_added.canvas_tab_button = QPushButton(tab_name)
            tab_button = self.canvas_added.canvas_tab_button
            self.canvas_added = None
        else:
            tab_button = QPushButton(tab_name)
        try:
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
            """)
        except Exception as e:
            print(f"Error setting stylesheet for tab button '{tab_name}': {e}")
        tab_index = self.page_count
        self.tab_buttons.append({
            'button': tab_button,
            'index': tab_index,
            'name': tab_name
        })
        #print(f"Adding tab '{tab_name}' at index {tab_index} with reference '{reference}'")
        tab_button.clicked.connect(lambda: self._on_tab_clicked(tab_index, reference))
        if reference == 'canvas':
            self.tab_layout.insertWidget(self.canvas_count, tab_button)
            self.page_count+=1
            self.count_w_separator+=1
            self.canvas_count+=1
            self.canvas_added = content_widget
            self.add_separator(ref='reference', content_widget=content_widget)
            self.add_new_canvas_tab_button(content_widget=content_widget)
            self.add_separator(content_widget=content_widget)
            self.add_variable_tab(content_widget, 'Main')
            self.add_device_tab(content_widget, 'Main')
            self.add_separator(ref='reference', content_widget=content_widget)
            self.canvas_added = None
            return tab_index
        elif reference == 'function':
            self.tab_layout.insertWidget(self.canvas_count, tab_button)
            self.page_count+=1
            self.count_w_separator+=1
            self.canvas_count+=1
            self.canvas_added = content_widget
            self.add_internal_variable_tab(content_widget, tab_name)
            self.add_separator(ref='reference', content_widget=content_widget)
            self.canvas_added = None
            return tab_index
        elif reference in ('variable', 'device', 'internal_variable'):
            self.tab_layout.insertWidget(self.count_w_separator, tab_button)
            self.page_count+=1
            self.count_w_separator+=1
            return tab_index
        else:
            self.tab_layout.addWidget(tab_button)
            self.page_count+=1
            self.count_w_separator+=1
            return tab_index
    
    def add_variable_tab(self, canvas_reference, name):
        """Add a Variables tab to the sidebar"""
        #print("Adding Variables tab")
        variables_panel = self.create_variables_panel(canvas_reference)
        self.add_tab(name+' variables', variables_panel, reference="variable")
    
    def add_device_tab(self, canvas_reference, name):
        """Add a Devices tab to the sidebar"""
        #print("Adding Devices tab")
        devices_panel = self.create_devices_panel(canvas_reference)
        self.add_tab(name+' devices', devices_panel, reference="device")
    
    def add_internal_variable_tab(self, canvas_reference, name):
        """Add an Internal Variables tab to the sidebar"""
        #print("Adding Internal Variables tab")
        internal_vars_panel = self.create_internal_vars_panel(canvas_reference)
        self.add_tab(name+' internal variables', internal_vars_panel, reference="internal_variable")

    def add_new_canvas_tab_button(self, content_widget=None):
        """Add a special button to create a new canvas tab"""
        content_widget.new_canvas_button = QPushButton("+ New Canvas")
        content_widget.new_canvas_button.setStyleSheet("""
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
        """)
        content_widget.new_canvas_button.clicked.connect(self._on_new_canvas_clicked)
        self.tab_layout.insertWidget(self.canvas_count, content_widget.new_canvas_button)
    
    def _on_new_canvas_clicked(self):
        """Handler for new canvas tab button click"""
        if not self.state_manager.app_state.on_tab_created():
            return

        name, ok = QInputDialog.getText(
            self,
            "New Canvas",
            "Enter name for new canvas:"
        )
        if not ok or not name.strip():
            return
        new_canvas = GridCanvas()
        new_canvas.main_window = self
        new_tab_index = self.add_tab(
            name,
            new_canvas,
            reference="function",
        )
        Utils.canvas_instances[new_canvas] = {
            'canvas': new_canvas,
            'index': new_tab_index,
            'id': self.function_id,
            'ref': 'function',
            'name': name
        }
        self.tab_changed.emit(new_tab_index)
        #print(f"Utils.canvas_instances count: {len(Utils.canvas_instances)}")
        #print(f"Utils.canvas_instances: {Utils.canvas_instances}")
        self.set_current_tab(new_tab_index, 'function')
    
    def add_separator(self, ref=None, content_widget=None):
        """Add a visual separator line with exactly 5px height"""
        if not hasattr(content_widget, 'separators'):
            content_widget.separators = []
        # Create a container for the separator
        content_widget.separator_container = QFrame()
        content_widget.separator_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)
        content_widget.separator_container.setFixedHeight(5)
        
        # Create the actual line
        content_widget.separator = QFrame()
        content_widget.separator.setFrameShape(QFrame.Shape.HLine)
        content_widget.separator.setFrameShadow(QFrame.Shadow.Plain)
        content_widget.separator.setLineWidth(1)
        content_widget.separator.setStyleSheet("background-color: #555555;")
        
        # Layout for container
        content_widget.layout = QVBoxLayout(content_widget.separator_container)
        content_widget.layout.setContentsMargins(0, 2, 0, 2)  # Vertical padding: 2px top + 2px bottom + 1px line = 5px total
        content_widget.layout.setSpacing(0)
        content_widget.layout.addWidget(content_widget.separator)
        content_widget.separators.append(content_widget.separator_container)
        if ref is None:
            self.tab_layout.insertWidget(self.canvas_count, content_widget.separator_container)
        else:
            self.tab_layout.insertWidget(self.count_w_separator, content_widget.separator_container)
            self.count_w_separator+=1
            
    def set_current_tab(self, tab_index, reference=None):
        """Switch to a specific tab by index"""
        if 0 <= tab_index < len(self.tab_buttons):
            self._on_tab_clicked(tab_index, reference)
    
    def get_current_tab_index(self):
        """Get currently active tab index"""
        return self.content_area.currentIndex()
    
    def get_tab_widget(self, tab_name):
        """Get the widget for a specific tab"""
        return self.pages.get(tab_name)
    
    def _on_tab_clicked(self, tab_index, reference=None):
        """Internal handler for tab clicks"""
        if self.state_manager.app_state.on_tab_changed():
            if 0 <= tab_index < len(self.tab_buttons):
                self.content_area.setCurrentIndex(tab_index)
                
                # Update button styles
                for tb in self.tab_buttons:
                    if tb['index'] == tab_index:
                        print(f"Setting active style for tab '{tb['name']}' at index {tab_index}")
                        try:
                            tb['button'].setStyleSheet("""
                                QPushButton {
                                    background-color: #1F538D;
                                    color: #FFFFFF;
                                    border: none;
                                    border-left: 3px solid #4CAF50;
                                    padding: 12px;
                                    text-align: left;
                                }
                            """)
                        except Exception as e:
                            print(f"Error setting active stylesheet for tab button '{tb['name']}': {e}")
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
                    pass
                    #print(f"Setting Utils.courent_canvas to canvas tab index {tab_index}")
                    #print(f"Utils.canvas_instances: {Utils.canvas_instances}")
                    #if tab_index - self.canvas_count < 0:
                        #tab_index = 0
                        #print(f"Courent canvas index: {tab_index}")
                        #Utils.courent_canvas = Utils.canvas_instances[tab_index]
                        #print(f"Set Utils.courent_canvas to tab '{Utils.courent_canvas}'")
                    #else:
                        #print(f"Setting Utils.courent_canvas to index {tab_index - self.canvas_count+1}")
                        #Utils.courent_canvas = Utils.canvas_instances[tab_index-self.canvas_count+1]
                        #print(f"Set Utils.courent_canvas to tab '{Utils.courent_canvas}'")
                self.state_manager.app_state.current_tab_reference = reference
                self.tab_changed.emit(tab_index)
    #MARK: - Inspector Panel Methods
    def toggle_inspector_frame(self, block):
        """Toggle inspector panel based on block selection"""
        #print(f"Self in toggle_inspector_frame: {self}")
        #print(f"Current canvas in toggle_inspector_frame: {self.current_canvas}")
        current_canvas = self.current_canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return
        
        # Get the splitter from the current canvas
        canvas_splitter = getattr(current_canvas, 'canvas_splitter', None)
        if canvas_splitter is None:
            print("ERROR: No canvas_splitter found in current canvas")
            return
        if not current_canvas.inspector_frame_visible:
            current_canvas.last_inspector_block = block
            self.show_inspector_frame(block)
        elif current_canvas.inspector_frame_visible and current_canvas.last_inspector_block != block:
            current_canvas.last_inspector_block = block
            self.update_inspector_content(block)
        else:
            # Toggle off if clicking same block
            self.hide_inspector_frame()
        
    def show_inspector_frame(self, block):
        """Show the inspector panel"""
        #print(f"Self in show_inspector_frame: {self}")
        current_canvas = self.current_canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return
        
        # Get the splitter from the current canvas
        canvas_splitter = getattr(current_canvas, 'canvas_splitter', None)
        if canvas_splitter is None:
            print("ERROR: No canvas_splitter found in current canvas")
            return
        if not current_canvas.inspector_frame_visible:
            current_canvas.last_inspector_block = block
            
            # Get current canvas
            
            
            # Create inspector frame if it doesn't exist
            if current_canvas.inspector_frame is None:
                current_canvas.inspector_frame = QFrame()
                current_canvas.inspector_frame.setStyleSheet("""
                    QFrame {
                        background-color: 2B2B2B;
                        border-left: 1px solid 3A3A3A;
                    }
                """)
                current_canvas.inspector_layout = QVBoxLayout(current_canvas.inspector_frame)
                
                # Scroll area
                current_canvas.scroll_area = QScrollArea()
                current_canvas.scroll_area.setWidgetResizable(True)
                current_canvas.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                
                current_canvas.inspector_content = QWidget()
                current_canvas.inspector_content_layout = QVBoxLayout(current_canvas.inspector_content)
                current_canvas.inspector_content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                current_canvas.inspector_content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                current_canvas.scroll_area.setWidget(current_canvas.inspector_content)
                
                current_canvas.inspector_layout.addWidget(current_canvas.scroll_area)
            
            # Add inspector to splitter
            current_canvas.canvas_splitter.addWidget(current_canvas.inspector_frame)
            current_canvas.canvas_splitter.setSizes([700, 300])  # Adjust initial ratio
            
            if block:
                self.update_inspector_content(block)
            
            current_canvas.inspector_frame.show()
            current_canvas.inspector_frame_visible = True


    def hide_inspector_frame(self):
        """Hide the inspector panel"""
        current_canvas = self.current_canvas
        if current_canvas:
            canvas_splitter = getattr(current_canvas, 'canvas_splitter', None)
                    
        if canvas_splitter and current_canvas.inspector_frame:
            current_canvas.inspector_frame.hide()
            
            # Get current canvas and its splitter
            if canvas_splitter:
                canvas_splitter.setSizes([1000, 0])  # Hide inspector
            
            current_canvas.inspector_frame_visible = False

    def update_inspector_content(self, block):
        """Update the content of the inspector panel based on the selected block"""
        current_canvas = self.current_canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return
        
        # Get the splitter from the current canvas
        canvas_splitter = getattr(current_canvas, 'canvas_splitter', None)
        if canvas_splitter is None:
            print("ERROR: No canvas_splitter found in current canvas")
            return
        # Clear ONLY the content layout, NOT the main inspector layout
        while current_canvas.inspector_content_layout.count():
            item = current_canvas.inspector_content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Remove spacer items
        for i in range(current_canvas.inspector_content_layout.count() - 1, -1, -1):
            item = current_canvas.inspector_content_layout.itemAt(i)
            if item and item.spacerItem():
                current_canvas.inspector_content_layout.takeAt(i)
        
        # Add new content
        title = QLabel(f"Inspector - {block.block_type}")
        title.setStyleSheet("font-weight: bold; font-size: 16px; padding: 5px;")
        current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), title)
        
        self.position_label = QLabel(f"Position: ({int(block.x())}, {int(block.y())})")
        current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), self.position_label)
        
        size_label = QLabel(f"Size: ({int(block.boundingRect().width())} x {int(block.boundingRect().height())})")
        current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), size_label)
        
        self.add_inputs(block)
        current_canvas.inspector_content_layout.addStretch()

    def update_pos(self, block):
        """Update position labels in inspector"""
        current_canvas = self.current_canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return
        
        if self.position_label:
            position_label = self.position_label
        else:
            position_label = None
        
        if position_label:
            position_label.setText(f"Position: ({int(block.x())}, {int(block.y())})")

    def add_inputs(self, block, dev_id=None, var_id=None):
        """Add input fields for block properties"""
        current_canvas = self.current_canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return
        
        if current_canvas.reference == 'canvas':
            #print(f"Current Utils.main_canvas['blocks']: {Utils.main_canvas['blocks']}")
            block_data = Utils.main_canvas['blocks'].get(block.block_id)
        elif current_canvas.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                if current_canvas == f_info.get('canvas'):
                    #print(f"Current Utils.functions[{f_id}]['blocks']: {Utils.functions[f_id]['blocks']}")
                    block_data = Utils.functions[f_id]['blocks'].get(block.block_id)
                    break
        
        #print(f"Adding inputs for block data: {block_data}")
        if block_data['type'] in ('Start', 'End'):
            return
        
        if block_data['type'] == 'Timer':
            # Timer block inputs
            label = QLabel("Interval (ms):")
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), label)
            
            interval_input = QLineEdit()
            regex = QRegularExpression(r"^\d*$")
            validator = QRegularExpressionValidator(regex, self)
            interval_input.setValidator(validator)
            interval_input.setText(block_data.get('sleep_time', '1000'))
            interval_input.setPlaceholderText("Interval in ms")
            interval_input.textChanged.connect(lambda text, bd=block_data: self.Block_sleep_interval_changed(text, bd))
            
            current_canvas.inspector_content_layout.insertWidget(
                current_canvas.inspector_content_layout.count(), 
                interval_input
            )
        if block_data['type'] in ('If', 'While', 'For Loop'):
            name_label = QLabel("Value 1 Name:")
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label)
            
            self.name_1_input = SearchableLineEdit()
            self.name_1_input.setText(block_data.get('value_1_name', ''))
            self.name_1_input.setPlaceholderText("Value 1 Name")
            self.name_1_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_1_name_changed(text, bd))
            
            self.insert_items(block, self.name_1_input)
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), self.name_1_input)
            
            type_label = QLabel("Operator:")
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), type_label)
            
            type_input = QComboBox()
            type_input.addItems(["==", "!=", "<", ">", "<=", ">="])
            type_input.setCurrentText(block_data.get('operator', '=='))
            type_input.currentTextChanged.connect(lambda text, bd=block_data: self.Block_operator_changed(text, bd))
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), type_input)
            
            value_label = QLabel("Value 2 name:")
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), value_label)
            
            self.name_2_input = SearchableLineEdit()
            self.name_2_input.setText(block_data.get('value_2_name', ''))
            self.name_2_input.setPlaceholderText("Value 2 Name")
            self.name_2_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_2_name_changed(text, bd))
            
            self.insert_items(block, self.name_2_input)
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), self.name_2_input)
        if block_data['type'] == 'Switch':
            name_label = QLabel("Value Name:")
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label)
            
            self.name_1_input = SearchableLineEdit()
            self.name_1_input.setText(block_data.get('value_1_name', ''))
            self.name_1_input.setPlaceholderText("Value Name")
            self.name_1_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_1_name_changed(text, bd))
            
            self.insert_items(block, self.name_1_input)
            
            self.Label_ON = QLabel("On")
            self.Label_OFF = QLabel("Off")
            
            self.switch = CustomSwitch()
            self.switch.set_checked(block_data.get('switch_state', False))
            self.switch.toggled.connect(lambda state, bd=block_data: self.Block_switch_changed(state, bd))
            
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(5, 5, 5, 5)
            
            row_layout.addWidget(self.Label_OFF)
            row_layout.addWidget(self.switch)
            row_layout.addWidget(self.Label_ON)
            
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), self.name_1_input)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), row_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        if block_data['type'] == 'Button':
            name_label = QLabel("Value Name:")
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label)
            
            self.name_1_input = SearchableLineEdit()
            self.name_1_input.setText(block_data.get('value_1_name', ''))
            self.name_1_input.setPlaceholderText("Value Name")
            self.name_1_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_1_name_changed(text, bd))
            
            self.insert_items(block, self.name_1_input)
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), self.name_1_input)
        if block_data['type'] == 'Blink_LED':
            name_label = QLabel("LED device name:")
            
            self.name_1_input = SearchableLineEdit()
            self.name_1_input.setText(block_data.get('value_1_name', ''))
            self.name_1_input.setPlaceholderText("LED device name")
            self.name_1_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_1_name_changed(text, bd))
            
            self.insert_items(block, self.name_1_input)
            
            time_label = QLabel("Blink Interval (ms):")

            self.blink_time_input = QLineEdit()
            regex = QRegularExpression(r"^\d*$")
            validator = QRegularExpressionValidator(regex, self)
            self.blink_time_input.setValidator(validator)
            self.blink_time_input.setText(block_data.get('sleep_time', '1000'))
            self.blink_time_input.setPlaceholderText("Blink Interval in ms")
            self.blink_time_input.textChanged.connect(lambda text, bd=block_data: self.Block_sleep_interval_changed(text, bd))

            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), self.name_1_input)

            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), time_label)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), self.blink_time_input)
        if block_data['type'] == 'Toggle_LED':
            name_label = QLabel("LED device name:")
            
            self.name_1_input = SearchableLineEdit()
            self.name_1_input.setText(block_data.get('value_1_name', ''))
            self.name_1_input.setPlaceholderText("LED device name")
            self.name_1_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_1_name_changed(text, bd))
            
            self.insert_items(block, self.name_1_input)

            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), self.name_1_input)
        if block_data['type'] == 'PWM_LED':
            name_label = QLabel("LED device name:")
            
            self.name_1_input = SearchableLineEdit()
            self.name_1_input.setText(block_data.get('value_1_name', ''))
            self.name_1_input.setPlaceholderText("LED device name")
            self.name_1_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_1_name_changed(text, bd))
            
            self.insert_items(block, self.name_1_input)

            PWM_label = QLabel("PWM Value (0-255):")

            self.PWM_value_input = QLineEdit()
            regex = QRegularExpression(r"^\d*$")
            validator = QRegularExpressionValidator(regex, self)
            self.PWM_value_input.setValidator(validator)
            self.PWM_value_input.setText(block_data.get('PWM_value', '128'))
            self.PWM_value_input.setPlaceholderText("PWM Value (0-255)")
            self.PWM_value_input.textChanged.connect(lambda text, bd=block_data: self.Block_PWM_value_changed(text, bd))

            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), self.name_1_input)

            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), PWM_label)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), self.PWM_value_input)
        if block_data['type'] in ("Basic_operations", "Exponential_operations", "Random_number"):
            name_label = QLabel("First Variable Name:")
            
            self.value_1_name_input = SearchableLineEdit()
            self.value_1_name_input.setText(block_data.get('value_1_name', ''))
            self.value_1_name_input.setPlaceholderText("First Variable Name")
            self.value_1_name_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_1_name_changed(text, bd))

            if block_data['type'] == "Basic_operations":
                box_label = QLabel("Operator:")

                operator_box = QComboBox()
                operator_box.addItems(["+", "-", "*", "/", "%"])
                operator_box.setCurrentText(block_data.get('operator', '+'))
                operator_box.currentTextChanged.connect(lambda text, bd=block_data: self.Block_operator_changed(text, bd))
            elif block_data['type'] == "Exponential_operations":
                box_label = QLabel("Operator:")

                operator_box = QComboBox()
                operator_box.addItems(["^", "√"])
                operator_box.setCurrentText(block_data.get('operator', '^'))
                operator_box.currentTextChanged.connect(lambda text, bd=block_data: self.Block_operator_changed(text, bd))
            else:
                operator_box = None

            name_label_2 = QLabel("Second Variable Name:")

            self.value_2_name_input = SearchableLineEdit()
            self.value_2_name_input.setText(block_data.get('value_2_name', ''))
            self.value_2_name_input.setPlaceholderText("Second Variable Name")
            self.value_2_name_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_2_name_changed(text, bd))

            name_label_3 = QLabel("Result Variable Name:")

            self.result_var_name_input = SearchableLineEdit()
            self.result_var_name_input.setText(block_data.get('result_var_name', ''))
            self.result_var_name_input.setPlaceholderText("Result Variable Name")
            self.result_var_name_input.textChanged.connect(lambda text, bd=block_data: self.Block_result_var_name_changed(text, bd))

            self.insert_items(block, self.value_1_name_input)
            self.insert_items(block, self.value_2_name_input)
            self.insert_items(block, self.result_var_name_input)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label_3)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), self.result_var_name_input)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), self.value_1_name_input) 
            if operator_box:
                current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), box_label)
                current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), operator_box) 
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), name_label_2)
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), self.value_2_name_input)
        if block_data['type'] == 'Function':
            
            var_label = QLabel("Input variables")
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), var_label)

            for canv, canv_info in Utils.canvas_instances.items():
                if canv_info.get('ref') == 'function' and canv_info.get('name') == block_data.get('name'):
                    break
            #print(f"Function canvas info: {canv_info}")
            
            for var_id, var_info in Utils.variables['function_canvases'][canv_info['id']].items():
                line_widget = QWidget()
                line_layout = QHBoxLayout(line_widget)
                line_layout.setContentsMargins(0, 0, 0, 0)
                
                ref_var_label = QLabel("Ref Variable:")

                ref_var_name = QLabel(var_info['name'])

                main_var_label = QLabel("Main Variable:")

                main_var_combo = SearchableLineEdit()
                main_var_combo.setPlaceholderText("Linked Variable Name")

                self.insert_items(block, main_var_combo, type='variable_m')
                line_layout.addWidget(ref_var_label)
                line_layout.addWidget(ref_var_name)
                line_layout.addWidget(main_var_label)
                line_layout.addWidget(main_var_combo) 

                if var_id is None:
                    id_var_generated = False
                    while not id_var_generated:
                        var_id = 'var_'+str(int(random()*100000))
                        if var_id not in block_data['internal_vars']['ref_vars'].keys():
                            id_var_generated = True
                            break
                        else:
                            id_var_generated = False
                if var_id not in block_data['internal_vars'].get('ref_vars', {}):
                    block_data['internal_vars']['ref_vars'][var_id] = {
                        'name': '',
                        'type': '',
                    }
                block_data['internal_vars']['ref_vars'][var_id]['name'] = var_info['name']
                block_data['internal_vars']['ref_vars'][var_id]['type'] = 'Variable'

                main_var_combo.textChanged.connect(lambda text, bd=block_data, v=var_id: self.function_variable_changed(text, bd, v))

                current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), line_widget)
            
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Plain)
            separator.setLineWidth(1)
            separator.setStyleSheet("background-color: #555555;")
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), separator)

            dev_label = QLabel("Imput devices")

            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), dev_label)

            for dev_id, dev_info in Utils.devices['function_canvases'][canv_info['id']].items():
                line_widget = QWidget()
                line_layout = QHBoxLayout(line_widget)
                line_layout.setContentsMargins(0, 0, 0, 0)
                
                ref_dev_label = QLabel("Ref Device:")

                ref_dev_name = QLabel(dev_info['name'])

                main_dev_label = QLabel("Main Device:")

                main_dev_combo = SearchableLineEdit()
                main_dev_combo.setPlaceholderText("Linked Device Name")

                self.insert_items(block, main_dev_combo, type='device_m')
                line_layout.addWidget(ref_dev_label)
                line_layout.addWidget(ref_dev_name)
                line_layout.addWidget(main_dev_label)
                line_layout.addWidget(main_dev_combo)
                
                if dev_id is None:
                    id_dev_generated = False
                    while not id_dev_generated:
                        dev_id = 'dev_'+str(int(random()*100000))
                        if dev_id not in block_data['internal_devs']['ref_devs'].keys():
                            id_dev_generated = True
                            break
                        else:
                            id_dev_generated = False

                if dev_id not in block_data['internal_devs'].get('ref_devs', {}):
                    block_data['internal_devs']['ref_devs'][dev_id] = {
                        'name': '',
                        'type': '',
                    }
                block_data['internal_devs']['ref_devs'][dev_id]['name'] = dev_info['name']
                block_data['internal_devs']['ref_devs'][dev_id]['type'] = 'Device'

                main_dev_combo.textChanged.connect(lambda text, bd=block_data, d=dev_id: self.function_device_changed(text, bd, d))


                current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), line_widget)
#MARK: - Block Property Change Handlers
    def function_variable_changed(self, text, block_data, var_id=None):
        #print(f"Function variable changed to: {text}, type: {type}")
        # Implement the logic to update function variable mapping in block_data
        # This is a placeholder implementation
        if var_id in block_data['internal_vars'].get('main_vars', {}):
            old_name = block_data['internal_vars']['main_vars'][var_id]['name']
            del block_data['internal_vars']['main_vars'][var_id]
        if var_id not in block_data['internal_vars'].get('main_vars', {}):
            block_data['internal_vars']['main_vars'][var_id] = {
                'name': '',
                'type': '',
            }
        block_data['internal_vars']['main_vars'][var_id]['name'] = text
        block_data['internal_vars']['main_vars'][var_id]['type'] = 'Variable'
        print(f"Updated block_data: {block_data}")

    def function_device_changed(self, text, block_data, dev_id=None):
        #print(f"Function device changed to: {text}, type: {type}")
        # Implement the logic to update function device mapping in block_data
        # This is a placeholder implementation
        if dev_id in block_data['internal_devs'].get('main_devs', {}):
            old_name = block_data['internal_devs']['main_devs'][dev_id]['name']
            del block_data['internal_devs']['main_devs'][dev_id]
        if dev_id not in block_data['internal_devs'].get('main_devs', {}):
            block_data['internal_devs']['main_devs'][dev_id] = {
                'name': '',
                'type': '',
            }
        block_data['internal_devs']['main_devs'][dev_id]['name'] = text
        block_data['internal_devs']['main_devs'][dev_id]['type'] = 'Device'
        print(f"Updated block_data: {block_data}")

    def Block_value_1_name_changed(self, text, block_data):
        current_canvas = self.current_canvas
        #print("Updating vlaue 1 name")
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return
        
        block_data['value_1_name'] = text
        if current_canvas.reference == 'canvas':
            #print(f"Current Utils.main_canvas['blocks']: {Utils.main_canvas['blocks']}")
            variables = Utils.variables['main_canvas']
            devices = Utils.devices['main_canvas']
        elif current_canvas.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                if current_canvas == f_info.get('canvas'):
                    #print(f"Current Utils.functions[{f_id}]['blocks']: {Utils.functions[f_id]['blocks']}")
                    variables = Utils.variables['function_canvases'][f_id]
                    devices = Utils.devices['function_canvases'][f_id]
                    break
        for var_id, var_info in variables.items():
            #print(f"Checking variable: {var_info}")
            if var_info['name'] == text:
                block_data['value_1_type'] = 'Variable'
                break
        for dev_id, dev_info in devices.items():
            if dev_info['name'] == text:
                block_data['value_1_type'] = 'Device'
                break
        if block_data['type'] == 'Button':
            if len(text) > 6:
                text = text[:4] + "..."
        else:
            if len(text) > 5:
                text = text[:3] + "..."
        block_data['value_1_name'] = text
        block_data['widget'].value_1_name = text
        block_data['widget'].update()
    
    def Block_operator_changed(self, text, block_data):
        #print("Updating operator")
        block_data['operator'] = text 
        block_data['widget'].operator = text   
        block_data['widget'].update()
    
    def Block_value_2_name_changed(self, text, block_data):
        #print("Updating vlaue 2 name") 
        block_data['value_2_name'] = text
        current_canvas = self.current_canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return

        if current_canvas.reference == 'canvas':
            #print(f"Current Utils.main_canvas['blocks']: {Utils.main_canvas['blocks']}")
            variables = Utils.variables['main_canvas']
            devices = Utils.devices['main_canvas']
        elif current_canvas.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                if current_canvas == f_info.get('canvas'):
                    #print(f"Current Utils.functions[{f_id}]['blocks']: {Utils.functions[f_id]['blocks']}")
                    variables = Utils.variables['function_canvases'][f_id]
                    devices = Utils.devices['function_canvases'][f_id]
                    break

        for var_id, var_info in variables.items():
            if var_info['name'] == text:
                block_data['value_2_type'] = 'Variable'
                break
        for dev_id, dev_info in devices.items():
            if dev_info['name'] == text:
                block_data['value_2_type'] = 'Device'
                break
        if len(text) > 5:
            text = text[:3] + "..."
        block_data['value_2_name'] = text
        block_data['widget'].value_2_name = text
        block_data['widget'].update()
    
    def Block_result_var_name_changed(self, text, block_data):
        #print("Updating result variable name") 
        block_data['result_var_name'] = text
        current_canvas = self.current_canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return

        if current_canvas.reference == 'canvas':
            #print(f"Current Utils.main_canvas['blocks']: {Utils.main_canvas['blocks']}")
            variables = Utils.variables['main_canvas']
            devices = Utils.devices['main_canvas']
        elif current_canvas.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                if current_canvas == f_info.get('canvas'):
                    #print(f"Current Utils.functions[{f_id}]['blocks']: {Utils.functions[f_id]['blocks']}")
                    variables = Utils.variables['function_canvases'][f_id]
                    devices = Utils.devices['function_canvases'][f_id]
                    break

        for var_id, var_info in variables.items():
            if var_info['name'] == text:
                block_data['result_var_type'] = 'Variable'
                break
        for dev_id, dev_info in devices.items():
            if dev_info['name'] == text:
                block_data['result_var_type'] = 'Device'
                break
        if len(text) > 5:
            text = text[:3] + "..."
        block_data['result_var_name'] = text
        block_data['widget'].result_var_name = text
        block_data['widget'].update()
    
    def Block_switch_changed(self, state, block_data):
        block_data['switch_state'] = state
        block_data['widget'].switch_state = state
        block_data['widget'].update()
    
    def Block_sleep_interval_changed(self, text, block_data):
        #print("Updating sleep interval")
        block_data['sleep_time'] = text
        block_data['widget'].sleep_time = text
        block_data['widget'].update()

    def Block_PWM_value_changed(self, text, block_data):
        #print("Updating PWM value")
        if text != '':
            pwm_val = int(text)
            if pwm_val < 0:
                pwm_val = 0
            elif pwm_val > 255:
                pwm_val = 255
            text = str(pwm_val)
            self.PWM_value_input.setText(text)
        block_data['PWM_value'] = text
        block_data['widget'].PWM_value = text
        block_data['widget'].update()

    def insert_items(self, block, line_edit, type=None):
        #print("Inserting items into line edit")
        current_canvas = self.current_canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return
        if current_canvas.reference == 'canvas':
            #print(f"Current Utils.main_canvas['blocks']: {Utils.main_canvas['blocks']}")
            if not block.block_id in Utils.main_canvas['blocks']:
                return
        elif current_canvas.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                if current_canvas == f_info.get('canvas'):
                    #print(f"Current Utils.functions[{f_id}]['blocks']: {Utils.functions[f_id]['blocks']}")
                    if not block.block_id in Utils.functions[f_id]['blocks']:
                        return
                    break
        #print("Inserting items into combo box")
        if hasattr(line_edit, 'addItems'):
            #print("Line edit supports addItems")
            # Collect all items
            all_items = []
            #print(f"All items before insertion: {all_items}")
            if block.block_type in ('Switch', 'Button'):
                if self.current_canvas.reference == 'canvas':
                    for id, text in Utils.devices['main_canvas'].items():
                        #print(f"Added device item into Switch/Button: {text}")
                        all_items.append(text['name'])
                elif self.current_canvas.reference == 'function':
                    for f_id, f_info in Utils.functions.items():
                        if current_canvas == f_info.get('canvas'):
                            for id, text in Utils.devices['function_canvases'][f_id].items():
                                #print(f"Added function device item into Switch/Button: {text}")
                                all_items.append(text['name'])
                            break
            elif block.block_type.startswith('Function_'):
                for canvas, info in Utils.canvas_instances.items():
                    if info['ref'] == 'function' and info['name'] == block.block_type.split('_')[1]:
                        function_id = info['id']
                        break
                if type == 'variable_f':
                    for v_id, v_info in Utils.variables['function_canvases'][function_id].items():
                        all_items.append(v_info['name'])
                        #print(f"Added function variable item: {v_info['name']}")
                elif type == 'variable_m':
                    for v_id, v_info in Utils.variables['main_canvas'].items():
                        all_items.append(v_info['name'])
                        #print(f"Added main variable item: {v_info['name']}")
                elif type == 'device_f':
                    for d_id, d_info in Utils.devices['function_canvases'][function_id].items():
                        all_items.append(d_info['name'])
                        #print(f"Added function device item: {d_info['name']}")
                elif type == 'device_m':
                    for d_id, d_info in Utils.devices['main_canvas'].items():
                        all_items.append(d_info['name'])
                        #print(f"Added main device item: {d_info['name']}")
            else:
                if self.current_canvas.reference == 'canvas':
                    for id, text in Utils.variables['main_canvas'].items():
                        all_items.append(text['name'])
                        #print(f"Added variable item: {text['name']}")
                    for id, text in Utils.devices['main_canvas'].items():
                        #print(f"Added device item: {text['name']}")
                        all_items.append(text['name'])
                elif self.current_canvas.reference == 'function':
                    for f_id, f_info in Utils.functions.items():
                        if current_canvas == f_info.get('canvas'):
                            for id, text in Utils.variables['function_canvases'][f_id].items():
                                all_items.append(text['name'])
                                #print(f"Added function variable item: {text['name']}")
                            for id, text in Utils.devices['function_canvases'][f_id].items():
                                all_items.append(text['name'])
                                #print(f"Added function device item: {text['name']}")
                            break

            # Add all items at once
            #print(f"Inserting items into combo box: {all_items}")
            line_edit.addItems(all_items)
            #print(f"Added {len(all_items)} items to combo box")

    #MARK: - Internal Variable Panel Methods
    def add_internal_variable_row(self, var_id=None, var_data=None, canvas_reference=None):
        """Add a new internal variable row"""
        #print(f"Adding variable row to canvas_reference: {canvas_reference}")
        id_var_generated = False
        if var_id is None:
            while not id_var_generated:
                var_id = f"variable_{str(int(random()*100000))}"
                #print(f"Generated variable_id attempt: {var_id}")
                for canvas, info in Utils.canvas_instances.items():
                    if canvas_reference == canvas and info['ref'] == 'canvas':
                        #print(f"Checking main_canvas for var_id: {var_id}")
                        pass
                    elif canvas_reference == canvas and info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                if var_id not in Utils.variables['function_canvases'][function_id].keys():
                                    Utils.variables['function_canvases'][function_id][var_id] = {
                                        'name': '',
                                        'type': 'Int',
                                        'widget': None,
                                        'name_imput': None,
                                        'type_input': None,
                                    }
                                    id_var_generated = True
                                    break
                                else:
                                    var_id = None
                    else:
                        print("Error: Canvas reference not found in Utils.canvas_instances")
        else:
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas and info['ref'] == 'canvas':
                    #print(f"Adding predefined var_id to main_canvas: {var_id}")
                    pass
                elif canvas_reference == canvas and info['ref'] == 'function':
                    for function_id, function_info in Utils.functions.items():
                        if function_info['canvas'] == canvas_reference:
                            Utils.variables['function_canvases'][function_id][var_id] = {
                                'name': '',
                                'type': 'Int',
                                'widget': None,
                                'name_imput': None,
                                'type_input': None,
                            }
                else:
                    print("Error: Canvas reference not found in Utils.canvas_instances")
        #print(f"Utils.variables after adding new variable: {Utils.variables}")
        canvas_reference.row_widget = QWidget()
        canvas_reference.row_layout = QHBoxLayout(canvas_reference.row_widget)
        canvas_reference.row_layout.setContentsMargins(5, 5, 5, 5)

        name_imput = QLineEdit()
        name_imput.setPlaceholderText("Name")
        if var_data and 'name' in var_data:
            name_imput.setText(var_data['name'])
            for function_id, function_info in Utils.functions.items():
                if function_info['canvas'] == canvas_reference:
                    Utils.variables['function_canvases'][function_id][var_id]['name'] = var_data['name']
        
        name_imput.textChanged.connect(lambda text, v_id=var_id, t="Variable", r=canvas_reference: self.name_changed(text, v_id, t, r))
        
        type_input = QComboBox()
        type_input.addItems(["Int", "Float", "String", "Bool"])
        if var_data and 'type' in var_data:
            type_input.setCurrentText(var_data['type'])
            for function_id, function_info in Utils.functions.items():
                if function_info['canvas'] == canvas_reference:
                    Utils.variables['function_canvases'][function_id][var_id]['type'] = var_data['type']
        
        type_input.currentTextChanged.connect(lambda  text, v_id=var_id, t="Variable", r=canvas_reference: self.type_changed(text, v_id , t, r))
        
        delete_btn = QPushButton("×")
        delete_btn.setFixedWidth(30)
        
        canvas_reference.row_layout.addWidget(name_imput)
        canvas_reference.row_layout.addWidget(type_input)
        canvas_reference.row_layout.addWidget(delete_btn)
        
        delete_btn.clicked.connect(lambda _, v_id=var_id, rw=canvas_reference.row_widget, t="Variable", r=canvas_reference: self.remove_internal_row(rw, v_id, t, r))

        for function_id, function_info in Utils.functions.items():
            if function_info['canvas'] == canvas_reference:
                Utils.variables['function_canvases'][function_id][var_id]['widget'] = canvas_reference.row_widget
                Utils.variables['function_canvases'][function_id][var_id]['name_imput'] = name_imput
                Utils.variables['function_canvases'][function_id][var_id]['type_input'] = type_input
        panel_layout = canvas_reference.internal_layout
        panel_layout.insertWidget(panel_layout.count() - 2 - canvas_reference.internal_devs_rows_count, canvas_reference.row_widget)
        
        canvas_reference.internal_vars_rows_count += 1
        canvas_reference.internal_rows_count += 1

        #print(f"Added variable: {self.var_id}")
    def add_internal_device_row(self, dev_id=None, dev_data=None, canvas_reference=None):
        #print(f"Adding variable row to canvas_reference: {canvas_reference}")
        id_dev_generated = False
        if dev_id is None:
            while not id_dev_generated:
                dev_id = f"device_{str(int(random()*100000))}"
                #print(f"Generated device_id attempt: {dev_id}")
                for canvas, info in Utils.canvas_instances.items():
                    if canvas_reference == canvas and info['ref'] == 'canvas':
                        #print(f"Checking main_canvas for dev_id: {dev_id}")
                        pass
                    elif canvas_reference == canvas and info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                if dev_id not in Utils.devices['function_canvases'][function_id].keys():
                                    Utils.devices['function_canvases'][function_id][dev_id] = {
                                        'name': '',
                                        'type': 'Output',
                                        'widget': None,
                                        'name_imput': None,
                                        'type_input': None,
                                    }
                                    id_dev_generated = True
                                    break
                                else:
                                    dev_id = None
                    else:
                        print("Error: Canvas reference not found in Utils.canvas_instances")
        else:
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas and info['ref'] == 'canvas':
                    #print(f"Adding predefined dev_id to main_canvas: {dev_id}")
                    pass
                elif canvas_reference == canvas and info['ref'] == 'function':
                    for function_id, function_info in Utils.functions.items():
                        if function_info['canvas'] == canvas_reference:
                            Utils.devices['function_canvases'][function_id][dev_id] = {
                                'name': '',
                                'type': 'Output',
                                'widget': None,
                                'name_imput': None,
                                'type_input': None,
                            }
                else:
                    print("Error: Canvas reference not found in Utils.canvas_instances")
        #print(f"Utils.devices after adding new device: {Utils.devices}")
        canvas_reference.row_widget = QWidget()
        canvas_reference.row_layout = QHBoxLayout(canvas_reference.row_widget)
        canvas_reference.row_layout.setContentsMargins(5, 5, 5, 5)

        name_imput = QLineEdit()
        name_imput.setPlaceholderText("Name")
        if dev_data and 'name' in dev_data:
            name_imput.setText(dev_data['name'])
            for function_id, function_info in Utils.functions.items():
                if function_info['canvas'] == canvas_reference:
                    Utils.devices['function_canvases'][function_id][dev_id]['name'] = dev_data['name']
        
        name_imput.textChanged.connect(lambda text, v_id=dev_id, t="Device", r=canvas_reference: self.name_changed(text, v_id, t, r))
        
        type_input = QComboBox()
        type_input.addItems(["Output", "Input", "Button", "PWM"])
        if dev_data and 'type' in dev_data:
            type_input.setCurrentText(dev_data['type'])
            for function_id, function_info in Utils.functions.items():
                if function_info['canvas'] == canvas_reference:
                    Utils.devices['function_canvases'][function_id][dev_id]['type'] = dev_data['type']
        
        type_input.currentTextChanged.connect(lambda  text, v_id=dev_id, t="Device", r=canvas_reference: self.type_changed(text, v_id , t, r))
        
        delete_btn = QPushButton("×")
        delete_btn.setFixedWidth(30)
        
        canvas_reference.row_layout.addWidget(name_imput)
        canvas_reference.row_layout.addWidget(type_input)
        canvas_reference.row_layout.addWidget(delete_btn)
        
        delete_btn.clicked.connect(lambda _, v_id=dev_id, rw=canvas_reference.row_widget, t="Device", r=canvas_reference: self.remove_internal_row(rw, v_id, t, r))

        for function_id, function_info in Utils.functions.items():
            if function_info['canvas'] == canvas_reference:
                Utils.devices['function_canvases'][function_id][dev_id]['widget'] = canvas_reference.row_widget
                Utils.devices['function_canvases'][function_id][dev_id]['name_imput'] = name_imput
                Utils.devices['function_canvases'][function_id][dev_id]['type_input'] = type_input
        panel_layout = canvas_reference.internal_layout
        panel_layout.insertWidget(panel_layout.count() - 1, canvas_reference.row_widget)
        
        canvas_reference.internal_devs_rows_count += 1
        canvas_reference.internal_rows_count += 1
    #MARK: - Variable Panel Methods
    def add_variable_row(self, var_id=None, var_data=None, canvas_reference=None):
        """Add a new variable row"""
        #print(f"Adding variable row to canvas_reference: {canvas_reference}")
        id_var_generated = False
        if var_id is None:
            while not id_var_generated:
                var_id = f"variable_{str(int(random()*100000))}"
                #print(f"Generated variable_id attempt: {var_id}"
                if var_id not in Utils.variables['main_canvas'].keys():
                    Utils.variables['main_canvas'][var_id] = {
                        'name': '',
                        'type': 'Int',
                        'value': '',
                        'widget': None,
                        'name_imput': None,
                        'type_input': None,
                        'value_input': None
                    }
                    id_var_generated = True
                    break
                else:
                    var_id = None
        else:
            Utils.variables['main_canvas'][var_id] = {
                'name': '',
                'type': 'Int',
                'value': '',
                'widget': None,
                'name_imput': None,
                'type_input': None,
                'value_input': None
            }
        #print(f"Utils.variables after adding new variable: {Utils.variables}")
        canvas_reference.row_widget = QWidget()
        canvas_reference.row_layout = QHBoxLayout(canvas_reference.row_widget)
        canvas_reference.row_layout.setContentsMargins(5, 5, 5, 5)

        name_imput = QLineEdit()
        name_imput.setPlaceholderText("Name")
        if var_data and 'name' in var_data:
            name_imput.setText(var_data['name'])
            Utils.variables['main_canvas'][var_id]['name'] = var_data['name']
        
        name_imput.textChanged.connect(lambda text, v_id=var_id, t="Variable", r=canvas_reference: self.name_changed(text, v_id, t, r))
        
        type_input = QComboBox()
        type_input.addItems(["Int", "Float", "String", "Bool"])
        if var_data and 'type' in var_data:
            type_input.setCurrentText(var_data['type'])
            Utils.variables['main_canvas'][var_id]['type'] = var_data['type']
        
        type_input.currentTextChanged.connect(lambda  text, v_id=var_id, t="Variable", r=canvas_reference: self.type_changed(text, v_id , t, r))
        
        self.value_var_input = QLineEdit()
        self.value_var_input.setPlaceholderText("Initial Value")
        if var_data and 'value' in var_data:
            print(f"Setting initial value for variable {var_id}: {var_data['value']}")
            self.value_var_input.setText(var_data['value'])
            Utils.variables['main_canvas'][var_id]['value'] = var_data['value']
        self.value_var_input.textChanged.connect(lambda text, v_id=var_id, t="Variable", r=canvas_reference: self.value_changed(text, v_id, t, r))
        
        delete_btn = QPushButton("×")
        delete_btn.setFixedWidth(30)
        
        canvas_reference.row_layout.addWidget(name_imput)
        canvas_reference.row_layout.addWidget(type_input)
        canvas_reference.row_layout.addWidget(self.value_var_input)
        canvas_reference.row_layout.addWidget(delete_btn)
        
        delete_btn.clicked.connect(lambda _, v_id=var_id, rw=canvas_reference.row_widget, t="Variable", r=canvas_reference: self.remove_row(rw, v_id, t, r))

        Utils.variables['main_canvas'][var_id]['widget'] = canvas_reference.row_widget
        Utils.variables['main_canvas'][var_id]['name_imput'] = name_imput
        Utils.variables['main_canvas'][var_id]['type_input'] = type_input
        Utils.variables['main_canvas'][var_id]['value_input'] = self.value_var_input

        panel_layout = canvas_reference.var_layout
        panel_layout.insertWidget(panel_layout.count() - 1, canvas_reference.row_widget)
        
        canvas_reference.variable_row_count += 1
        
        #print(f"Added variable: {self.var_id}")
    
    def Clear_All_Variables(self):
        #print("Clearing all variables")
        var_ids_to_remove = []
        # Get a SNAPSHOT of variable IDs BEFORE modifying anything
        for canvas, info in Utils.canvas_instances.items():
            if canvas == info['canvas']:
                var_ids_to_remove += list(Utils.variables['main_canvas'].keys())
            elif canvas == info['function']:
                for function_id, function_info in Utils.functions.items():
                    var_ids_to_remove += list(Utils.variables['function_canvases'][function_id].keys())
        #print(f"Current Utils.variables before clearing: {Utils.variables}")
        #print(f"Variable IDs to remove: {var_ids_to_remove}")
        
        # Now remove them
        try:
            for varid in var_ids_to_remove:
                #print(f"Removing varid: {varid}")
                for canvas, info in Utils.canvas_instances.items():
                    if canvas == info['canvas']:
                        canvas_reference = info['canvas']
                        rowwidget = Utils.variables['main_canvas'][varid]['widget']
                        self.remove_row(rowwidget, varid, 'Variable', canvas_reference)
                    elif canvas == info['canvas']:
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas:
                                canvas_reference = function_info['canvas']
                                rowwidget = Utils.variables['function_canvases'][function_id][varid]['widget']
                                self.remove_row(rowwidget, varid, 'Variable', canvas_reference)
        except Exception as e:
            print(f"Error while clearing variables: {e}")

    #MARK: - Devices Panel Methods
    def add_device_row(self, device_id=None, dev_data=None, canvas_reference=None):
        """Add a new device row"""
        #print(f"Adding device row called with device_id: {device_id}, dev_data: {dev_data}")
        #print(f"Current Utils.devices before adding new device: {Utils.devices}")
        id_dev_generated = False
        if device_id is None:
            while not id_dev_generated:
                device_id = f"device_{str(int(random()*100000))}"
                if device_id not in Utils.devices['main_canvas'].keys():
                    Utils.devices['main_canvas'][device_id] = {
                        'name': '',
                        'type': 'Output',
                        'PIN': '',
                        'widget': None,
                        'name_imput': None,
                        'type_input': None,
                        'value_input': None
                    }
                    id_dev_generated = True
                    break
                else:
                    device_id = None
        else:
            Utils.devices['main_canvas'][device_id] = {
                'name': '',
                'type': 'Output',
                'PIN': '',
                'widget': None,
                'name_imput': None,
                'type_input': None,
                'value_input': None
            }
        #print(f"Generated device_id: {device_id}")
        self.device_id = device_id
        #print(f"Adding device row {self.device_id}, dev_data: {dev_data}. Current devices: {Utils.devices}")

        canvas_reference.row_widget = QWidget()
        canvas_reference.row_layout = QHBoxLayout(canvas_reference.row_widget)
        canvas_reference.row_layout.setContentsMargins(5, 5, 5, 5)
 
        name_imput = QLineEdit()
        name_imput.setPlaceholderText("Name")
        if dev_data and 'name' in dev_data:
            name_imput.setText(dev_data['name'])
            Utils.devices['main_canvas'][device_id]['name'] = dev_data['name']
        
        name_imput.textChanged.connect(lambda text, d_id=device_id, t="Device", r=canvas_reference: self.name_changed(text, d_id, t, r))
        
        type_input = QComboBox()
        type_input.addItems(["Output", "Input", "PWM", "Button"])
        if dev_data and 'type' in dev_data:
            type_input.setCurrentText(dev_data['type'])
            Utils.devices['main_canvas'][device_id]['type'] = dev_data['type']
        
        type_input.currentTextChanged.connect(lambda text, d_id=device_id, t="Device", r=canvas_reference: self.type_changed(text, d_id, t, r))
        
        self.value_dev_input = QLineEdit()
        self.value_dev_input.setPlaceholderText("PIN")
        if dev_data and 'PIN' in dev_data:
            print(f"Setting initial PIN value for device {device_id}: {dev_data['PIN']}")
            self.value_dev_input.setText(str(dev_data['PIN']))
            Utils.devices['main_canvas'][device_id]['PIN'] = dev_data['PIN']

        regex = QRegularExpression(r"^\d*$")
        validator = QRegularExpressionValidator(regex, self)
        self.value_dev_input.setValidator(validator)
        self.value_dev_input.textChanged.connect(lambda text, d_id=device_id, t="Device", r=canvas_reference: self.value_changed(text, d_id, t, r))
        
        delete_btn = QPushButton("×")
        delete_btn.setFixedWidth(30)
        
        canvas_reference.row_layout.addWidget(name_imput)
        canvas_reference.row_layout.addWidget(type_input)
        canvas_reference.row_layout.addWidget(self.value_dev_input)
        canvas_reference.row_layout.addWidget(delete_btn)
        
        delete_btn.clicked.connect(lambda _, d_id=device_id, rw=canvas_reference.row_widget, t="Device", r=canvas_reference: self.remove_row(rw, d_id, t, r))
        
        panel_layout = canvas_reference.dev_layout
        panel_layout.insertWidget(panel_layout.count() - 1, canvas_reference.row_widget)
        
        canvas_reference.devices_row_count += 1
        Utils.devices['main_canvas'][device_id]['widget'] = canvas_reference.row_widget
        Utils.devices['main_canvas'][device_id]['name_imput'] = name_imput
        Utils.devices['main_canvas'][device_id]['type_input'] = type_input
        Utils.devices['main_canvas'][device_id]['value_input'] = self.value_dev_input
        
    def Clear_All_Devices(self):
        #print("Clearing all devices")
        dev_ids_to_remove = []
        # Get a SNAPSHOT of variable IDs BEFORE modifying anything
        for canvas, info in Utils.canvas_instances.items():
            if canvas == info['canvas']:
                dev_ids_to_remove += list(Utils.devices['main_canvas'].keys())
            elif canvas == info['function']:
                for function_id, function_info in Utils.functions.items():
                    dev_ids_to_remove += list(Utils.devices['function_canvases'][function_id].keys())
        #print(f"Current Utils.devices before clearing: {Utils.devices}")
        #print(f"Device IDs to remove: {dev_ids_to_remove}")
        # Now remove them
        try:
            for device_id in dev_ids_to_remove:
                #print(f"Removing device_id: {device_id}")
                for canvas, info in Utils.canvas_instances.items():
                    if canvas == info['canvas']:
                        canvas_reference = info['canvas']
                        rowwidget = Utils.devices['main_canvas'][device_id]['widget']
                        self.remove_row(rowwidget, device_id, 'Device', canvas_reference)
                    elif canvas == info['function']:
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas:
                                canvas_reference = function_info['canvas']
                                rowwidget = Utils.devices['function_canvases'][function_id][device_id]['widget']
                                self.remove_row(rowwidget, device_id, 'Device', canvas_reference)
        except Exception as e:
            print(f"Error while clearing devices: {e}")
    
    #MARK: - Common Methods
    def remove_row(self, row_widget, var_id, type, canvas_reference=None):
        """Remove a variable row"""
        #print(f"Removing row {var_id} of type {type}")
        if type == "Variable":
                
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        del Utils.variables['main_canvas'][var_id]
                        for imput, var_ids in Utils.vars_same.items():
                            if var_id in var_ids:
                                var_ids.remove(var_id)
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                del Utils.variables['function_canvases'][function_id][var_id]
                                for imput, var_ids in Utils.vars_same.items():
                                    if var_id in var_ids:
                                        var_ids.remove(var_id)
                                break
            
            for imput2, var in Utils.vars_same.items():
                #print(f"Var {var}, len var {len(var)}")
                if len(var) <= 1:
                    for var_id in var:
                        if info['ref'] == 'canvas':
                            Utils.variables['main_canvas'][var_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
                        elif info['ref'] == 'function':
                            Utils.variables['function_canvases'][function_id][var_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
            
            panel_layout = canvas_reference.var_layout
            panel_layout.removeWidget(row_widget)
            
            row_widget.setParent(None)
            row_widget.deleteLater()
            
            canvas_reference.variable_row_count -= 1
        elif type == "Device":
                
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        del Utils.devices['main_canvas'][var_id]
                        for imput, dev_ids in Utils.devs_same.items():
                            if var_id in dev_ids:
                                dev_ids.remove(var_id)
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                del Utils.devices['function_canvases'][function_id][var_id]
                                for imput, dev_ids in Utils.devs_same.items():
                                    if var_id in dev_ids:
                                        dev_ids.remove(var_id)
                                break
            
            for imput2, dev in Utils.devs_same.items():
                #print(f"Dev {dev}, len dev {len(dev)}")
                if len(dev) <= 1:
                    for dev_id in dev:
                        if info['ref'] == 'canvas':
                            Utils.devices['main_canvas'][dev_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
                        elif info['ref'] == 'function':
                            Utils.devices['function_canvases'][function_id][dev_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
            
            panel_layout = canvas_reference.dev_layout
            panel_layout.removeWidget(row_widget)
            
            row_widget.setParent(None)
            row_widget.deleteLater()
            
            canvas_reference.devices_row_count -= 1
        #print(f"Deleted variable: {var_id}")
    
    def remove_internal_row(self, row_widget, var_id, type, canvas_reference=None):
        if type == "Variable":
                
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        pass
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                del Utils.variables['function_canvases'][function_id][var_id]
                                for imput, var_ids in Utils.vars_same.items():
                                    if var_id in var_ids:
                                        var_ids.remove(var_id)
                                break
            
            for imput2, var in Utils.vars_same.items():
                #print(f"Var {var}, len var {len(var)}")
                if len(var) <= 1:
                    for var_id in var:
                        if info['ref'] == 'canvas':
                            pass
                        elif info['ref'] == 'function':
                            Utils.variables['function_canvases'][function_id][var_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
            
            panel_layout = canvas_reference.internal_layout
            panel_layout.removeWidget(row_widget)
            
            row_widget.setParent(None)
            row_widget.deleteLater()
            
        elif type == "Device":

            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        pass
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                del Utils.devices['function_canvases'][function_id][var_id]
                                for imput, dev_ids in Utils.devs_same.items():
                                    if var_id in dev_ids:
                                        dev_ids.remove(var_id)
                                break
            
            for imput2, dev in Utils.devs_same.items():
                #print(f"Dev {dev}, len dev {len(dev)}")
                if len(dev) <= 1:
                    for dev_id in dev:
                        if info['ref'] == 'canvas':
                            pass
                        elif info['ref'] == 'function':
                            Utils.devices['function_canvases'][function_id][dev_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
            
            panel_layout = canvas_reference.internal_layout
            panel_layout.removeWidget(row_widget)
            
            row_widget.setParent(None)
            row_widget.deleteLater()
            

    def name_changed(self, text, var_id, type, canvas_reference=None):
        #print(f"Name changed to {text} for {type} with id {var_id}")
        if type == "Variable":
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        Utils.variables['main_canvas'][var_id]['name'] = text
                        break
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                Utils.variables['function_canvases'][function_id][var_id]['name'] = text
                                break
            #print(f"Utils.variables before name change: {Utils.variables}")
            # Step 1: Group all var_ids by their name value
            Utils.vars_same.clear() 
            if info['ref'] == 'canvas':
                Utils.variables['main_canvas'][var_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
            elif info['ref'] == 'function':
                Utils.variables['function_canvases'][function_id][var_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
            if info['ref'] == 'canvas':
                for v_id, v_info in Utils.variables['main_canvas'].items():
                    name = v_info['name_imput'].text().strip()
                    if name:
                        Utils.vars_same.setdefault(name, []).append(v_id)
            elif info['ref'] == 'function':
                for v_id, v_info in Utils.variables['function_canvases'][function_id].items():
                    name = v_info['name_imput'].text().strip()
                    if name:
                        Utils.vars_same.setdefault(name, []).append(v_id)
            
            # Step 2: Color red if duplicate
            for name, id_list in Utils.vars_same.items():
                #print(id_list)
                border_col = "border-color: #ff0000;" if len(id_list) > 1 else "border-color: #3F3F3F;"
                if info['ref'] == 'canvas':
                    for v_id in id_list:
                        Utils.variables['main_canvas'][v_id]['name_imput'].setStyleSheet(border_col)
                elif info['ref'] == 'function':                
                    for v_id in id_list:
                        Utils.variables['function_canvases'][function_id][v_id]['name_imput'].setStyleSheet(border_col)
            #print("Utils.variables:", Utils.variables)
        
        elif type == "Device":
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        Utils.devices['main_canvas'][var_id]['name'] = text
                        break
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                Utils.devices['function_canvases'][function_id][var_id]['name'] = text
                                break
            #print(f"Utils.devices before name change: {Utils.devices}")
            # Step 1: Group all var_ids by their name value
            Utils.devs_same.clear() 
            if info['ref'] == 'canvas':
                Utils.devices['main_canvas'][var_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
            elif info['ref'] == 'function':
                Utils.devices['function_canvases'][function_id][var_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
            if info['ref'] == 'canvas':
                for d_id, d_info in Utils.devices['main_canvas'].items():
                    name = d_info['name_imput'].text().strip()
                    if name:
                        Utils.devs_same.setdefault(name, []).append(d_id)
            elif info['ref'] == 'function':
                for d_id, d_info in Utils.devices['function_canvases'][function_id].items():
                    name = d_info['name_imput'].text().strip()
                    if name:
                        Utils.devs_same.setdefault(name, []).append(d_id)
            
            # Step 2: Color red if duplicate
            for name, id_list in Utils.devs_same.items():
                #print(id_list)
                border_col = "border-color: #ff0000;" if len(id_list) > 1 else "border-color: #3F3F3F;"
                if info['ref'] == 'canvas':
                    for d_id in id_list:
                        Utils.devices['main_canvas'][d_id]['name_imput'].setStyleSheet(border_col)
                elif info['ref'] == 'function':                
                    for d_id in id_list:
                        Utils.devices['function_canvases'][function_id][d_id]['name_imput'].setStyleSheet(border_col)
            #print("Utils.devices:", Utils.devices)
    
    def type_changed(self, imput, id, type, canvas_reference=None):
        #print(f"Updating variable {imput}")
        if type == "Variable":
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        Utils.variables['main_canvas'][id]['type'] = imput
                        break
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                Utils.variables['function_canvases'][function_id][id]['type'] = imput
                                break
        elif type == "Device":
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        Utils.devices['main_canvas'][id]['type'] = imput
                        break
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                Utils.devices['function_canvases'][function_id][id]['type'] = imput
                                break
    
    def value_changed(self, imput, id, type, canvas_reference=None):
        #print(f"Updating variable {imput}")
        
        if type == "Variable":
            try:
                value = len(imput)
                for v_id, v_info in Utils.variables['main_canvas'].items():
                    if v_id == id:
                        v_type = Utils.variables['main_canvas'][id]['type']
                        break
                print(f"Variable {id} of type {v_type} changed to value: {imput}")
                
                if v_type == "Int" and int(imput) > sys.maxsize:
                    self.value_var_input.blockSignals(True)
                    self.value_var_input.setText(str(sys.maxsize))
                    imput = str(sys.maxsize)
                    self.value_var_input.blockSignals(False)
                if v_type == "Int" and int(imput) < -sys.maxsize-1:
                    self.value_var_input.blockSignals(True)
                    self.value_var_input.setText(str(-sys.maxsize-1))
                    imput = str(-sys.maxsize-1)
                    self.value_var_input.blockSignals(False)
                if v_type == "Float" and float(imput) > sys.maxsize:
                    self.value_var_input.blockSignals(True)
                    self.value_var_input.setText(str(sys.maxsize))
                    imput = str(sys.maxsize)
                    self.value_var_input.blockSignals(False)
                if v_type == "Float" and float(imput) < -sys.maxsize-1:
                    self.value_var_input.blockSignals(True)
                    self.value_var_input.setText(str(-sys.maxsize-1))
                    imput = str(-sys.maxsize-1)
                    self.value_var_input.blockSignals(False)
                if v_type == "Bool" and int(imput) > 1:
                    self.value_var_input.blockSignals(True)
                    self.value_var_input.setText("1")
                    imput = "1"
                    self.value_var_input.blockSignals(False)
                if v_type == "Bool" and int(imput) < 0:
                    self.value_var_input.blockSignals(True)
                    self.value_var_input.setText("0")
                    imput = "0"
                    self.value_var_input.blockSignals(False)


            except ValueError:
                    # Text is empty or can't convert (shouldn't happen with regex)
                    pass
            
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        Utils.variables['main_canvas'][id]['value'] = imput
                        break
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                Utils.variables['function_canvases'][function_id][id]['value'] = imput
                                break
        elif type == "Device":
            try:
                if int(imput) > 40:
                    self.value_dev_input.blockSignals(True)
                    self.value_dev_input.setText("40")
                    imput = "40"
                    self.value_dev_input.blockSignals(False)
                
                if int(imput) < 0:
                    self.value_dev_input.blockSignals(True)
                    self.value_dev_input.setText("0")
                    imput = "0"
                    self.value_dev_input.blockSignals(False)
            except ValueError:
                    # Text is empty or can't convert (shouldn't happen with regex)
                    pass
            for canvas, info in Utils.canvas_instances.items():
                if canvas_reference == canvas:
                    if info['ref'] == 'canvas':
                        Utils.devices['main_canvas'][id]['PIN'] = imput
                        break
                    elif info['ref'] == 'function':
                        for function_id, function_info in Utils.functions.items():
                            if function_info['canvas'] == canvas_reference:
                                Utils.devices['function_canvases'][function_id][id]['PIN'] = imput
                                break    
    #MARK: - Other Methods
    def open_elements_window(self):
        """Open the elements window"""
        #print("Opening elements window")
        elements_window = ElementsWindow.get_instance(self.current_canvas)
        print("Elements window instance:", elements_window)
        try:
            print("Checking if elements dialog can be opened...")
            if self.state_manager.app_state.on_elements_dialog_open():
                print("Opening elements dialog...")
                elements_window.open()
        except Exception as e:
            print(f"Error opening elements window: {e}")
    
    def open_settings_window(self):
        """Open the device settings window"""
        settings_window = DeviceSettingsWindow.get_instance(self.current_canvas)
        if self.state_manager.app_state.on_settings_dialog_open():
            settings_window.open()
    
    def open_help(self, which):
        """Open the help window"""
        help_window = HelpWindow.get_instance(self.current_canvas, which)
        if self.state_manager.app_state.on_help_dialog_open():
            help_window.open()
    
    def view_generated_code(self):
        """View the generated code"""
        code_viewer = CodeViewerWindow.get_instance(self.current_canvas)
        if self.state_manager.app_state.on_code_viewer_dialog_open():
            code_viewer.open()

    def block_management(self, block_id, window):
        """Track block windows"""
        self.blockIDs[block_id] = window
    
    def compile_code(self):
        """Compile the visual code"""
        try:
            #print("Starting code compilation...")
            self.code_compiler.compile()
            #print("Code compiled successfully")
        except Exception as e:
            print(f"Compilation error: {e}")
            pass
    
    # Menu actions
    
    def create_save_shortcut(self):
        """Create Ctrl+S keyboard shortcut for saving"""
        from PyQt6.QtGui import QKeySequence, QShortcut
        #print("Creating save shortcut (Ctrl+S)")
        save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        save_shortcut.activated.connect(self.on_save_file)
    
    def setup_auto_save_timer(self):
        """Setup auto-save timer for every 5 minutes"""
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_project)
        
        # 5 minutes = 300,000 milliseconds
        self.auto_save_timer.start(300000)  # 300000 ms = 5 minutes
        
        #print("✓ Auto-save timer started (every 5 minutes)")
    
    def get_current_time(self):
        """Get current time for logging"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def auto_save_project(self):
        """Auto-save current project"""
        name = Utils.project_data.metadata.get('name', 'Untitled')
        #print(f"Auto-saving project '{name}'")
        try:
            if FileManager.save_project(name, is_autosave=True):
                #print(f"✓ Auto-saved '{name}' at {self.get_current_time()}")
                pass
            else:
                print(f"✗ Auto-save failed for '{name}'")
        except Exception as e:
            print(f"✗ Auto-save error: {e}")

    def on_save_file(self):
        """Save current project"""
        
        name = Utils.project_data.metadata.get('name', 'Untitled')
        if name == 'Untitled':
            self.on_save_file_as()
            return
        #print(f"Metadata: {Utils.project_data.metadata}")
        #print(f"Saving project as '{name}'")
        if FileManager.save_project(name):
            print(f"✓ Project '{name}' saved")

    def on_save_file_as(self):
        """Save current project with new name"""
        
        text, ok = QInputDialog.getText(self, "Save Project As", 
            "Enter project name:", QLineEdit.EchoMode.Normal, 
            Utils.project_data.metadata.get('name', ''))
        
        if ok and text:
            Utils.project_data.metadata['name'] = text
            if FileManager.save_project(text):
                print(f"✓ Project saved as '{text}'")
        
    def on_open_file(self):
        """Open saved project"""
        
        projects = FileManager.list_projects()
        if not projects:
            QMessageBox.information(self, "No Projects", "No saved projects found")
            return
        
        items = [p['name'] for p in projects]
        item, ok = QInputDialog.getItem(self, "Open Project", 
            "Select project:", items, 0, False)
        
        if ok and item:
            self.wipe_canvas()
            if FileManager.load_project(item):
                self.rebuild_from_data()
                #print(f"✓ Project '{item}' loaded")

    def clear_canvas(self):
        """Clear the canvas of all blocks and connections"""
        self.Clear_All_Variables()
        self.Clear_All_Devices()
        for canvas in Utils.canvas_instances.keys():
            #print("Clearing canvas:", canvas)
            if canvas:
                canvas.path_manager.clear_all_paths()
                #print("Cleared all paths")
                widget_ids_to_remove = []
                if canvas.reference == 'canvas':
                    widget_ids_to_remove += list(Utils.main_canvas['blocks'].keys())
                    #print(f"Widget IDs to remove from main canvas: {widget_ids_to_remove}")
                elif canvas.reference == 'function':
                    #print("Clearing function canvas")
                    for f_id, f_info in Utils.functions.items():
                        if canvas == f_info.get('canvas'):
                            widget_ids_to_remove += list(Utils.functions[f_id]['blocks'].keys())
                            #print(f"Widget IDs to remove from function {f_id} canvas: {widget_ids_to_remove}")
                for widget_id in widget_ids_to_remove:
                    if widget_id in Utils.main_canvas['blocks'].keys():
                        block_widget = Utils.main_canvas['blocks'][widget_id]['widget']
                        canvas.remove_block(block_widget)
                        #print(f"Removed block {widget_id} from main canvas")
                    else:
                        for f_id, f_info in Utils.functions.items():
                            if widget_id in Utils.functions[f_id]['blocks'].keys():
                                block_widget = Utils.functions[f_id]['blocks'][widget_id]['widget']
                                canvas.remove_block(block_widget)
                                #print(f"Removed block {widget_id} from function {f_id} canvas")
                QCoreApplication.processEvents()
                
                canvas.update()
    
    def wipe_canvas(self):
        self.close_child_windows()
        
        self.clear_canvas()
        
        self.delete_canvas_instance()
        
        FileManager.new_project()

        ElementsWindow._instance = None

        Utils.variables = {
            'main_canvas': {},
            'function_canvases': {}
        }
        Utils.devices = {
            'main_canvas': {},
            'function_canvases': {}
        }
        self.variable_frame = None
        self.variable_frame_visible = False
        self.variable_row_count = 1
        self.Devices_frame = None
        self.devices_frame_visible = False
        self.devices_row_count = 1
        self.last_canvas = None
        self.blockIDs = {}
        self.execution_thread = None
        self.canvas_added = None
        self.pages = {}
        self.page_count = 0
        self.count_w_separator = 0
        self.canvas_count = 0
        self.tab_buttons = []  # Track tab buttons
        
        self.central_widget.setParent(None)
        self.central_widget.deleteLater()
    
    def on_new_file(self):
        """Create new project"""
        self.wipe_canvas()
        
        self.create_canvas_frame()
        
    def delete_canvas_instance(self):
        """Delete a canvas instance from tracking"""
        canvases_to_delete = {}
        for canvas_key, info in list(Utils.canvas_instances.items()):
            canvases_to_delete[canvas_key] = info['canvas']
            if info['ref'] == 'canvas':
                #print(f"Preparing to delete main canvas instance: {canvas_key}")
                canvas_key.new_canvas_button.setParent(None)
                canvas_key.new_canvas_button.deleteLater()

        for canvas in canvases_to_delete:
            #print(f"Deleted canvas instance: {canvas}")
            if canvas.reference == 'canvas':
                canvas.var_button.setParent(None)
                canvas.dev_button.setParent(None)
                canvas.canvas_tab_button.setParent(None)
                canvas.var_button.deleteLater()
                canvas.dev_button.deleteLater()
                canvas.canvas_tab_button.deleteLater()
            elif canvas.reference == 'function':
                canvas.internal_var_button.setParent(None)
                canvas.canvas_tab_button.setParent(None)
                canvas.internal_var_button.deleteLater()
                canvas.canvas_tab_button.deleteLater()
            
            canvas.deleteLater()     
            del Utils.canvas_instances[canvas]
            self.remove_excess_separators(canvas)
    
    def remove_excess_separators(self, content_widget):
        """
        Deletes ALL separators for a canvas if it has more than one.
        """
        # Check if the list exists and has more than 1 item
        #print(f"Checking separators for canvas: {content_widget}")
        #print(f"Current separators: {getattr(content_widget, 'separators', None)}")
        if hasattr(content_widget, 'separators') and len(content_widget.separators) >= 1:
            #print(f"Found {len(content_widget.separators)} separators. Deleting all...")
            
            # Iterate through the list and remove each separator
            for sep in content_widget.separators:
                sep.setParent(None)
                sep.deleteLater()
                
                # IMPORTANT: Decrement the layout counter to keep indices correct
                self.count_w_separator -= 1

            # Clear the list and the single reference
            content_widget.separators.clear()
            content_widget.separator_container = None
            
            #print("All separators deleted.")    
    
    def closeEvent(self, event):
        """Handle window close event - prompt to save if there are unsaved changes"""
        
        # Stop auto-save timer
        if hasattr(self, 'auto_save_timer') and self.auto_save_timer.isActive():
            self.auto_save_timer.stop()
        
        # Stop execution thread
        if hasattr(self, 'execution_thread') and self.execution_thread is not None:
            if self.execution_thread.isRunning():
                self.execution_thread.stop()
                self.execution_thread.wait(3000)
                self.execution_thread.terminate()
        
        name = Utils.project_data.metadata.get("name", "Untitled")
        
        if name == "Untitled":
            # Check if untitled project has any content
            has_content = (
                len(Utils.main_canvas.get("blocks", {})) > 0 or
                len(Utils.functions) > 0 or
                len(Utils.variables.get("main_canvas", {})) > 0 or
                len(Utils.devices.get("main_canvas", {})) > 0
            )
            
            if not has_content:
                # Empty untitled project, just close
                self.clear_canvas()
                self.close_child_windows()
                import gc
                gc.collect()
                event.accept()
                return
            
            # Has content but untitled
            reply = QMessageBox.question(
                self, "Save Project?",
                f"Save untitled project before closing?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.on_save_file_as()
            elif reply != QMessageBox.StandardButton.Discard:
                event.ignore()
                return
        
        else:
            # Compare with saved version
            comparison = FileManager.compare_projects(name)
            print(f"Comparison result for '{name}': {comparison}")
            print(f"Has changes: {comparison.has_changes}")
            if comparison.has_changes:
                print("Unsaved changes detected, prompting user")
                change_summary = self.build_change_summary(comparison)
                reply = QMessageBox.question(
                    self, "Save Project?",
                    f"Do you want to save changes to '{name}' before closing?\n\n{change_summary}",
                    QMessageBox.StandardButton.Save |
                    QMessageBox.StandardButton.Discard |
                    QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Save
                )
                
                if reply == QMessageBox.StandardButton.Save:
                    FileManager.save_project(name)
                elif reply != QMessageBox.StandardButton.Discard:
                    event.ignore()
                    return
        
        # Cleanup and close
        self.clear_canvas()
        self.close_child_windows()
        import gc
        gc.collect()
        event.accept()
    
    def build_change_summary(self, comparison) -> str:
        """Build detailed human-readable summary from ProjectComparison"""
        summary = []
        print(f"Building change summary from comparison: {comparison}")
        # Main Canvas Changes
        if comparison.main_canvas_changed:
            print("Main canvas changes detected")
            main_details = []
            if comparison.main_blocks_added:
                main_details.append(f"  ✓ {len(comparison.main_blocks_added)} block(s) added")
            if comparison.main_blocks_removed:
                main_details.append(f"  ✓ {len(comparison.main_blocks_removed)} block(s) removed")
            if comparison.main_blocks_modified:
                main_details.append(f"  ✓ {len(comparison.main_blocks_modified)} block(s) modified")
            if comparison.main_connections_added:
                main_details.append(f"  ✓ {len(comparison.main_connections_added)} connection(s) added")
            if comparison.main_connections_removed:
                main_details.append(f"  ✓ {len(comparison.main_connections_removed)} connection(s) removed")
            
            if main_details:
                summary.append("📋 Main Canvas:")
                summary.extend(main_details)
        
        # Function Canvas Changes
        if comparison.function_canvases_changed:
            print("Function canvas changes detected")
            func_details = []
            if comparison.function_canvases_added:
                func_details.append(f"  ✓ {len(comparison.function_canvases_added)} function(s) added")
            if comparison.function_canvases_removed:
                func_details.append(f"  ✓ {len(comparison.function_canvases_removed)} function(s) removed")
            if comparison.function_blocks_modified:
                func_details.append(f"  ✓ {len(comparison.function_blocks_modified)} function(s) with block changes")
            if comparison.function_connections_modified:
                func_details.append(f"  ✓ {len(comparison.function_connections_modified)} function(s) with connection changes")
            
            if func_details:
                summary.append("⚙️ Functions:")
                summary.extend(func_details)
        
        # Variables Changes
        if comparison.variables_changed:
            print("Variable changes detected")
            var_details = []
            if comparison.variables_added:
                var_details.append(f"  ✓ {len(comparison.variables_added)} variable(s) added")
            if comparison.variables_removed:
                var_details.append(f"  ✓ {len(comparison.variables_removed)} variable(s) removed")
            if comparison.variables_modified:
                var_details.append(f"  ✓ {len(comparison.variables_modified)} variable(s) modified")
            
            if var_details:
                summary.append("📊 Variables:")
                summary.extend(var_details)
        
        # Devices Changes
        if comparison.devices_changed:
            print("Device changes detected")
            dev_details = []
            if comparison.devices_added:
                dev_details.append(f"  ✓ {len(comparison.devices_added)} device(s) added")
            if comparison.devices_removed:
                dev_details.append(f"  ✓ {len(comparison.devices_removed)} device(s) removed")
            if comparison.devices_modified:
                dev_details.append(f"  ✓ {len(comparison.devices_modified)} device(s) modified")
            
            if dev_details:
                summary.append("🔌 Devices:")
                summary.extend(dev_details)
        
        # Settings Changes
        if comparison.settings_changed:
            summary.append(f"⚡ Settings: {len(comparison.settings_modified)} setting(s) changed")
        
        if not summary:
            print("No changes detected")
            return "✓ No changes detected."
        
        return "Unsaved Changes Detected:\n\n" + "\n".join(summary)
        
    def close_child_windows(self):
        
        # Close Elements window if it exists
        try:
            if ElementsWindow._instance is not None:
                if ElementsWindow._instance.isVisible():
                    ElementsWindow._instance.close()
                ElementsWindow._instance = None
        except:
            # If instance already deleted, just reset
            ElementsWindow._instance = None
        
        # Close Device Settings window if it exists
        try:
            device_settings_window = DeviceSettingsWindow.get_instance(self.current_canvas)
            if device_settings_window.isVisible():
                device_settings_window.close()
        except:
            pass
        
        try:
            help_window = HelpWindow.get_instance(self.current_canvas)
            if help_window.isVisible():
                help_window.close()
        except:
            pass
    #MARK: - Compile and Upload Methods
    def compile_and_upload(self):
        """
        Main compile and upload method.
        Updated to properly handle RPi execution.
        """
        try:
            # Show compilation message
            QMessageBox.information(
                self,
                "Compiling...",
                "Compiling your code and preparing upload...",
                QMessageBox.StandardButton.Ok
            )
            
            # ===== STEP 1: Compile code =====
            #print("📝 Step 1: Compiling code...")
            self.code_compiler.compile()  # This creates File.py
            #print("✓ Code compiled successfully to File.py")
            
            # ===== STEP 2: Show compiled output =====
            try:
                with open('File.py', 'r') as f:
                    compiled_code = f.read()
                print("--- Generated Code ---")
                print(compiled_code)
                print("--- End of Code ---")
            except FileNotFoundError:
                print("⚠️  Warning: Could not read compiled File.py")
            
            # ===== STEP 3: Execute based on device type =====
            #print("🚀 Step 3: Executing on device...")
            
            rpi_model = Utils.app_settings.rpi_model_index
            
            if rpi_model == 0:  # Pico W
                #print("🎯 Target: Pico W (MicroPython)")
                if self.execute_on_pico_w():
                    #print("✓ Code executed successfully!")
                    QMessageBox.information(
                        self,
                        "Success",
                        "Code compiled, executed, and uploaded successfully!",
                        QMessageBox.StandardButton.Ok
                    )
                else:
                    #print("⚠️  Execution warning - Check device connection")
                    QMessageBox.warning(
                        self,
                        "Execution Issue",
                        "Code compiled but execution encountered issues. Check device connection and try again.",
                        QMessageBox.StandardButton.Ok
                    )
            
            elif rpi_model in [1, 2, 3, 4, 5, 6, 7]:  # Raspberry Pi
                #print(f"🎯 Target: Raspberry Pi (GPIO) - Model {rpi_model}")
                #Execute on RPi in background thread
                self.execute_on_rpi_ssh_background()
                
                #print("✓ Execution started on Raspberry Pi")
                # Show info (don't show success here - let thread signals handle it)
                QMessageBox.information(
                    self,
                    "Execution Started",
                    "Code is being executed on your Raspberry Pi.\nCheck the status messages for updates.",
                    QMessageBox.StandardButton.Ok
                )
            
            else:
                print("❌ Unknown device model")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Unknown device model: {rpi_model}",
                    QMessageBox.StandardButton.Ok
                )
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            QMessageBox.critical(
                self,
                "Compilation Error",
                f"Failed to compile code:\n{str(e)}",
                QMessageBox.StandardButton.Ok
            )
    
    # ===== Signal handlers for thread communication =====
    
    def on_execution_status(self, status):
        """Handle status updates from execution thread"""
        #print(f"[RPi Status] {status}")
    
    def on_execution_output(self, output):
        """Handle output from execution thread"""
        #print(f"[RPi Output] {output}")
        QMessageBox.information(
            self,
            "Execution Output",
            output,
            QMessageBox.StandardButton.Ok
        )
    
    def on_execution_error(self, error):
        """Handle errors from execution thread"""
        #print(f"[RPi Error] {error}")
        QMessageBox.critical(
            self,
            "Execution Error",
            error,
            QMessageBox.StandardButton.Ok
        )

    def execute_on_pico_w(self):
        """
        Execute on Pico W using pyboard.py (already imported)
        """
        try:
            import subprocess
            
            # Method 1: Using mpremote (if available)
            try:
                #print("Attempting to use mpremote...")
                # mpremote will automatically detect and connect to Pico W
                result = subprocess.run(
                    ["mpremote", "cp", "File.py", ":/main.py"],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if result.returncode == 0:
                    #print("✓ File uploaded via mpremote")
                    
                    # Run the code
                    result = subprocess.run(
                        ["mpremote", "run", "main.py"],
                        capture_output=True,
                        text=True,
                        timeout=15
                    )
                    
                    if result.returncode == 0:
                        #print("✓ Code executed successfully")
                        if result.stdout:
                            #print(f"Output: {result.stdout}")
                            pass
                        return True
                    else:
                        print(f"⚠ Execution error: {result.stderr}")
                        return False
                else:
                    raise Exception("mpremote cp failed")
                    
            except (FileNotFoundError, subprocess.TimeoutExpired):
                # Fallback: Use pyboard.py
                #print("Attempting fallback: pyboard.py method...")
                return self.execute_on_pico_w_pyboard()
        
        except Exception as e:
            print(f"❌ Pico W execution error: {e}")
            return False

    def execute_on_pico_w_pyboard(self):
        """
        Fallback: Execute on Pico W using pyboard.py
        """
        try:
            import subprocess
            
            # Assuming pyboard.py is in the same directory
            result = subprocess.run(
                [
                    "python", "pyboard.py",
                    "--device", "/dev/ttyACM0",  # Adjust for your system
                    "File.py"
                ],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                #print("✓ Code executed via pyboard.py")
                if result.stdout:
                    #print(f"Output: {result.stdout}")
                    pass
                return True
            else:
                print(f"⚠ Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Pyboard execution error: {e}")
            return False

    def execute_on_rpi_ssh_background(self):
        """
        Execute code on RPi in background thread.
        This replaces the old execute_on_rpi_ssh_background() method.
        """
        try:
            # ===== STEP 1: Stop old execution if running =====
            if self.execution_thread is not None and self.execution_thread.isRunning():
                #print("[MainWindow] ⏹️  Stopping previous execution...")
                self.execution_thread.stop()  # Signal it to stop
                
                # Wait for thread to finish (max 5 seconds)
                if not self.execution_thread.wait(5000):
                    #print("[MainWindow] ⚠️  Warning: Thread didn't stop gracefully")
                    # Optional: Force terminate (not recommended, but available)
                    # self.execution_thread.terminate()
                    pass
                
                #print("[MainWindow] ✓ Previous execution stopped")
            
            # ===== STEP 2: Get RPi settings =====
            rpi_host = Utils.app_settings.rpi_host
            rpi_user = Utils.app_settings.rpi_user
            rpi_password = Utils.app_settings.rpi_password
            
            if not rpi_host or not rpi_user:
                QMessageBox.warning(
                    self,
                    "Configuration Error",
                    "Raspberry Pi not configured. Go to Settings.",
                    QMessageBox.StandardButton.Ok
                )
                return
            
            # ===== STEP 3: Create new thread =====
            ssh_config = {
                'filepath': 'File.py',  # Your compiled file
                'rpi_host': rpi_host,
                'rpi_user': rpi_user,
                'rpi_password': rpi_password,
            }
            
            self.execution_thread = RPiExecutionThread(ssh_config)
            
            # Connect signals to UI slots
            self.execution_thread.status.connect(self.on_execution_status)
            self.execution_thread.output.connect(self.on_execution_output)
            self.execution_thread.error.connect(self.on_execution_error)
            
            # ===== STEP 4: Start execution =====
            self.execution_thread.start()
            #print("[MainWindow] ✓ New execution started")
        
        except Exception as e:
            print(f"[MainWindow] ❌ Error: {str(e)}")
            QMessageBox.critical(
                self,
                "Execution Error",
                f"Failed to start execution: {str(e)}",
                QMessageBox.StandardButton.Ok
            ) 
    #MARK: - Rebuild UI from Saved Data
    def rebuild_from_data(self):
        """
        Reconstruct the entire UI from Utils.project_data
        
        Called after loading a project file.
        
        Rebuilds:
        1. All blocks on canvas with their positions
        2. All connections between blocks
        3. Variables in the side panel
        4. Devices in the side panel
        """
        #print("Starting rebuild from saved data...")
        
        self.rebuild_canvas_instances()
        
        self._rebuild_settings()
        
        # Rebuild variable panel
        self._rebuild_variables_panel()
        
        # Rebuild devices panel
        self._rebuild_devices_panel()
        
        # Clear canvas and rebuild blocks
        self._rebuild_blocks()
        
        # Rebuild connections
        self._rebuild_connections()
        
        
        #print("✓ Project rebuild complete")

    def rebuild_canvas_instances(self):
        """Rebuild canvas instances from project data"""
        #print("Rebuilding canvas instances...")
        # Recreate main canvas
        self.create_canvas_frame()
        #print("Main canvas recreated")
        
        # Recreate function canvases
        #print(f"Recreating {len(Utils.project_data.canvases)-1} function canvases from project data...")
        #print(f" Canvas data: {Utils.project_data.canvases}")
        for canvas, canvas_info in Utils.project_data.canvases.items():
            print(f" Recreating canvas: {canvas_info['name']} (Ref: {canvas_info['ref']})")
            name = canvas_info['name']
            if canvas_info['ref'] == 'main_canvas':
                print(" Skipping main canvas, already created")
                continue  # Skip main canvas, already created
            elif canvas_info['ref'] == 'function':
                print(f" Creating function canvas: {canvas_info['name']}")
                new_canvas = GridCanvas()
                new_canvas.main_window = self
                new_tab_index = self.add_tab(
                    tab_name=canvas_info['name'],
                    content_widget=new_canvas,
                    reference="function",
                    function_id=canvas_info['id']
                )
                Utils.canvas_instances[new_canvas] = {
                    'canvas': new_canvas,
                    'index': new_tab_index,
                    'ref': 'function',
                    'name': name,
                    'id': canvas_info['id']
                }
        
        #print("Canvas instances rebuilt")
    
    def _rebuild_settings(self):
        """Rebuild settings from project_data"""
        #print(f"Rebuilding {len(Utils.project_data.settings)} settings...")
        #print(f" RPi Model: {Utils.app_settings.rpi_model} (Index: {Utils.app_settings.rpi_model_index})")
        Utils.app_settings.rpi_model = Utils.project_data.settings.get('rpi_model', "RPI 4 model B")
        Utils.app_settings.rpi_model_index = Utils.project_data.settings.get('rpi_model_index', 6)
        #print(f" RPi Model: {Utils.app_settings.rpi_model} (Index: {Utils.app_settings.rpi_model_index})")
        self.current_canvas.update()
        #print(" Settings rebuilt")

    def _rebuild_blocks(self):
        """Recreate all block widgets on canvas from project_data"""
        try:
            for canvas, canvas_info in Utils.canvas_instances.items():
                if canvas_info['ref'] == 'canvas':
                    for block_id, block in Utils.project_data.main_canvas['blocks'].items():
                        self.add_block_from_data(
                            block_type=block['type'],
                            x=block['x'],
                            y=block['y'],
                            block_id=str(block_id),
                            canvas=canvas,
                            name=block['name'] if 'name' in block else None
                        )
                            
                elif canvas_info['ref'] == 'function':
                    print("Rebuilding blocks for function canvas")
                    for function_id, function_info in Utils.functions.items():
                        print(f" Checking function: {function_id}")
                        if function_info['canvas'] == canvas:
                            print(f" Found matching canvas for function: {function_id}")
                            for block_id, block in Utils.project_data.functions[function_id]['blocks'].items():
                                print(f"  Rebuilding block {block_id} of type {block['type']}")
                                self.add_block_from_data(
                                    block_type=block['type'],
                                    x=block['x'],
                                    y=block['y'],
                                    block_id=str(block_id),
                                    canvas=canvas,
                                    name=block['name'] if 'name' in block else None,
                                )
            #print("✓ Blocks rebuilt on canvas")
        except Exception as e:
            print(f"❌ Error rebuilding blocks: {e}")
        

    def add_block_from_data(self, block_type, x, y, block_id, canvas=None, name=None):
        """Add a new block to the canvas"""
        print(f" Adding block from data: ID={block_id}, Type={block_type}, X={x}, Y={y}, Canvas {canvas}")
        block = BlockGraphicsItem(
            x=x, y=y,
            block_id=block_id,
            block_type=block_type,
            parent_canvas=canvas,
            name=name
        )
        for canvas_key, canvas_info in Utils.canvas_instances.items():
            if canvas_info['canvas'] == canvas:
                break
        if canvas_info['ref'] == 'canvas':
            if block_type in ('If', 'While', 'Button'):
                block.value_1_name = Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1")
                #block.value_1_type = Utils.project_data.blocks[block_id].get('value_1_type', "N/A")
                block.value_2_name = Utils.project_data.main_canvas['blocks'][block_id].get('value_2_name', "var2")
                #block.value_2_type = Utils.project_data.blocks[block_id].get('value_2_type', "N/A")
                block.operator = Utils.project_data.main_canvas['blocks'][block_id].get('operator', "==")
            elif block_type == 'Switch':
                block.value_1_name = Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1")
                block.switch_state = Utils.project_data.main_canvas['blocks'][block_id].get('switch_state', False)
            elif block_type == 'Sleep':
                block.sleep_time = Utils.project_data.main_canvas['blocks'][block_id].get('sleep_time', "1000")
            elif block_type in ('Basic_operations', 'Exponential_operations', 'Random_number'):
                block.value_1_name = Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1")
                block.value_2_name = Utils.project_data.main_canvas['blocks'][block_id].get('value_2_name', "var2")
                block.operator = Utils.project_data.main_canvas['blocks'][block_id].get('operator', None)
                block.result_var_name = Utils.project_data.main_canvas['blocks'][block_id].get('result_var_name', "result")
            elif block_type == 'Blink_LED':
                block.value_1_name = Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1")
                block.sleep_time = Utils.project_data.main_canvas['blocks'][block_id].get('sleep_time', "1000")
            elif block_type == 'Toggle_LED':
                block.value_1_name = Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1")
            elif block_type == 'PWM_LED':
                block.value_1_name = Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1")
                block.PWM_value = Utils.project_data.main_canvas['blocks'][block_id].get('PWM_value', "128")
        if canvas_info['ref'] == 'function':
            #print("Setting function canvas block properties")
            for function_id, function_info in Utils.functions.items():
                #print(f" Checking function: {function_id}")
                if function_info['canvas'] == canvas:
                    #print(f" Found matching canvas for function: {function_id}")
                    if block_type in ('If', 'While', 'Button'):
                        block.value_1_name = Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1")
                        #block.value_1_type = Utils.project_data.blocks[block_id].get('value_1_type', "N/A")
                        block.value_2_name = Utils.project_data.functions[function_id]['blocks'][block_id].get('value_2_name', "var2")
                        #block.value_2_type = Utils.project_data.blocks[block_id].get('value_2_type', "N/A")
                        block.operator = Utils.project_data.functions[function_id]['blocks'][block_id].get('operator', "==")
                    elif block_type == 'Switch':
                        block.value_1_name = Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1")
                        block.switch_state = Utils.project_data.functions[function_id]['blocks'][block_id].get('switch_state', False)
                    elif block_type == 'Sleep':
                        block.sleep_time = Utils.project_data.functions[function_id]['blocks'][block_id].get('sleep_time', "1000")
                    elif block_type in ('Basic_operations', 'Exponential_operations', 'Random_number'):
                        block.value_1_name = Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1")
                        block.value_2_name = Utils.project_data.functions[function_id]['blocks'][block_id].get('value_2_name', "var2")
                        block.operator = Utils.project_data.functions[function_id]['blocks'][block_id].get('operator', None)
                        block.result_var_name = Utils.project_data.functions[function_id]['blocks'][block_id].get('result_var_name', "result")
                    elif block_type == 'Blink_LED':
                        block.value_1_name = Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1")
                        block.sleep_time = Utils.project_data.functions[function_id]['blocks'][block_id].get('sleep_time', "1000")
                    elif block_type == 'Toggle_LED':
                        block.value_1_name = Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1")
                    elif block_type == 'PWM_LED':
                        block.value_1_name = Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1")
                        block.PWM_value = Utils.project_data.functions[function_id]['blocks'][block_id].get('PWM_value', "128")
                    break
                
        canvas.scene.addItem(block)
        
        # Store in Utils
        if canvas_info['ref'] == 'canvas':
            if block_type in ('If', 'While', 'Button'):
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'value_1_name': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1"),
                    'value_1_type': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_type', "N/A"),
                    'value_2_name': Utils.project_data.main_canvas['blocks'][block_id].get('value_2_name', "var2"),
                    'value_2_type': Utils.project_data.main_canvas['blocks'][block_id].get('value_2_type', "N/A"),
                    'operator': Utils.project_data.main_canvas['blocks'][block_id].get('operator', "=="),
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            elif block_type == 'Timer':
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'sleep_time': Utils.project_data.main_canvas['blocks'][block_id].get('sleep_time', "1000"),
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            elif block_type == 'Switch':
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'value_1_name': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1"),
                    'switch_state': Utils.project_data.main_canvas['blocks'][block_id].get('switch_state', False),
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            elif block_type in ('Start', 'End', 'While_true'):
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            elif block_type in ("Basic_operations", "Exponential_operations", "Random_number"):
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'value_1_name': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1"),
                    'value_1_type': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_type', "N/A"),
                    'value_2_name': Utils.project_data.main_canvas['blocks'][block_id].get('value_2_name', "var2"),
                    'value_2_type': Utils.project_data.main_canvas['blocks'][block_id].get('value_2_type', "N/A"),
                    'operator': Utils.project_data.main_canvas['blocks'][block_id].get('operator', None),
                    'result_var_name': Utils.project_data.main_canvas['blocks'][block_id].get('result_var_name', "result"),
                    'result_var_type': Utils.project_data.main_canvas['blocks'][block_id].get('result_var_type', "N/A"),
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            elif block_type == 'Blink_LED':
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'value_1_name': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1"),
                    'value_1_type': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_type', "N/A"),
                    'sleep_time': Utils.project_data.main_canvas['blocks'][block_id].get('sleep_time', "1000"),
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            elif block_type == 'Toggle_LED':
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'value_1_name': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1"),
                    'value_1_type': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_type', "N/A"),
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            elif block_type == 'PWM_LED':
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'value_1_name': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_name', "var1"),
                    'value_1_type': Utils.project_data.main_canvas['blocks'][block_id].get('value_1_type', "N/A"),
                    'PWM_value': Utils.project_data.main_canvas['blocks'][block_id].get('PWM_value', "128"),
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            elif block_type == 'Function':
                info = {
                    'type': 'Function',
                    'id': block_id,
                    'name': Utils.project_data.main_canvas['blocks'][block_id].get('name', ''),
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'internal_vars': {
                        'main_vars': Utils.project_data.main_canvas['blocks'][block_id]['internal_vars'].get('main_vars', {}),
                        'ref_vars': Utils.project_data.main_canvas['blocks'][block_id]['internal_vars'].get('ref_vars', {}),
                    },
                    'internal_devs': {
                        'main_devs': Utils.project_data.main_canvas['blocks'][block_id]['internal_devs'].get('main_devs', {}),
                        'ref_devs': Utils.project_data.main_canvas['blocks'][block_id]['internal_devs'].get('ref_devs', {}),
                    },
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            else:
                print(f"Error: Unknown block type {block_type}")
                info = {
                    'type': block_type,
                    'id': block_id,
                    'widget': block,
                    'width': block.boundingRect().width(),
                    'height': block.boundingRect().height(),
                    'x': x,
                    'y': y,
                    'in_connections': Utils.project_data.main_canvas['blocks'][block_id].get('in_connections', {}),
                    'out_connections': Utils.project_data.main_canvas['blocks'][block_id].get('out_connections', {}),
                    'canvas': canvas
                }
            Utils.main_canvas['blocks'][block_id] = info
        if canvas_info['ref'] == 'function':
            print("Storing function canvas block in Utils")
            for function_id, function_info in Utils.functions.items():
                print(f" Checking function: {function_id}")
                if function_info['canvas'] == canvas:
                    print(f" Found matching canvas for function: {function_id}")
                    if block_type in ('If', 'While', 'Button'):
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'value_1_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1"),
                            'value_1_type': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_type', "N/A"),
                            'value_2_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_2_name', "var2"),
                            'value_2_type': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_2_type', "N/A"),
                            'operator': Utils.project_data.functions[function_id]['blocks'][block_id].get('operator', "=="),
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    elif block_type == 'Timer':
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'sleep_time': Utils.project_data.functions[function_id]['blocks'][block_id].get('sleep_time', "1000"),
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    elif block_type == 'Switch':
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'value_1_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1"),
                            'switch_state': Utils.project_data.functions[function_id]['blocks'][block_id].get('switch_state', False),
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    elif block_type in ('Start', 'End', 'While_true'):
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    elif block_type in ("Basic_operations", "Exponential_operations", "Random_number"):
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'value_1_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1"),
                            'value_1_type': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_type', "N/A"),
                            'value_2_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_2_name', "var2"),
                            'value_2_type': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_2_type', "N/A"),
                            'operator': Utils.project_data.functions[function_id]['blocks'][block_id].get('operator', None),
                            'result_var_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('result_var_name', "result"),
                            'result_var_type': Utils.project_data.functions[function_id]['blocks'][block_id].get('result_var_type', "N/A"),
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    elif block_type == 'Blink_LED':
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'value_1_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1"),
                            'value_1_type': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_type', "N/A"),
                            'sleep_time': Utils.project_data.functions[function_id]['blocks'][block_id].get('sleep_time', "1000"),
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    elif block_type == 'Toggle_LED':
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'value_1_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1"),
                            'value_1_type': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_type', "N/A"),
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    elif block_type == 'PWM_LED':
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'value_1_name': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_name', "var1"),
                            'value_1_type': Utils.project_data.functions[function_id]['blocks'][block_id].get('value_1_type', "N/A"),
                            'PWM_value': Utils.project_data.functions[function_id]['blocks'][block_id].get('PWM_value', "128"),
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    elif block_type == 'Function':
                        info = {
                            'type': 'Function',
                            'id': block_id,
                            'name': Utils.project_data.functions[function_id]['blocks'][block_id].get('name', ''),
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'internal_vars': {
                                'main_vars': Utils.project_data.functions[function_id]['blocks'][block_id]['internal_vars'].get('main_vars', {}),
                                'ref_vars': Utils.project_data.functions[function_id]['blocks'][block_id]['internal_vars'].get('ref_vars', {}),
                            },
                            'internal_devs': {
                                'main_devs': Utils.project_data.functions[function_id]['blocks'][block_id]['internal_devs'].get('main_devs', {}),
                                'ref_devs': Utils.project_data.functions[function_id]['blocks'][block_id]['internal_devs'].get('ref_devs', {}),
                            },
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    else:
                        print(f"Error: Unknown block type {block_type}")
                        info = {
                            'type': block_type,
                            'id': block_id,
                            'widget': block,
                            'width': block.boundingRect().width(),
                            'height': block.boundingRect().height(),
                            'x': x,
                            'y': y,
                            'in_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('in_connections', {}),
                            'out_connections': Utils.project_data.functions[function_id]['blocks'][block_id].get('out_connections', {}),
                            'canvas': canvas
                        }
                    
                    Utils.functions[function_id]['blocks'][block_id] = info
                    break
        block.connect_graphics_signals()
        return block

    def _rebuild_connections(self):
        """Recreate all connection paths from projectdata"""
        for canvas, canvas_info in Utils.canvas_instances.items():
            if canvas_info['ref'] == 'canvas':
                #print(f"Rebuilding {len(Utils.project_data.main_canvas['paths'])} connections...")
                #print(f"Utils.top_infos contains: {list(Utils.main_canvas['blocks'].keys())}")
                #print(f"Project connections: {list(Utils.project_data.main_canvas['paths'].keys())}")
                #print(f"Path conections before rebuild: {Utils.project_data.main_canvas['paths']}")
            
                for conn_id, conn_data in Utils.project_data.main_canvas['paths'].items():
                    try:
                        from_block_id = str(conn_data.get("from"))
                        to_block_id = str(conn_data.get("to"))
                        
                        #print(f"Processing connection {conn_id}: {from_block_id} -> {to_block_id}")
                        
                        # DEBUG: Check what's actually in Utils.top_infos
                        #print(f"Available block IDs in Utils.top_infos: {list(Utils.main_canvas['blocks'].keys())}")
                        #print(f"Is {from_block_id} in top_infos? {from_block_id in Utils.main_canvas['blocks']}")
                        #print(f"Is {to_block_id} in top_infos? {to_block_id in Utils.main_canvas['blocks']}")
                        
                        if from_block_id not in Utils.main_canvas['blocks'] or to_block_id not in Utils.main_canvas['blocks']:
                            print(f"❌ Connection {conn_id}: Missing block reference!")
                            #print(f"  from_block_id ({from_block_id}) exists: {from_block_id in Utils.main_canvas['blocks']}")
                            #print(f"  to_block_id ({to_block_id}) exists: {to_block_id in Utils.main_canvas['blocks']}")
                            continue
                        
                        from_block = Utils.main_canvas['blocks'][from_block_id]
                        to_block = Utils.main_canvas['blocks'][to_block_id]
                        
                        from_blockwidget = from_block.get("widget")
                        to_blockwidget = to_block.get("widget")
                        
                        path_item = PathGraphicsItem(
                            from_block=from_blockwidget,
                            to_block=to_blockwidget,
                            path_id=conn_id,
                            parent_canvas=canvas,
                            to_circle_type=conn_data.get("to_circle_type", "in"),
                            from_circle_type=conn_data.get("from_circle_type", "out")
                        )
                        canvas.scene.addItem(path_item)
                        # Recreate connection
                        Utils.main_canvas['paths'][conn_id] = {
                            'from': from_block_id,
                            'from_circle_type': conn_data.get("from_circle_type", "out"),
                            'to': to_block_id,
                            'to_circle_type': conn_data.get("to_circle_type", "in"),
                            'waypoints': conn_data.get("waypoints", []),
                            'canvas': canvas,
                            'color': QColor(31, 83, 141),
                            'item': path_item
                        }
                        #print(f"Recreated path in Utils.main_canvas: {Utils.main_canvas['paths'][conn_id]}")
                        Utils.scene_paths[conn_id] = path_item
                        
                        # Update block connection references
                        if conn_id not in from_block["out_connections"].keys():
                            from_block["out_connections"][conn_id] = conn_data.get("from_circle_type", "out")
                        if conn_id not in to_block["in_connections"].keys():
                            to_block["in_connections"][conn_id] = conn_data.get("to_circle_type", "in")
                        
                        #print(f"✓ Connection {conn_id} recreated")
                        
                    except Exception as e:
                        print(f"❌ Error recreating connection {conn_id}: {e}")
                        import traceback
                        traceback.print_exc()
            elif canvas_info['ref'] == 'function':
                for function_id, function_info in Utils.functions.items():
                    #print(f" Checking function: {function_id}")
                    if function_info['canvas'] == canvas:
                        #print(f" Found matching canvas for function: {function_id}")
                        #print(f"Rebuilding {len(Utils.project_data.functions[function_id]['paths'])} connections...")
                        #print(f"Utils.top_infos contains: {list(Utils.functions[function_id]['blocks'].keys())}")
                        #print(f"Project connections: {list(Utils.project_data.functions[function_id]['paths'].keys())}")
                        #print(f"Path conections before rebuild: {Utils.project_data.functions[function_id]['paths']}")
                    
                        for conn_id, conn_data in Utils.project_data.functions[function_id]['paths'].items():
                            try:
                                from_block_id = str(conn_data.get("from"))
                                to_block_id = str(conn_data.get("to"))
                                
                                #print(f"Processing connection {conn_id}: {from_block_id} -> {to_block_id}")
                                
                                # DEBUG: Check what's actually in Utils.top_infos
                                #print(f"Available block IDs in Utils.top_infos: {list(Utils.functions[function_id]['blocks'].keys())}")
                                #print(f"Is {from_block_id} in top_infos? {from_block_id in Utils.functions[function_id]['blocks']}")
                                #print(f"Is {to_block_id} in top_infos? {to_block_id in Utils.functions[function_id]['blocks']}")
                                
                                if from_block_id not in Utils.functions[function_id]['blocks'] or to_block_id not in Utils.functions[function_id]['blocks']:
                                    print(f"❌ Connection {conn_id}: Missing block reference!")
                                    #print(f"  from_block_id ({from_block_id}) exists: {from_block_id in Utils.functions[function_id]['blocks']}")
                                    #print(f"  to_block_id ({to_block_id}) exists: {to_block_id in Utils.functions[function_id]['blocks']}")
                                    continue
                                
                                from_block = Utils.functions[function_id]['blocks'][from_block_id]
                                to_block = Utils.functions[function_id]['blocks'][to_block_id]
                                
                                from_blockwidget = from_block.get("widget")
                                to_blockwidget = to_block.get("widget")
                                
                                path_item = PathGraphicsItem(
                                    from_block=from_blockwidget,
                                    to_block=to_blockwidget,
                                    path_id=conn_id,
                                    parent_canvas=canvas,
                                    to_circle_type=conn_data.get("to_circle_type", "in"),
                                    from_circle_type=conn_data.get("from_circle_type", "out")
                                )
                                canvas.scene.addItem(path_item)
                                # Recreate connection
                                Utils.functions[function_id]['paths'][conn_id] = {
                                    'from': from_block_id,
                                    'from_circle_type': conn_data.get("from_circle_type", "out"),
                                    'to': to_block_id,
                                    'to_circle_type': conn_data.get("to_circle_type", "in"),
                                    'waypoints': conn_data.get("waypoints", []),
                                    'canvas': canvas,
                                    'color': QColor(31, 83, 141),
                                    'item': path_item
                                }
                                #print(f"Recreated path in Utils.functions for {function_id}: {Utils.functions[function_id]['paths'][conn_id]}")
                                Utils.scene_paths[conn_id] = path_item
                                
                                # Update block connection references
                                if conn_id not in from_block["out_connections"].keys():
                                    from_block["out_connections"][conn_id] = conn_data.get("from_circle_type", "out")
                                if conn_id not in to_block["in_connections"].keys():
                                    to_block['in_connections'][conn_id] = conn_data.get("to_circle_type", "in")
                                
                                #print(f"✓ Connection {conn_id} recreated")
                                
                            except Exception as e:
                                print(f"❌ Error recreating connection {conn_id}: {e}")
                                import traceback
                                traceback.print_exc()
                                
        for canvas, canvas_info in Utils.canvas_instances.items():
            canvas.scene.update()
            
        
    def _rebuild_variables_panel(self):
        """Recreate variables in the side panel"""
        #print(f"Rebuilding {len(Utils.project_data.variables)} variables...")
        #print(f" Project variables data: {Utils.project_data.variables}")
        for canvas, canvas_info in Utils.canvas_instances.items():
            #print(f" Canvas: {canvas_info['name']} (Ref: {canvas_info['ref']})")
            if canvas_info['ref'] == 'canvas':
                #print(" Recreating variables for main canvas")
                for var_id, var_info in list(Utils.project_data.variables['main_canvas'].items()):
                    #print(f"  Recreating variable {var_id} on main canvas")
                    self.add_variable_row(var_id, var_info, canvas)
                print(f"Variables after main canvas rebuild: {Utils.variables['main_canvas']}")
            elif canvas_info['ref'] == 'function':
                #print(f" Recreating variables for function canvas: {canvas_info['name']}")
                for var_id, var_info in list(Utils.project_data.variables['function_canvases'][canvas_info['id']].items()):
                    #print(f"  Recreating variable {var_id} on function canvas")
                    self.add_internal_variable_row(var_id, var_info, canvas)
                print(f"Variables after function canvas rebuild: {Utils.variables['function_canvases'][canvas_info['id']]}")

    def _rebuild_devices_panel(self):
        """Recreate devices in the side panel"""
        #print(f"Rebuilding {len(Utils.project_data.devices)} devices...")
        
        for canvas, canvas_info in Utils.canvas_instances.items():
            #print(f" Canvas: {canvas_info['name']} (Ref: {canvas_info['ref']})")
            if canvas_info['ref'] == 'canvas':
                #print(" Recreating devices for main canvas")
                for dev_id, dev_info in list(Utils.project_data.devices['main_canvas'].items()):
                    #print(f"  Recreating device {dev_id} on main canvas")
                    self.add_device_row(dev_id, dev_info, canvas)
                print(f"Devices after main canvas rebuild: {Utils.devices['main_canvas']}")
            elif canvas_info['ref'] == 'function':
                #print(f" Recreating devices for function canvas: {canvas_info['name']}")
                for dev_id, dev_info in list(Utils.project_data.devices['function_canvases'][canvas_info['id']].items()):
                    #print(f"  Recreating device {dev_id} on function canvas")
                    self.add_internal_device_row(dev_id, dev_info, canvas)
                print(f"Devices after function canvas rebuild: {Utils.devices['function_canvases'][canvas_info['id']]}")
        
def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(31, 31, 31))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(43, 43, 43))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(58, 58, 58))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(43, 43, 43))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(31, 83, 141))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(31, 83, 141))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
