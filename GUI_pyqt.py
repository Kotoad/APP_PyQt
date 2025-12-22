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
    QStackedWidget, QSplitter
)
import typing
from PyQt6 import QtGui
from Imports import (
    get_code_compiler, get_spawn_elements, get_device_settings_window,
    get_file_manager, get_path_manager, get_Elements_Window, get_utils,
    get_Help_Window, get_Sidebar_TabView
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

            try:
                # Kill any existing python processes that might be running old code
                # This ensures old code stops before new code starts
                kill_command = "pkill -f 'python3.*File.py' || true"
                stdin, stdout, stderr = ssh.exec_command(kill_command, timeout=5)
                kill_status = stdout.channel.recv_exit_status()
                print(f"[RPiExecutionThread] Kill command executed (exit code: {kill_status})")
            except Exception as e:
                print(f"[RPiExecutionThread] Warning: Could not kill old processes: {e}")

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
        
        # Size configuration - YOU CONTROL CIRCLE SIZE HERE!
        self.base_width = width
        self.base_height = height
        self.circle_diameter = height - 8  # <-- CIRCLE SIZE DEPENDS ON HEIGHT!
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
        print(f"All items added: {self.all_items}")

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
        print(f"Item height: {itemheight}")
        count = self.popup.count()
        print(f"Item count: {count}")
        h = min(count * itemheight, itemheight * 5)  # Max 5 items visible
        print(f"Popup height: {h}")
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
        print(f"Self in GridCanvas init: {self}")
        self.grid_size = grid_size
        
        self.spawner = spawningelements(self)
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
        if event.key() == Qt.Key.Key_Home:
            # Reset zoom and pan
            self.resetTransform()
            self.zoom_level = 1.0
            event.accept()
        if self.spawner and self.spawner.element_placed:
            print(f"Key pressed: {event.key()}")
            print(f"Element placed before: {self.spawner.element_placed}")
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
        print("⚠ GridCanvas.mousePressEvent fired!")
        
        if event.button() == Qt.MouseButton.MiddleButton:
            print("Middle mouse button pressed - starting pan")
            self.middle_mouse_pressed = True
            self.middle_mouse_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return  # Skip default processing, just pan
        if event.button() == Qt.MouseButton.LeftButton:
            if self.spawner and self.spawner.element_placed:
                # Place the element at mouse position
                scene_pos = self.mapToScene(event.position().toPoint())
                self.spawner.place_element_at(self, scene_pos.x(), scene_pos.y())
                event.accept()
                return
        if event.button() == Qt.MouseButton.RightButton:
            print("Right mouse button pressed - checking for context menu")
            # Right-click: show context menu if over a block or path
            scene_pos = self.mapToScene(event.position().toPoint())
            print(f"Scene position: {scene_pos}")
            items = self.scene.items(scene_pos)
            print(f"Items under cursor: {items}")
            for item in items:
                print(f"Checking item: {item}")
                if isinstance(item, BlockGraphicsItem):
                    print("Showing block context menu")
                    self.show_block_context_menu(item, scene_pos)
                    event.accept()
                    return
                elif isinstance(item, PathGraphicsItem):
                    print("Showing path context menu")
                    self.show_path_context_menu(item, scene_pos)
                    event.accept()
                    return
        # For all other buttons, let parent handle it (sends to scene)
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
    
    def add_block(self, block_type, x, y, block_id):
        """Add a new block to the canvas"""
        block = BlockGraphicsItem(
            x=x, y=y,
            block_id=block_id,
            block_type=block_type,
            parent_canvas=self,
            main_window=self.main_window
        )
        
        self.scene.addItem(block)
        
        current_canvas = self.main_window.current_canvas
        if current_canvas:
            print(f"Current canvas in add_block: {current_canvas}")
            print(f"Parent canvas in block: {self}")
        if hasattr(self, 'reference') and self.reference:
            print(f"Canvas reference in add_block: {self.reference}")
        # Store in Utils
        info = {
            'type': block_type,
            'id': block_id,
            'widget': block,
            'type': block_type,
            'width': block.boundingRect().width(),
            'height': block.boundingRect().height(),
            'x': x,
            'y': y,
            'value_1_name': "var1",
            'value_1_type': "N/A",
            'value_2_name': "var2",
            'value_2_type': "N/A",
            'operator': "==",
            'switch_state': False,
            'sleep_time': "1000",
            'in_connections': [],
            'out_connections': [],
            'canvas': self
        }
        if self.reference == 'canvas':
            Utils.main_canvas['blocks'].setdefault(block_id, info)
        elif self.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                print(f"Utils.functions key: {f_id}, value: {f_info}")
                if self == f_info.get('canvas'):
                    print(f"Matched function canvas for block addition: {f_id}")
                    Utils.functions[f_id]['blocks'].setdefault(block_id, info)
                    break
        print(f"Added block: {info}")
        if self.reference == 'canvas':
            print(f"Current Utils.main_canvas blocks: {Utils.main_canvas['blocks']}")
        elif self.reference == 'function':
            print(f"Current Utils.functions[{f_id}] blocks: {Utils.functions[f_id]['blocks']}")
        Utils.top_infos[block_id] = info
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
        if path_id in Utils.paths:
            path_item = Utils.paths[path_id].get('item')
            if path_item:
                self.scene.removeItem(path_item)
            del Utils.paths[path_id]
    
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
        print(f"Editing block: {block_id}")
    
    def duplicate_block(self, block, block_id):
        """Create a copy of a block"""
        #TODO : Implement duplication logic
        if block_id not in Utils.top_infos:
            return
        
        block_data = Utils.top_infos[block_id]
        x = block_data['x'] + 50
        y = block_data['y'] + 50
        print(f"Duplicating block {block_id} at ({x}, {y})")
    
    def delete_block(self, block, block_id):
        """Delete a block and its connections"""
        print(f"Deleting block: {block_id}")
        
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
                print(f"Canvas in Utils.canvas_instances: {canvas}, info: {info}")
                if info['index'] == index:
                    print(f"✓ Found current canvas in Utils.canvas_instances: {canvas}")
                    widget = info['canvas']
            print(f"Current sidebar tab index: {index}, widget: {widget}")
            
            # Check if it's a GridCanvas instance
            if isinstance(widget, GridCanvas):
                print("✓ Current canvas found.")
                return widget
        except Exception as e:
            print(f"⚠️ Error getting current canvas: {e}")
        
        # Fallback to main canvas if property fails
        if hasattr(self, 'canvas') and self.canvas is not None:
            print("✓ Using main canvas as fallback.")
            return self.canvas
        
        print("❌ No canvas available.")
        return None
        
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visual Programming Interface")
        self.resize(1200, 800)
        self.code_compiler = Code_Compiler()
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
            QPushButton {
                background-color: #C74343;
                color: #FFFFFF;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #E05555;
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
                
                
        self.create_menu_bar()
        self.create_canvas_frame()
    
    def mousePressEvent(self, event):
        """Debug: Track if main window gets mouse press"""
        print("⚠ MainWindow.mousePressEvent fired!")
        super().mousePressEvent(event)
    #MARK: - UI Creation Methods
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        print(f"Menubar Height: {menubar.height()}")
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
        canvas_action.triggered.connect(lambda: self.set_current_tab(0))

        variables_action = view_menu.addAction("Show Variables")
        variables_action.triggered.connect(lambda: self.set_current_tab(1))

        devices_action = view_menu.addAction("Show Devices")
        devices_action.triggered.connect(lambda: self.set_current_tab(2))
        
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
        
    def create_canvas_frame(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
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
    
    def on_tab_changed(self, index):
        if index not in [info['index'] for info in Utils.canvas_instances.values()]:
            print(f"Tab index {index} not in Utils.canvas_instances indices.")
            return
        if self.current_canvas != self.last_canvas:
            print(f"Sidebar tab changed to index: {index}, widget: {self.current_canvas}")
            for var_canvas, var_panel in Utils.variables_panels.items():
                if var_canvas == self.current_canvas:
                    print("Current tab is a GridCanvas with Variables panel.")
                    try:
                        for canvas, info in Utils.canvas_instances.items():
                            canvas.var_button.hide()
                            if info['ref'] == 'canvas':
                                print("Keeping variable button visible for main canvas.")
                                canvas.var_button.show()
                            if canvas == self.current_canvas:
                                canvas.var_button.show()
                    except Exception as e:
                        print(f"Error showing/hiding variable buttons: {e}")
            for dev_canvas, dev_panel in Utils.devices_panels.items():
                if dev_canvas == self.current_canvas:
                    print("Current tab is a GridCanvas with Devices panel.")
                    try:
                        for canvas, info in Utils.canvas_instances.items():
                            canvas.dev_button.hide()
                            if info['ref'] == 'canvas':
                                print("Keeping variable button visible for main canvas.")
                                canvas.dev_button.show()
                            if canvas == self.current_canvas:
                                canvas.dev_button.show()
                    except Exception as e:
                        print(f"Error showing/hiding device buttons: {e}")
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
        Utils.variables_panels[canvas_reference] = canvas_reference.widget
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
        Utils.devices_panels[canvas_reference] = canvas_reference.widget
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
        self.pages = {}
        self.page_count = 0
        self.count_w_separator = 0
        self.canvas_count = 0
        self.tab_buttons = []  # Track tab buttons
        
        return widget

    def add_tab(self, tab_name, content_widget=None, icon=None, reference=None):
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
            print(f"Adding canvas tab: {tab_name}")
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
                function_id = 'function_'+str(len(Utils.functions)+1)
                Utils.functions[function_id] = {
                    'name': tab_name,
                    'id': function_id,
                    'canvas': content_widget,
                    'blocks': {},
                    'paths': {}
                }
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
            print("Adding Variable tab button")
            print(f"Content widget in variable tab: {content_widget}")
            self.canvas_added.var_button = QPushButton(tab_name)
            tab_button = self.canvas_added.var_button
        elif reference == 'device':
            print("Adding Device tab button")
            print(f"Content widget in device tab: {content_widget}")
            self.canvas_added.dev_button = QPushButton(tab_name)
            tab_button = self.canvas_added.dev_button
        else:
            tab_button = QPushButton(tab_name)
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
            
            QPushButton:pressed {
                background-color: #1F538D;
                border-left: 3px solid #4CAF50;
            }
        """)
        tab_index = self.page_count
        self.tab_buttons.append({
            'button': tab_button,
            'index': tab_index,
            'name': tab_name
        })
        print(f"Adding tab '{tab_name}' at index {tab_index} with reference '{reference}'")
        tab_button.clicked.connect(lambda: self._on_tab_clicked(tab_index, reference))
        if reference == 'canvas':
            self.tab_layout.insertWidget(self.canvas_count, tab_button)
            self.page_count+=1
            self.count_w_separator+=1
            self.canvas_count+=1
            self.canvas_added = content_widget
            self.add_separator(ref='reference')
            self.add_new_canvas_tab_button()
            self.add_separator()
            self.add_variable_tab(content_widget, 'Main')
            self.add_device_tab(content_widget, 'Main')
            self.add_separator(ref='reference')
            self.canvas_added = None
            return tab_index
        elif reference == 'function':
            self.tab_layout.insertWidget(self.canvas_count, tab_button)
            self.page_count+=1
            self.count_w_separator+=1
            self.canvas_count+=1
            self.canvas_added = content_widget
            self.add_variable_tab(content_widget, tab_name)
            self.add_device_tab(content_widget, tab_name)
            self.add_separator(ref='reference')
            self.canvas_added = None
            return tab_index
        elif reference in ('variable', 'device'):
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
        print("Adding Variables tab")
        variables_panel = self.create_variables_panel(canvas_reference)
        self.add_tab(name+' variables', variables_panel, reference="variable")
    
    def add_device_tab(self, canvas_reference, name):
        """Add a Devices tab to the sidebar"""
        print("Adding Devices tab")
        devices_panel = self.create_devices_panel(canvas_reference)
        self.add_tab(name+' devices', devices_panel, reference="device")
    
    def add_new_canvas_tab_button(self):
        """Add a special button to create a new canvas tab"""
        new_canvas_button = QPushButton("+ New Canvas")
        new_canvas_button.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: #1F538D;
                border-left: 3px solid #4CAF50;
            
        """)
        new_canvas_button.clicked.connect(self._on_new_canvas_clicked)
        self.tab_layout.insertWidget(self.canvas_count, new_canvas_button)
    
    def _on_new_canvas_clicked(self):
        """Handler for new canvas tab button click"""
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
        Utils.canvas_instances[new_canvas] = {'canvas': new_canvas,
                                              'index': new_tab_index,
                                              'ref': 'function'}
        self.tab_changed.emit(new_tab_index)
        print(f"Utils.canvas_instances count: {len(Utils.canvas_instances)}")
        print(f"Utils.canvas_instances: {Utils.canvas_instances}")
        self.set_current_tab(new_tab_index)
    
    def add_separator(self, ref=None):
        """Add a visual separator line with exactly 5px height"""
        
        # Create a container for the separator
        separator_container = QFrame()
        separator_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)
        separator_container.setFixedHeight(5)
        
        # Create the actual line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Plain)
        separator.setLineWidth(1)
        separator.setStyleSheet("background-color: #555555;")
        
        # Layout for container
        layout = QVBoxLayout(separator_container)
        layout.setContentsMargins(0, 2, 0, 2)  # Vertical padding: 2px top + 2px bottom + 1px line = 5px total
        layout.setSpacing(0)
        layout.addWidget(separator)
        if ref is None:
            self.tab_layout.insertWidget(self.canvas_count, separator_container)
        else:
            self.tab_layout.insertWidget(self.count_w_separator, separator_container)
            self.count_w_separator+=1
            
    def set_current_tab(self, tab_index):
        """Switch to a specific tab by index"""
        if 0 <= tab_index < len(self.tab_buttons):
            self._on_tab_clicked(tab_index)
    
    def get_current_tab_index(self):
        """Get currently active tab index"""
        return self.content_area.currentIndex()
    
    def get_tab_widget(self, tab_name):
        """Get the widget for a specific tab"""
        return self.pages.get(tab_name)
    
    def _on_tab_clicked(self, tab_index, reference=None):
        """Internal handler for tab clicks"""
        if 0 <= tab_index < len(self.tab_buttons):
            self.content_area.setCurrentIndex(tab_index)
            
            # Update button styles
            for tb in self.tab_buttons:
                if tb['index'] == tab_index:
                    tb['button'].setStyleSheet("""
                        QPushButton {
                            background-color: #1F538D;
                            color: #FFFFFF;
                            border-left: 3px solid #4CAF50;
                            padding: 12px;
                            text-align: left;
                        }
                    """)
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
                print(f"Setting Utils.courent_canvas to canvas tab index {tab_index}")
                print(f"Utils.canvas_instances: {Utils.canvas_instances}")
                #if tab_index - self.canvas_count < 0:
                    #tab_index = 0
                    #print(f"Courent canvas index: {tab_index}")
                    #Utils.courent_canvas = Utils.canvas_instances[tab_index]
                    #print(f"Set Utils.courent_canvas to tab '{Utils.courent_canvas}'")
                #else:
                    #print(f"Setting Utils.courent_canvas to index {tab_index - self.canvas_count+1}")
                    #Utils.courent_canvas = Utils.canvas_instances[tab_index-self.canvas_count+1]
                    #print(f"Set Utils.courent_canvas to tab '{Utils.courent_canvas}'")
            self.tab_changed.emit(tab_index)
    #MARK: - Inspector Panel Methods
    def toggle_inspector_frame(self, block):
        """Toggle inspector panel based on block selection"""
        print(f"Self in toggle_inspector_frame: {self}")
        print(f"Current canvas in toggle_inspector_frame: {self.current_canvas}")
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
        print(f"Self in show_inspector_frame: {self}")
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
        current_canvas.inspector_content_layout.addWidget(title)
        
        position_label = QLabel(f"Position: ({int(block.x())}, {int(block.y())})")
        current_canvas.inspector_content_layout.addWidget(position_label)
        
        size_label = QLabel(f"Size: ({int(block.boundingRect().width())} x {int(block.boundingRect().height())})")
        current_canvas.inspector_content_layout.addWidget(size_label)
        
        self.add_inputs(block)
        current_canvas.inspector_content_layout.addStretch()

    def add_inputs(self, block):
        """Add input fields for block properties"""
        current_canvas = self.current_canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return
        
        if current_canvas.reference == 'canvas':
            print(f"Current Utils.main_canvas['blocks']: {Utils.main_canvas['blocks']}")
            block_data = Utils.main_canvas['blocks'].get(block.block_id)
        elif current_canvas.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                if current_canvas == f_info.get('canvas'):
                    print(f"Current Utils.functions[{f_id}]['blocks']: {Utils.functions[f_id]['blocks']}")
                    block_data = Utils.functions[f_id]['blocks'].get(block.block_id)
                    break
        
        print(f"Adding inputs for block data: {block_data}")
        if block_data['type'] in ('Start', 'End'):
            return
        
        if block_data['type'] == 'Timer':
            # Timer block inputs
            label = QLabel("Interval (ms):")
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), label)
            
            interval_input = QLineEdit()
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
            self.name_1_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_name_1_changed(text, bd))
            
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
            self.name_1_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_name_1_changed(text, bd))
            
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
            self.name_1_input.textChanged.connect(lambda text, bd=block_data: self.Block_value_name_1_changed(text, bd))
            
            self.insert_items(block, self.name_1_input)
            
            current_canvas.inspector_content_layout.insertWidget(current_canvas.inspector_content_layout.count(), self.name_1_input)
    
    def Block_value_name_1_changed(self, text, block_data):
        current_canvas = self.current_canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return
        
        # Get the splitter from the current canvas
        canvas_splitter = getattr(current_canvas, 'canvas_splitter', None)
        if canvas_splitter is None:
            print("ERROR: No canvas_splitter found in current canvas")
            return
        block_data['value_1_name'] = text
        for var_id, var_info in Utils.variables.items():
            if var_info['name'] == text:
                block_data['value_1_type'] = 'Variable'
                break
        for dev_id, dev_info in Utils.devices.items():
            if dev_info['name'] == text:
                block_data['value_1_type'] = 'Device'
                break
        if current_canvas.last_block.block_type == 'Button':
            block_data['value_2_name'] = ''
            block_data['value_2_type'] = 'N/A'
            if len(text) > 6:
                text = text[:4] + "..."
            item = block_data['widget']
        else:
            if len(text) > 5:
                text = text[:3] + "..."
            item = block_data['widget']
        if item:
            item.value_1_name = text
            item.update()
    
    def Block_operator_changed(self, text, block_data):
        block_data['operator'] = text
        item = block_data['widget']
        if item:    
            item.operator = text
            item.update()
    
    def Block_value_2_name_changed(self, text, block_data):
        block_data['value_2_name'] = text
        for var_id, var_info in Utils.variables.items():
            if var_info['name'] == text:
                block_data['value_2_type'] = 'Variable'
                break
        for dev_id, dev_info in Utils.devices.items():
            if dev_info['name'] == text:
                block_data['value_2_type'] = 'Device'
                break
        if len(text) > 5:
            text = text[:3] + "..."
        item = block_data['widget']
        if item:
            item.value_2_name = text
            item.update()
    
    def Block_switch_changed(self, state, block_data):
        block_data['switch_state'] = state
        print(f"Switch state changed to: {state}")
        item = block_data['widget']
        if item:
            item.switch_state = state
            item.update()
    
    def Block_sleep_interval_changed(self, text, block_data):
        block_data['sleep_time'] = text
        item = block_data['widget']
        if item:
            item.sleep_time = text
            item.update()
    
    def insert_items(self, block, line_edit):
        current_canvas = self.current_canvas
        if current_canvas is None:
            print("ERROR: No current canvas available")
            return
        if current_canvas.reference == 'canvas':
            print(f"Current Utils.main_canvas['blocks']: {Utils.main_canvas['blocks']}")
            if not block.block_id in Utils.main_canvas['blocks']:
                return
        elif current_canvas.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                if current_canvas == f_info.get('canvas'):
                    print(f"Current Utils.functions[{f_id}]['blocks']: {Utils.functions[f_id]['blocks']}")
                    if not block.block_id in Utils.functions[f_id]['blocks']:
                        return
                    break
        print("Inserting items into combo box")
        if hasattr(line_edit, 'addItems'):
            print("Line edit supports addItems")
            # Collect all items
            all_items = []
            print(f"All items before insertion: {all_items}")
            if block.block_type in ('Switch', 'Button'):
                for id, text in Utils.dev_items.items():
                    print(f"Added device item into Switch/Button: {text}")
                    all_items.append(text)
            else:
                for id, text in Utils.var_items.items():
                    all_items.append(text)
                    print(f"Added variable item: {text}")
                for id, text in Utils.dev_items.items():
                    print(f"Added device item: {text}")
                    all_items.append(text)

            # Add all items at once
            print(f"Inserting items into combo box: {all_items}")
            line_edit.addItems(all_items)
            print(f"Added {len(all_items)} items to combo box")
            
    #MARK: - Variable Panel Methods
    def add_variable_row(self, var_id=None, var_data=None, canvas_reference=None):
        """Add a new variable row"""
        if var_id is None:
            var_id = f"var_{canvas_reference.variable_row_count}"
        self.var_id = var_id
        #print(f"Adding variable row {self.var_id}")
        
        canvas_reference.row_widget = QWidget()
        canvas_reference.row_layout = QHBoxLayout(canvas_reference.row_widget)
        canvas_reference.row_layout.setContentsMargins(5, 5, 5, 5)
 
        name_imput = QLineEdit()
        name_imput.setPlaceholderText("Name")
        if var_data and 'name' in var_data:
            name_imput.setText(var_data['name'])
            Utils.variables[var_id]['name'] = var_data['name']
        
        name_imput.textChanged.connect(lambda text, v_id=var_id, t="Variable": self.name_changed(text, v_id, t))
        
        type_input = QComboBox()
        type_input.addItems(["Int", "Float", "String", "Bool"])
        if var_data and 'type' in var_data:
            type_input.setCurrentText(var_data['type'])
            Utils.variables[var_id]['type'] = var_data['type']
        
        type_input.currentTextChanged.connect(lambda  text, v_id=var_id, t="Variable": self.type_changed(text, v_id , t))
        
        self.value_var_input = QLineEdit()
        self.value_var_input.setPlaceholderText("Initial Value")
        if var_data and 'value' in var_data:
            self.value_var_input.setText(var_data['value'])
            Utils.variables[var_id]['value'] = var_data['value']
        regex = QRegularExpression(r"^\d*$")
        validator = QRegularExpressionValidator(regex, self)
        self.value_var_input.setValidator(validator)
        self.value_var_input.textChanged.connect(lambda text, v_id=var_id, t="Variable": self.value_changed(text, v_id, t))
        
        delete_btn = QPushButton("×")
        delete_btn.setFixedWidth(30)
        
        canvas_reference.row_layout.addWidget(name_imput)
        canvas_reference.row_layout.addWidget(type_input)
        canvas_reference.row_layout.addWidget(self.value_var_input)
        canvas_reference.row_layout.addWidget(delete_btn)
        
        delete_btn.clicked.connect(lambda _, v_id=var_id, rw=canvas_reference.row_widget, t="Variable", r=canvas_reference: self.remove_row(rw, v_id, t, r))
        
        Utils.variables[var_id] = {
            'name': '',
            'type': 'Out',
            'value': '',
            'widget': canvas_reference.row_widget,
            'name_imput': name_imput,
            'type_input': type_input,
            'value_input': self.value_var_input
        } 
        
        panel_layout = canvas_reference.var_layout
        panel_layout.insertWidget(panel_layout.count() - 1, canvas_reference.row_widget)
        
        canvas_reference.variable_row_count += 1
        
        #print(f"Added variable: {self.var_id}")
    
    def Clear_All_Variables(self):
        print("Clearing all variables")
        
        # Get a SNAPSHOT of variable IDs BEFORE modifying anything
        var_ids_to_remove = list(Utils.variables.keys())
        print(f"Variable IDs to remove: {var_ids_to_remove}")
        
        # Now remove them
        for varid in var_ids_to_remove:
            if varid in Utils.variables:
                print(f"Removing varid: {varid}")
                rowwidget = Utils.variables[varid]['widget']
                self.remove_row(rowwidget, varid, 'Variable')
            else:
                print(f"WARNING: varid {varid} not found in Utils.variables")

    #MARK: - Devices Panel Methods
    def add_device_row(self, device_id=None, dev_data=None, canvas_reference=None):
        """Add a new device row"""
        print(f"Adding device row called with device_id: {device_id}, dev_data: {dev_data}")
        
        if device_id is None:
            device_id = f"device_{canvas_reference.devices_row_count}"
        self.device_id = device_id
        print(f"Adding device row {self.device_id}, dev_data: {dev_data}. Current devices: {Utils.devices}")
        
        Utils.devices[device_id] = {
            'name': '',
            'type': 'Output',
            'PIN': None,
            'widget': None,
            'name_imput': None,
            'type_input': None,
            'value_input': None
        } 
        
        canvas_reference.row_widget = QWidget()
        canvas_reference.row_layout = QHBoxLayout(canvas_reference.row_widget)
        canvas_reference.row_layout.setContentsMargins(5, 5, 5, 5)
 
        name_imput = QLineEdit()
        name_imput.setPlaceholderText("Name")
        if dev_data and 'name' in dev_data:
            name_imput.setText(dev_data['name'])
            Utils.devices[device_id]['name'] = dev_data['name']
        
        name_imput.textChanged.connect(lambda text, d_id=device_id, t="Device": self.name_changed(text, d_id, t))
        
        type_input = QComboBox()
        type_input.addItems(["Output", "Input", "PWM", "Button"])
        if dev_data and 'type' in dev_data:
            type_input.setCurrentText(dev_data['type'])
            Utils.devices[device_id]['type'] = dev_data['type']
        
        type_input.currentTextChanged.connect(lambda text, d_id=device_id, t="Device": self.type_changed(text, d_id, t))
        
        self.value_dev_input = QLineEdit()
        self.value_dev_input.setPlaceholderText("PIN")
        if dev_data and 'PIN' in dev_data:
            self.value_dev_input.setText(str(dev_data['PIN']))
            Utils.devices[device_id]['PIN'] = dev_data['PIN']
        regex = QRegularExpression(r"^\d*$")
        validator = QRegularExpressionValidator(regex, self)
        self.value_dev_input.setValidator(validator)
        self.value_dev_input.textChanged.connect(lambda text, d_id=device_id, t="Device": self.value_changed(text, d_id, t))
        
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
        
        Utils.devices[device_id]['widget'] = canvas_reference.row_widget
        Utils.devices[device_id]['name_imput'] = name_imput
        Utils.devices[device_id]['type_input'] = type_input
        Utils.devices[device_id]['value_input'] = self.value_dev_input
        

    def Clear_All_Devices(self):
        print("Clearing all devices")
        
        # Get a SNAPSHOT of device IDs BEFORE modifying anything
        device_ids_to_remove = list(Utils.devices.keys())
        print(f"Device IDs to remove: {device_ids_to_remove}")
        
        # Now remove them
        for device_id in device_ids_to_remove:
            if device_id in Utils.devices:
                print(f"Removing device_id: {device_id}")
                rowwidget = Utils.devices[device_id]['widget']
                self.remove_row(rowwidget, device_id, 'Device')
            else:
                print(f"WARNING: device_id {device_id} not found in Utils.devices")
    
    #MARK: - Common Methods
    def remove_row(self, row_widget, var_id, type, canvas_reference=None):
        """Remove a variable row"""
        print(f"Removing row {var_id} of type {type}")
        if type == "Variable":
            if var_id in Utils.var_items:
                del Utils.var_items[var_id]
                
            if var_id in Utils.variables:
                #print(f"Deleting {var_id}")
                del Utils.variables[var_id]
                for imput, var_ids in Utils.vars_same.items():
                    if var_id in var_ids:
                        var_ids.remove(var_id)
                        #print(f"Vars_same {var_ids}")
            
            for imput2, var in Utils.vars_same.items():
                #print(f"Var {var}, len var {len(var)}")
                if len(var) <= 1:
                    for var_id in var:
                        Utils.variables[var_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
            
            panel_layout = canvas_reference.var_layout
            panel_layout.removeWidget(row_widget)
            
            row_widget.setParent(None)
            row_widget.deleteLater()
            
            canvas_reference.variable_row_count -= 1
        elif type == "Device":
            if var_id in Utils.dev_items:
                del Utils.dev_items[var_id]
                
            if var_id in Utils.devices:
                #print(f"Deleting {var_id}")
                del Utils.devices[var_id]
                for imput, dev_ids in Utils.devs_same.items():
                    if var_id in dev_ids:
                        dev_ids.remove(var_id)
                        #print(f"Devs_same {dev_ids}")
            
            for imput2, dev in Utils.devs_same.items():
                #print(f"Dev {dev}, len dev {len(dev)}")
                if len(dev) <= 1:
                    for dev_id in dev:
                        Utils.devices[dev_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
            
            panel_layout = canvas_reference.dev_layout
            panel_layout.removeWidget(row_widget)
            
            row_widget.setParent(None)
            row_widget.deleteLater()
            
            canvas_reference.devices_row_count -= 1
        #print(f"Deleted variable: {var_id}")
    
    def name_changed(self, text, var_id, type):
        if type == "Variable":
            Utils.variables[var_id]['name'] = text

            if var_id in Utils.var_items:
                Utils.var_items[var_id] = text
            else:
                Utils.var_items.setdefault(var_id, text)
            # Step 1: Group all var_ids by their name value
            Utils.vars_same.clear()
            Utils.variables[var_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
            for v_id, v_info in Utils.variables.items():
                name = v_info['name_imput'].text().strip()
                if name:
                    Utils.vars_same.setdefault(name, []).append(v_id)
            
            # Step 2: Color red if duplicate
            for name, id_list in Utils.vars_same.items():
                #print(id_list)
                border_col = "border-color: #ff0000;" if len(id_list) > 1 else "border-color: #3F3F3F;"
                for v_id in id_list:
                    Utils.variables[v_id]['name_imput'].setStyleSheet(border_col)
            print("Utils.variables:", Utils.variables)
        
        elif type == "Device":
            Utils.devices[var_id]['name'] = text

            if var_id in Utils.dev_items:
                Utils.dev_items[var_id] = text
            else:
                Utils.dev_items.setdefault(var_id, text)
            print(f"dev_items: {Utils.dev_items}")
            # Step 1: Group all dev_ids by their name value
            Utils.devs_same.clear()
            Utils.devices[var_id]['name_imput'].setStyleSheet("border-color: #3F3F3F;")
            for d_id, d_info in Utils.devices.items():
                name = d_info['name_imput'].text().strip()
                if name:
                    Utils.devs_same.setdefault(name, []).append(d_id)
            
            # Step 2: Color red if duplicate
            for name, id_list in Utils.devs_same.items():
                #print(id_list)
                border_col = "border-color: #ff0000;" if len(id_list) > 1 else "border-color: #3F3F3F;"
                for d_id in id_list:
                    Utils.devices[d_id]['name_imput'].setStyleSheet(border_col)
            print("Calling refresh_all_blocks from name_changed")
            print(f"Utils.devices: {Utils.devices}")
    
    def type_changed(self, imput, id, type):
        #print(f"Updating variable {imput}")
        if type == "Variable":
            if id in Utils.variables:
                Utils.variables[id]['type'] = imput
                print(f"Type {id} value changed to: {imput}")
        elif type == "Device":
            if id in Utils.devices:
                Utils.devices[id]['type'] = imput
                print(f"Type {id} value changed to: {imput}")
    
    def value_changed(self, imput, id, type):
        #print(f"Updating variable {imput}")
        
        if type == "Variable":
            try:
                value = len(imput)
                
                if value > 4:
                    self.value_var_input.blockSignals(True)
                    imput = imput[:4]
                    self.value_var_input.setText(imput)
                    self.value_var_input.blockSignals(False)
                
                elif value < 0:
                    self.value_var_input.blockSignals(True)
                    self.value_var_input.setText("0")
                    self.value_var_input.blockSignals(False)
            except ValueError:
                    # Text is empty or can't convert (shouldn't happen with regex)
                    pass
            if id in Utils.variables:
                Utils.variables[id]['value'] = imput
                print(f"Value {id} value changed to: {imput}")
        elif type == "Device":
            try:
                value = len(imput)
                
                if value > 4:
                    self.value_dev_input.blockSignals(True)
                    imput = imput[:4]
                    self.value_dev_input.setText(imput)
                    self.value_dev_input.blockSignals(False)
                
                elif value < 0:
                    self.value_dev_input.blockSignals(True)
                    self.value_dev_input.setText("0")
                    self.value_dev_input.blockSignals(False)
            except ValueError:
                    # Text is empty or can't convert (shouldn't happen with regex)
                    pass
            if id in Utils.devices:
                Utils.devices[id]['PIN'] = imput
                print(f"device {id} PIN changed to: {imput}")   
    #MARK: - Other Methods
    def open_elements_window(self):
        """Open the elements window"""
        elements_window = ElementsWindow.get_instance(self.current_canvas)
        elements_window.open()
    
    def open_settings_window(self):
        """Open the device settings window"""
        device_settings_window = DeviceSettingsWindow.get_instance(self.current_canvas)
        device_settings_window.open()
    
    def open_help(self, which):
        """Open the help window"""
        HelpWindow = get_Help_Window()
        self.help_window_instance = HelpWindow.get_instance(self.current_canvas, which)
        self.help_window_instance.open()
    
    
    def block_management(self, block_id, window):
        """Track block windows"""
        self.blockIDs[block_id] = window
    
    def compile_code(self):
        """Compile the visual code"""
        try:
            print("Starting code compilation...")
            self.code_compiler.compile()
            print("Code compiled successfully")
        except Exception as e:
            print(f"Compilation error: {e}")
            pass
    
    # Menu actions
    
    def create_save_shortcut(self):
        """Create Ctrl+S keyboard shortcut for saving"""
        from PyQt6.QtGui import QKeySequence, QShortcut
        print("Creating save shortcut (Ctrl+S)")
        save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        save_shortcut.activated.connect(self.on_save_file)
    
    def setup_auto_save_timer(self):
        """Setup auto-save timer for every 5 minutes"""
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_project)
        
        # 5 minutes = 300,000 milliseconds
        self.auto_save_timer.start(300000)  # 300000 ms = 5 minutes
        
        print("✓ Auto-save timer started (every 5 minutes)")
    
    def get_current_time(self):
        """Get current time for logging"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def auto_save_project(self):
        """Auto-save current project"""
        name = Utils.project_data.metadata.get('name', 'Untitled')
        print(f"Auto-saving project '{name}'")
        try:
            if FileManager.save_project(name, is_autosave=True):
                print(f"✓ Auto-saved '{name}' at {self.get_current_time()}")
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
        print(f"Metadata: {Utils.project_data.metadata}")
        print(f"Saving project as '{name}'")
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

        self.clear_canvas()
        
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
            self.clear_canvas()
            if FileManager.load_project(item):
                self.rebuild_from_data()
                print(f"✓ Project '{item}' loaded")

    def clear_canvas(self):
        """Clear the canvas of all blocks and connections"""
        self.Clear_All_Variables()
        self.Clear_All_Devices()
        for canvas in Utils.canvas_instances.keys():
            print("Clearing canvas:", canvas)
            if canvas:
                canvas.path_manager.clear_all_paths()
                print("Cleared all paths")
                widget_ids_to_remove = []
                if canvas.reference == 'canvas':
                    widget_ids_to_remove = list(Utils.main_canvas['blocks'].keys())
                    print(f"Widget IDs to remove from main canvas: {widget_ids_to_remove}")
                    for block_id in widget_ids_to_remove:
                        if block_id in Utils.main_canvas['blocks']:
                            widget = Utils.main_canvas['blocks'][block_id]['widget']
                            print(f"Removing widget for block_id {block_id}: {widget}")
                            widget.setParent(None)  # Remove from parent
                            canvas.scene.removeItem(widget)  # Remove from scene
                            widget.deleteLater()
                            Utils.main_canvas['blocks'].pop(block_id, None)
                elif canvas.reference == 'function':
                    print("Clearing function canvas")
                    for f_id, f_info in Utils.functions.items():
                        if canvas == f_info.get('canvas'):
                            widget_ids_to_remove = list(Utils.functions[f_id]['blocks'].keys())
                            print(f"Widget IDs to remove from function {f_id} canvas: {widget_ids_to_remove}")
                            for block_id in widget_ids_to_remove:
                                if block_id in Utils.functions[f_id]['blocks']:
                                    widget = Utils.functions[f_id]['blocks'][block_id]['widget']
                                    print(f"Removing widget for block_id {block_id}: {widget}")
                                    widget.setParent(None)  # Remove from parent
                                    canvas.scene.removeItem(widget)  # Remove from scene
                                    widget.deleteLater()
                                    Utils.functions[f_id]['blocks'].pop(block_id, None)
                
                QCoreApplication.processEvents()
                
                canvas.update()
    
    def on_new_file(self):
        """Create new project"""
        self.clear_canvas()
        
        FileManager.new_project()
    
    def closeEvent(self, event):
        """Handle window close event - prompt to save if there are unsaved changes"""
        if hasattr(self, 'auto_save_timer') and self.auto_save_timer.isActive():
            self.auto_save_timer.stop()
        
        # ✅ Stop execution thread
        if hasattr(self, 'execution_thread') and self.execution_thread is not None:
            if self.execution_thread.isRunning():
                self.execution_thread.stop()
                self.execution_thread.wait(3000)
                self.execution_thread.terminate()
        name = Utils.project_data.metadata.get('name', 'Untitled')
        
        if name == 'Untitled':
            print("Closing project 'Untitled'")
            self.on_save_file_as()
            import gc
            gc.collect()
            event.accept()
            return
        
        # Save current state to compare file
        FileManager.save_project(name, is_compare=True)
        
        # Compare with last saved version
        comparison = FileManager.compare_projects(name)
        
        if comparison['has_changes']:
            # Show detailed change summary
            change_summary = self._build_change_summary(comparison)
            
            # Show dialog asking if user wants to save
            reply = QMessageBox.question(
                self,
                'Save Project?',
                f'Do you want to save changes before closing?\n\n{change_summary}',
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Save:
                if name == 'Untitled':
                    self.on_save_file_as()
                else:
                    self.on_save_file()
                
                self.clear_canvas()
                self.close_child_windows()
                import gc
                gc.collect()
                event.accept()
                
            elif reply == QMessageBox.StandardButton.Discard:
                self.clear_canvas()
                self.close_child_windows()
                import gc
                gc.collect()
                event.accept()
                
            else:  # Cancel
                event.ignore()
                return
        else:
            # No unsaved changes
            self.clear_canvas()
            self.close_child_windows()
            import gc
            gc.collect()
            event.accept()

    def _build_change_summary(self, comparison: dict) -> str:
        """Build human-readable summary of changes"""
        summary = []
        
        if comparison['blocks_changed']:
            summary.append(f"📦 Blocks modified")
        if comparison['connections_changed']:
            summary.append(f"🔗 Connections modified")
        if comparison['variables_changed']:
            summary.append(f"📋 Variables modified")
        if comparison['devices_changed']:
            summary.append(f"⚙️ Devices modified")
        if comparison['settings_changed']:
            summary.append(f"⚙️ Settings modified")
        
        if not summary:
            return "No changes detected."
        
        return "Changes detected:\n• " + "\n• ".join(summary)

    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes in the project"""
        name = Utils.project_data.metadata.get('name', 'Untitled')
        
        # Save current state to compare file for checking
        FileManager.save_project(name, is_compare=True)
        
        # Compare with last saved version
        comparison = FileManager.compare_projects(name)
        
        return comparison.get('has_changes', True)
        
    
    def close_child_windows(self):
        
        if self.help_window_instance is not None and self.help_window_instance.isVisible():
            self.help_window_instance.close()
        
        # Close Elements window if it exists
        try:
            elements_window = ElementsWindow.get_instance(self.current_canvas)
            if elements_window.isVisible():
                elements_window.close()
        except:
            pass
        
        # Close Device Settings window if it exists
        try:
            device_settings_window = DeviceSettingsWindow.get_instance(self.current_canvas)
            if device_settings_window.isVisible():
                device_settings_window.close()
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
            print("📝 Step 1: Compiling code...")
            self.code_compiler.compile()  # This creates File.py
            print("✓ Code compiled successfully to File.py")
            
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
            print("🚀 Step 3: Executing on device...")
            
            rpi_model = Utils.app_settings.rpi_model_index
            
            if rpi_model == 0:  # Pico W
                print("🎯 Target: Pico W (MicroPython)")
                if self.execute_on_pico_w():
                    print("✓ Code executed successfully!")
                    QMessageBox.information(
                        self,
                        "Success",
                        "Code compiled, executed, and uploaded successfully!",
                        QMessageBox.StandardButton.Ok
                    )
                else:
                    print("⚠️  Execution warning - Check device connection")
                    QMessageBox.warning(
                        self,
                        "Execution Issue",
                        "Code compiled but execution encountered issues. Check device connection and try again.",
                        QMessageBox.StandardButton.Ok
                    )
            
            elif rpi_model in [1, 2, 3, 4, 5, 6, 7]:  # Raspberry Pi
                print(f"🎯 Target: Raspberry Pi (GPIO) - Model {rpi_model}")
                # Execute on RPi in background thread
                self.execute_on_rpi_ssh_background()
                
                print("✓ Execution started on Raspberry Pi")
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
        print(f"[RPi Status] {status}")
    
    def on_execution_output(self, output):
        """Handle output from execution thread"""
        print(f"[RPi Output] {output}")
        QMessageBox.information(
            self,
            "Execution Output",
            output,
            QMessageBox.StandardButton.Ok
        )
    
    def on_execution_error(self, error):
        """Handle errors from execution thread"""
        print(f"[RPi Error] {error}")
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
                print("Attempting to use mpremote...")
                # mpremote will automatically detect and connect to Pico W
                result = subprocess.run(
                    ["mpremote", "cp", "File.py", ":/main.py"],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if result.returncode == 0:
                    print("✓ File uploaded via mpremote")
                    
                    # Run the code
                    result = subprocess.run(
                        ["mpremote", "run", "main.py"],
                        capture_output=True,
                        text=True,
                        timeout=15
                    )
                    
                    if result.returncode == 0:
                        print("✓ Code executed successfully")
                        if result.stdout:
                            print(f"Output: {result.stdout}")
                        return True
                    else:
                        print(f"⚠ Execution error: {result.stderr}")
                        return False
                else:
                    raise Exception("mpremote cp failed")
                    
            except (FileNotFoundError, subprocess.TimeoutExpired):
                # Fallback: Use pyboard.py
                print("Attempting fallback: pyboard.py method...")
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
                print("✓ Code executed via pyboard.py")
                if result.stdout:
                    print(f"Output: {result.stdout}")
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
                print("[MainWindow] ⏹️  Stopping previous execution...")
                self.execution_thread.stop()  # Signal it to stop
                
                # Wait for thread to finish (max 5 seconds)
                if not self.execution_thread.wait(5000):
                    print("[MainWindow] ⚠️  Warning: Thread didn't stop gracefully")
                    # Optional: Force terminate (not recommended, but available)
                    # self.execution_thread.terminate()
                
                print("[MainWindow] ✓ Previous execution stopped")
            
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
            print("[MainWindow] ✓ New execution started")
        
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
        print("Starting rebuild from saved data...")
        
        self._rebuild_settings()
        
        # Rebuild variable panel
        self._rebuild_variables_panel()
        
        # Rebuild devices panel
        self._rebuild_devices_panel()
        
        # Clear canvas and rebuild blocks
        self._rebuild_blocks()
        
        # Rebuild connections
        self._rebuild_connections()
        
        
        
        print("✓ Project rebuild complete")

    def _rebuild_settings(self):
        """Rebuild settings from project_data"""
        print(f"Rebuilding {len(Utils.project_data.settings)} settings...")
        print(f" RPi Model: {Utils.app_settings.rpi_model} (Index: {Utils.app_settings.rpi_model_index})")
        Utils.app_settings.rpi_model = Utils.project_data.settings.get('rpi_model', "RPI 4 model B")
        Utils.app_settings.rpi_model_index = Utils.project_data.settings.get('rpi_model_index', 6)
        print(f" RPi Model: {Utils.app_settings.rpi_model} (Index: {Utils.app_settings.rpi_model_index})")
        self.current_canvas.update()
        print(" Settings rebuilt")

    def _rebuild_blocks(self):
        """Recreate all block widgets on canvas from project_data"""
        print(f"Rebuilding {len(Utils.project_data.blocks)} blocks...")
        # Clear existing blocks from canvas
        for block_id in list(Utils.top_infos.keys()):
            if block_id in Utils.top_infos:
                widget = Utils.top_infos[block_id]['widget']
                widget.setParent(None)
                widget.deleteLater()
        
        Utils.top_infos.clear()
        
        # Recreate each block

        for block_id, block_data in Utils.project_data.blocks.items():
            block_id = str(block_id)
            print(f" Recreating block {block_id} of type {block_data['type']}...")
            try:
                # Create the block widget
                block_widget = self.add_block_from_data(
                    block_type=block_data['type'],
                    x=block_data['x'],
                    y=block_data['y'],
                    block_id=block_id
                )
                
                print(f" Utils.top_infos updated with block {block_id}")
                print(f" Utils.top_infos now has {len(Utils.top_infos)} blocks")
                print(f" Block data: {Utils.top_infos[block_id]}")
                print(f"  ✓ Block {block_id} ({block_data['type']}) recreated")
                
            except Exception as e:
                print(f"  ✗ Error recreating block {block_id}: {e}")

    def add_block_from_data(self, block_type, x, y, block_id):
        
        
        
        """Add a new block to the canvas"""
        block = BlockGraphicsItem(
            x=x, y=y,
            block_id=block_id,
            block_type=block_type,
            parent_canvas=self.current_canvas
        )
        
        block.value_1_name = Utils.project_data.blocks[block_id].get('value_1_name', "var1")
        #block.value_1_type = Utils.project_data.blocks[block_id].get('value_1_type', "N/A")
        block.value_2_name = Utils.project_data.blocks[block_id].get('value_2_name', "var2")
        #block.value_2_type = Utils.project_data.blocks[block_id].get('value_2_type', "N/A")
        block.operator = Utils.project_data.blocks[block_id].get('operator', "==")
        block.switch_state = Utils.project_data.blocks[block_id].get('switch_state', False)
        block.sleep_time = Utils.project_data.blocks[block_id].get('sleep_time', "1000")
        
        self.current_canvas.scene.addItem(block)
        
        # Store in Utils
        Utils.top_infos[block_id] = {
            'type': Utils.project_data.blocks[block_id]['type'],
            'id': block_id,
            'widget': block,
            'type': block_type,
            'width': block.boundingRect().width(),
            'height': block.boundingRect().height(),
            'x': x,
            'y': y,
            'value_1_name': Utils.project_data.blocks[block_id].get('value_1_name', "var1"),
            'value_1_type': Utils.project_data.blocks[block_id].get('value_1_type', "N/A"),
            'value_2_name': Utils.project_data.blocks[block_id].get('value_2_name', "var2"),
            'value_2_type': Utils.project_data.blocks[block_id].get('value_2_type', "N/A"),
            'operator': Utils.project_data.blocks[block_id].get('operator', "=="),
            'switch_state': Utils.project_data.blocks[block_id].get('switch_state', False),
            'sleep_time': Utils.project_data.blocks[block_id].get('sleep_time', "1000"),
            'in_connections': Utils.project_data.blocks[block_id].get('in_connections', []),
            'out_connections': Utils.project_data.blocks[block_id].get('out_connections', [])
        }
        block.connect_graphics_signals()
        return block

    def _rebuild_connections(self):
        """Recreate all connection paths from projectdata"""
        print(f"Rebuilding {len(Utils.project_data.connections)} connections...")
        
        # Don't clear! The blocks should already be in Utils.top_infos from rebuild_blocks()
        # Utils.paths.clear()  # KEEP THIS
        self.current_canvas.path_manager.clear_all_paths()
        
        print(f"Utils.top_infos contains: {list(Utils.top_infos.keys())}")
        print(f"Project connections: {list(Utils.project_data.connections.keys())}")
        print(f"Path conections before rebuild: {Utils.project_data.connections}")
        for conn_id, conn_data in Utils.project_data.connections.items():
            try:
                from_block_id = str(conn_data.get("from"))
                to_block_id = str(conn_data.get("to"))
                
                print(f"Processing connection {conn_id}: {from_block_id} -> {to_block_id}")
                
                # DEBUG: Check what's actually in Utils.top_infos
                print(f"Available block IDs in Utils.top_infos: {list(Utils.top_infos.keys())}")
                print(f"Is {from_block_id} in top_infos? {from_block_id in Utils.top_infos}")
                print(f"Is {to_block_id} in top_infos? {to_block_id in Utils.top_infos}")
                
                if from_block_id not in Utils.top_infos or to_block_id not in Utils.top_infos:
                    print(f"❌ Connection {conn_id}: Missing block reference!")
                    print(f"  from_block_id ({from_block_id}) exists: {from_block_id in Utils.top_infos}")
                    print(f"  to_block_id ({to_block_id}) exists: {to_block_id in Utils.top_infos}")
                    continue
                
                from_block = Utils.top_infos[from_block_id]
                to_block = Utils.top_infos[to_block_id]
                
                from_blockwidget = from_block.get("widget")
                to_blockwidget = to_block.get("widget")
                
                path_item = PathGraphicsItem(
                    from_block=from_blockwidget,
                    to_block=to_blockwidget,
                    path_id=conn_id,
                    parent_canvas=self.current_canvas,
                    to_circle_type=conn_data.get("to_circle_type", "in"),
                    from_circle_type=conn_data.get("from_circle_type", "out")
                )
                self.current_canvas.scene.addItem(path_item)
                # Recreate connection
                Utils.paths[conn_id] = {
                    'from': from_block_id,
                    'from_circle_type': conn_data.get("from_circle_type", "out"),
                    'to': to_block_id,
                    'to_circle_type': conn_data.get("to_circle_type", "in"),
                    'waypoints': conn_data.get("waypoints", []),
                    'color': QColor(31, 83, 141),
                    'item': path_item
                }
                Utils.scene_paths[conn_id] = path_item
                
                # Update block connection references
                if conn_id not in from_block.get("out_connections", []):
                    from_block.get("out_connections", []).append(conn_id)
                if conn_id not in to_block.get("in_connections", []):
                    to_block.get("in_connections", []).append(conn_id)
                
                print(f"✓ Connection {conn_id} recreated")
                
            except Exception as e:
                print(f"❌ Error recreating connection {conn_id}: {e}")
                import traceback
                traceback.print_exc()
        
        self.current_canvas.update()

    def _rebuild_variables_panel(self):
        """Recreate variables in the side panel"""
        print(f"Rebuilding {len(Utils.project_data.variables)} variables...")
        
        if not self.variable_frame:
            self.show_variable_frame()
        
        panel_layout = self.var_layout
        
        # Clear existing variable rows
        for var_id in list(Utils.variables.keys()):
            if var_id in Utils.variables:
                widget = Utils.variables[var_id].get('widget')
                if widget:
                    panel_layout.removeWidget(widget)
                    widget.setParent(None)
                    widget.deleteLater()
        
        Utils.variables.clear()
        Utils.var_items.clear()
        Utils.vars_same.clear()
        self.variable_row_count = 1
        
        # Recreate each variable
        for var_id, var_data in Utils.project_data.variables.items():
            try:
                # Add variable row to UI
                self.add_variable_row(var_id, var_data)
                for v_id, v_info in Utils.variables.items():
                    Utils.var_items[v_id] = v_info['name']
                print(f"  ✓ Variable {var_id} ({var_data['name']}) recreated")
                
            except Exception as e:
                print(f"  ✗ Error recreating variable {var_id}: {e}")
        if self.variable_frame:
            self.hide_variable_frame()

    def _rebuild_devices_panel(self):
        """Recreate devices in the side panel"""
        print(f"Rebuilding {len(Utils.project_data.devices)} devices...")
        
        if not self.Devices_frame:
            self.show_devices_frame()
            
        panel_layout = self.dev_layout
        
        # Clear existing device rows
        for dev_id in list(Utils.devices.keys()):
            if dev_id in Utils.devices:
                widget = Utils.devices[dev_id].get('widget')
                if widget:
                    panel_layout.removeWidget(widget)
                    widget.setParent(None)
                    widget.deleteLater()
        
        Utils.devices.clear()
        Utils.dev_items.clear()
        Utils.devs_same.clear()
        self.devices_row_count = 0
        
        # Recreate each device
        for dev_id, dev_data in Utils.project_data.devices.items():
            try:
                # Add device row to UI
                self.add_device_row(dev_id, dev_data)
                for d_id, d_info in Utils.devices.items():
                    Utils.dev_items[d_id] = d_info['name']
                print(f"  ✓ Device {dev_id} ({dev_data['name']}) recreated")
                
            except Exception as e:
                print(f"  ✗ Error recreating device {dev_id}: {e}")

        if self.Devices_frame:
            self.hide_devices_frame()
        
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
