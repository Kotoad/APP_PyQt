"""
STATE MACHINE FOR PyQt6 - TAILORED TO YOUR PROJECT

Based on your visual programming interface project, this shows:
- Canvas state management (EMPTY, EDITING, RUNNING, ERROR)
- Window state coordination (Main, Settings, Help, Elements)
- Block/Path state tracking
- Device execution states

For your architecture with:
  ├─ MainWindow (QMainWindow)
  ├─ GridCanvas (QGraphicsView + QGraphicsScene)
  ├─ Multiple Dialog windows (Settings, Help, Elements)
  └─ Block/Path/Device management system
"""

from enum import Enum, auto
from PyQt6.QtCore import pyqtSignal, QObject


# ============================================================================
# CANVAS STATE MACHINE
# ============================================================================

class CanvasState(Enum):
    """States for a single GridCanvas"""
    EMPTY = auto()        # No blocks, ready for input
    EDITING = auto()      # User adding/modifying blocks
    COMPILING = auto()    # Code compilation in progress
    RUNNING = auto()      # Code executing on RPi
    PAUSED = auto()       # Execution paused
    ERROR = auto()        # Compilation or execution error
    IDLE = auto()         # Compiled, not running


class CanvasStateMachine(QObject):
    """
    Manages state of a single canvas (editing, compiling, running)
    Emits signals for UI updates tied to canvas state
    
    Usage in your GridCanvas:
        self.state_machine = CanvasStateMachine()
        self.state_machine.state_changed.connect(self.on_state_changed)
    """
    
    state_changed = pyqtSignal(CanvasState)  # Signal when state changes
    block_added = pyqtSignal()               # Signal block was added
    compilation_started = pyqtSignal()       # Compilation starting
    execution_started = pyqtSignal()         # Code running on RPi
    error_occurred = pyqtSignal(str)         # Error with message
    
    def __init__(self):
        super().__init__()
        self.state = CanvasState.EMPTY
        self.error_message = ""
        self.block_count = 0
    
    # Guard conditions
    def can_compile(self) -> bool:
        """Can only compile from EDITING or IDLE states"""
        return self.state in (CanvasState.EDITING, CanvasState.IDLE)
    
    def can_run(self) -> bool:
        """Can only run if compilation succeeded (IDLE state)"""
        return self.state == CanvasState.IDLE
    
    def can_edit(self) -> bool:
        """Can edit if not currently executing"""
        return self.state in (CanvasState.EMPTY, CanvasState.EDITING, CanvasState.ERROR)
    
    # State transitions
    def on_block_added(self):
        """Called when user adds a block"""
        if self.state == CanvasState.EMPTY:
            self.transition_to(CanvasState.EDITING)
        self.block_added.emit()
    
    def on_block_modified(self):
        """Called when user modifies a block"""
        if self.state == CanvasState.IDLE:
            # If compiled code is modified, revert to editing
            self.transition_to(CanvasState.EDITING)
    
    def on_compile_start(self):
        """Called when compilation button clicked"""
        if not self.can_compile():
            return False
        
        self.transition_to(CanvasState.COMPILING)
        self.compilation_started.emit()
        return True
    
    def on_compile_success(self):
        """Called when compilation completes successfully"""
        self.transition_to(CanvasState.IDLE)
    
    def on_compile_error(self, error_msg: str):
        """Called when compilation fails"""
        self.error_message = error_msg
        self.transition_to(CanvasState.ERROR)
        self.error_occurred.emit(error_msg)
    
    def on_run_start(self):
        """Called when code execution starts"""
        if not self.can_run():
            return False
        
        self.transition_to(CanvasState.RUNNING)
        self.execution_started.emit()
        return True
    
    def on_run_pause(self):
        """Called when execution paused"""
        if self.state == CanvasState.RUNNING:
            self.transition_to(CanvasState.PAUSED)
    
    def on_run_resume(self):
        """Called when execution resumed"""
        if self.state == CanvasState.PAUSED:
            self.transition_to(CanvasState.RUNNING)
    
    def on_run_stop(self):
        """Called when execution stopped"""
        if self.state in (CanvasState.RUNNING, CanvasState.PAUSED):
            self.transition_to(CanvasState.IDLE)
    
    def on_run_error(self, error_msg: str):
        """Called when execution error occurs"""
        self.error_message = error_msg
        self.transition_to(CanvasState.ERROR)
        self.error_occurred.emit(error_msg)
    
    def on_error_clear(self):
        """Called when user clears error"""
        self.transition_to(CanvasState.EDITING)
        self.error_message = ""
    
    def transition_to(self, new_state: CanvasState):
        """Transition to new state and emit signal"""
        if new_state != self.state:
            self.state = new_state
            self.state_changed.emit(new_state)
            print(f"[Canvas State] {self.state.name}")


# ============================================================================
# APPLICATION WINDOW STATE MACHINE
# ============================================================================

class AppWindowState(Enum):
    """States for main application window"""
    STARTUP = auto()         # App initializing
    IDLE = auto()            # Ready for input
    ELEMENTS_OPEN = auto()   # Elements dialog open
    SETTINGS_OPEN = auto()   # Settings dialog open
    HELP_OPEN = auto()       # Help dialog open
    EXPORTING = auto()       # Exporting/saving project
    ERROR = auto()           # Application error


class MainWindowStateMachine(QObject):
    """
    Manages state of MainWindow and all its dialogs
    
    Usage in your MainWindow.__init__:
        self.app_state_machine = MainWindowStateMachine()
        self.app_state_machine.dialog_opened.connect(self.on_dialog_opened)
    """
    
    state_changed = pyqtSignal(AppWindowState)
    dialog_opened = pyqtSignal(str)    # "elements", "settings", "help"
    dialog_closed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.state = AppWindowState.STARTUP
        self.open_dialogs = set()
    
    def can_open_dialog(self) -> bool:
        """Check if application state allows opening dialogs"""
        return self.state not in (AppWindowState.EXPORTING, AppWindowState.ERROR)
    
    def on_startup_complete(self):
        """App initialization complete"""
        self.transition_to(AppWindowState.IDLE)
    
    def on_elements_open(self):
        """Elements dialog opened"""
        if self.can_open_dialog():
            self.open_dialogs.add("elements")
            self.dialog_opened.emit("elements")
    
    def on_elements_close(self):
        """Elements dialog closed"""
        self.open_dialogs.discard("elements")
        self.dialog_closed.emit("elements")
    
    def on_settings_open(self):
        """Settings dialog opened"""
        if self.can_open_dialog():
            self.open_dialogs.add("settings")
            self.dialog_opened.emit("settings")
    
    def on_settings_close(self):
        """Settings dialog closed"""
        self.open_dialogs.discard("settings")
        self.dialog_closed.emit("settings")
    
    def on_help_open(self):
        """Help dialog opened"""
        if self.can_open_dialog():
            self.open_dialogs.add("help")
            self.dialog_opened.emit("help")
    
    def on_help_close(self):
        """Help dialog closed"""
        self.open_dialogs.discard("help")
        self.dialog_closed.emit("help")
    
    def on_export_start(self):
        """Project export started"""
        self.transition_to(AppWindowState.EXPORTING)
    
    def on_export_complete(self):
        """Project export finished"""
        self.transition_to(AppWindowState.IDLE)
    
    def on_error(self):
        """Application error occurred"""
        self.transition_to(AppWindowState.ERROR)
    
    def transition_to(self, new_state: AppWindowState):
        """Transition to new state"""
        if new_state != self.state:
            self.state = new_state
            self.state_changed.emit(new_state)
            print(f"[App State] {self.state.name}")


# ============================================================================
# BLOCK STATE MACHINE
# ============================================================================

class BlockState(Enum):
    """States for an individual block"""
    SELECTED = auto()
    DESELECTED = auto()
    EDITING = auto()
    CONNECTED = auto()
    ERROR = auto()


class BlockStateMachine(QObject):
    """
    Manages state of a single block (BlockGraphicsItem)
    
    Usage in your BlockGraphicsItem.__init__:
        self.state_machine = BlockStateMachine()
        self.state_machine.state_changed.connect(self.on_block_state_changed)
    """
    
    state_changed = pyqtSignal(BlockState)
    highlight_changed = pyqtSignal(bool)  # True = highlight, False = normal
    
    def __init__(self):
        super().__init__()
        self.state = BlockState.DESELECTED
    
    def on_selected(self):
        """Block clicked/selected"""
        self.transition_to(BlockState.SELECTED)
        self.highlight_changed.emit(True)
    
    def on_deselected(self):
        """Block deselected"""
        self.transition_to(BlockState.DESELECTED)
        self.highlight_changed.emit(False)
    
    def on_edit_start(self):
        """Inspector panel opened for this block"""
        self.transition_to(BlockState.EDITING)
    
    def on_connection_made(self):
        """Block connected to another block"""
        self.transition_to(BlockState.CONNECTED)
    
    def on_validation_error(self):
        """Block has invalid configuration"""
        self.transition_to(BlockState.ERROR)
        self.highlight_changed.emit(True)  # Highlight in red
    
    def on_validation_clear(self):
        """Error condition resolved"""
        self.transition_to(BlockState.DESELECTED)
        self.highlight_changed.emit(False)
    
    def transition_to(self, new_state: BlockState):
        """Transition to new state"""
        if new_state != self.state:
            self.state = new_state
            self.state_changed.emit(new_state)


# ============================================================================
# DEVICE EXECUTION STATE MACHINE
# ============================================================================

class DeviceExecutionState(Enum):
    """States for device during code execution"""
    IDLE = auto()
    INITIALIZING = auto()
    RUNNING = auto()
    ERROR = auto()
    STOPPED = auto()


class DeviceExecutionMachine(QObject):
    """
    Manages state of Raspberry Pi/device during code execution
    
    Usage in your RPiExecutionThread:
        self.device_state = DeviceExecutionMachine()
        self.device_state.status_changed.connect(self.update_status_bar)
    """
    
    status_changed = pyqtSignal(DeviceExecutionState, str)  # state, message
    connection_failed = pyqtSignal(str)  # error message
    
    def __init__(self):
        super().__init__()
        self.state = DeviceExecutionState.IDLE
        self.connection_timeout = 10
    
    def on_connection_start(self):
        """Starting SSH connection"""
        self.transition_to(DeviceExecutionState.INITIALIZING, 
                          "Connecting to RPi...")
    
    def on_connection_success(self):
        """SSH connection established"""
        self.transition_to(DeviceExecutionState.INITIALIZING,
                          "Connected, initializing...")
    
    def on_connection_failed(self, error: str):
        """SSH connection failed"""
        self.transition_to(DeviceExecutionState.ERROR, 
                          f"Connection failed: {error}")
        self.connection_failed.emit(error)
    
    def on_execution_start(self):
        """Code execution started"""
        self.transition_to(DeviceExecutionState.RUNNING,
                          "Code executing...")
    
    def on_execution_error(self, error: str):
        """Execution error occurred"""
        self.transition_to(DeviceExecutionState.ERROR,
                          f"Execution error: {error}")
    
    def on_execution_complete(self):
        """Execution completed successfully"""
        self.transition_to(DeviceExecutionState.STOPPED,
                          "Execution complete")
    
    def on_stop_signal(self):
        """User stopped execution"""
        self.transition_to(DeviceExecutionState.STOPPED,
                          "Stopped by user")
    
    def transition_to(self, new_state: DeviceExecutionState, message: str):
        """Transition to new state with status message"""
        if new_state != self.state:
            self.state = new_state
            self.status_changed.emit(new_state, message)
            print(f"[Device] {self.state.name}: {message}")


# ============================================================================
# INTEGRATION EXAMPLE - How to use in your MainWindow
# ============================================================================

"""
EXAMPLE: Integrating state machines into your MainWindow

In your main_pyqt.py or GUI_pyqt.py:

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create state machines
        self.app_state_machine = MainWindowStateMachine()
        self.canvas_state_machine = CanvasStateMachine()
        
        # Connect signals to slots
        self.app_state_machine.dialog_opened.connect(self.on_dialog_opened)
        self.canvas_state_machine.state_changed.connect(self.on_canvas_state_changed)
        self.canvas_state_machine.error_occurred.connect(self.on_canvas_error)
        
        # When user clicks "Elements" button:
        self.elements_button.clicked.connect(self.on_elements_button_click)
    
    def on_elements_button_click(self):
        # State machine manages dialog state
        self.app_state_machine.on_elements_open()
        self.elements_window.show()
    
    def on_dialog_opened(self, dialog_name: str):
        # Update UI based on which dialog opened
        print(f"Dialog opened: {dialog_name}")
    
    def on_canvas_state_changed(self, state: CanvasState):
        # Update buttons/UI based on canvas state
        if state == CanvasState.EDITING:
            self.compile_button.setEnabled(True)
            self.run_button.setEnabled(False)
        elif state == CanvasState.IDLE:
            self.compile_button.setEnabled(True)
            self.run_button.setEnabled(True)
        elif state == CanvasState.RUNNING:
            self.compile_button.setEnabled(False)
            self.run_button.setText("Stop")
    
    def on_canvas_error(self, error_msg: str):
        # Handle compilation/execution errors
        QMessageBox.critical(self, "Error", error_msg)
        self.statusBar().showMessage(f"Error: {error_msg}")
"""


# ============================================================================
# QUICK PATTERNS FOR YOUR PROJECT
# ============================================================================

"""
Pattern 1: Block Added
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
In your GridCanvas.addBlock():
    self.state_machine.on_block_added()

Pattern 2: Compilation Workflow
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
In your compile button handler:
    if self.canvas_state_machine.on_compile_start():
        # Start compilation in thread
        self.code_compiler.compile()
    
In compilation thread success callback:
    self.canvas_state_machine.on_compile_success()

In compilation thread error callback:
    self.canvas_state_machine.on_compile_error("Syntax error at line 5")

Pattern 3: Execution Workflow
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
In your run button handler:
    if self.canvas_state_machine.on_run_start():
        self.execution_thread.start()
    
In execution thread:
    self.device_state_machine.on_connection_start()
    try:
        ssh.connect(...)
        self.device_state_machine.on_connection_success()
    except:
        self.device_state_machine.on_connection_failed(str(error))

Pattern 4: Dialog State Management
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
In your elements button handler:
    self.app_state_machine.on_elements_open()
    self.elements_window.show()

When elements window closes:
    self.app_state_machine.on_elements_close()

Pattern 5: Block Selection State
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
In your BlockGraphicsItem.mousePressEvent():
    self.state_machine.on_selected()

In your canvas deselect handler:
    self.state_machine.on_deselected()
"""
