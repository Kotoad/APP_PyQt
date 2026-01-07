"""
HOW TO INTEGRATE STATE MACHINES INTO YOUR EXISTING PyQt6 PROJECT

This guide shows exactly where to add state machines to your existing code:
- GUI_pyqt.py (MainWindow)
- spawn_elements_pyqt.py (GridCanvas)
- Help_window.py, settings_window.py (Dialog windows)
- code_compiler.py (Compilation states)
"""

# ============================================================================
# 1. UPDATE YOUR Imports.py
# ============================================================================

"""
Add these imports to the top of your Imports.py:

from enum import Enum, auto
from PyQt6.QtCore import pyqtSignal, QObject

Then add to the lazy loaders:

def get_state_machines():
    from pyqt6_state_machines import (
        CanvasStateMachine, MainWindowStateMachine, 
        BlockStateMachine, DeviceExecutionMachine
    )
    return (CanvasStateMachine, MainWindowStateMachine, 
            BlockStateMachine, DeviceExecutionMachine)
"""


# ============================================================================
# 2. UPDATE GUI_pyqt.py - MainWindow
# ============================================================================

"""
In your MainWindow.__init__(), add after creating the GUI:

    def __init__(self):
        super().__init__()
        # ... existing code ...
        
        # NEW: Add state machines
        from pyqt6_state_machines import MainWindowStateMachine, CanvasStateMachine
        
        self.app_state_machine = MainWindowStateMachine()
        self.canvas_state_machine = CanvasStateMachine()
        
        # Connect signals
        self.app_state_machine.state_changed.connect(self._on_app_state_changed)
        self.canvas_state_machine.state_changed.connect(self._on_canvas_state_changed)
        self.canvas_state_machine.error_occurred.connect(self._on_canvas_error)
        
        # Set initial app state to IDLE when window ready
        self.app_state_machine.on_startup_complete()


Update your button handlers to use state machines:

    def compileandupload(self):
        \"\"\"Compile button handler\"\"\"
        # NEW: Check if compilation is allowed
        if not self.canvas_state_machine.on_compile_start():
            QMessageBox.warning(self, "Invalid State", 
                              "Cannot compile in current state")
            return
        
        # Existing compilation code
        try:
            self.codecompiler.compile()
            # When compilation succeeds:
            self.canvas_state_machine.on_compile_success()
        except Exception as e:
            # When compilation fails:
            self.canvas_state_machine.on_compile_error(str(e))


    def openelementswindow(self):
        \"\"\"Elements button handler\"\"\"
        # NEW: Track dialog state
        self.app_state_machine.on_elements_open()
        
        elementswindow = ElementsWindow.getinstance(self.currentcanvas)
        elementswindow.open()


Add new slot methods:

    def _on_app_state_changed(self, new_state):
        \"\"\"Update UI when app state changes\"\"\"
        # Disable/enable buttons based on state
        if new_state.name == "EXPORTING":
            self.compile_button.setEnabled(False)
            self.run_button.setEnabled(False)
        elif new_state.name == "IDLE":
            self.compile_button.setEnabled(True)
    
    def _on_canvas_state_changed(self, new_state):
        \"\"\"Update canvas UI based on compilation/execution state\"\"\"
        print(f"Canvas state changed to: {new_state.name}")
        
        if new_state.name == "EDITING":
            self.compile_button.setText("Compile")
            self.compile_button.setEnabled(True)
            self.run_button.setEnabled(False)
        
        elif new_state.name == "IDLE":
            self.compile_button.setText("Recompile")
            self.compile_button.setEnabled(True)
            self.run_button.setText("Run")
            self.run_button.setEnabled(True)
        
        elif new_state.name == "COMPILING":
            self.compile_button.setEnabled(False)
            self.run_button.setEnabled(False)
            self.statusBar().showMessage("Compiling...")
        
        elif new_state.name == "RUNNING":
            self.compile_button.setEnabled(False)
            self.run_button.setText("Stop")
            self.run_button.setEnabled(True)
            self.statusBar().showMessage("Code running on RPi...")
        
        elif new_state.name == "ERROR":
            self.compile_button.setEnabled(True)
            self.run_button.setText("Run")
            self.statusBar().showMessage("Error - see details")
    
    def _on_canvas_error(self, error_msg: str):
        \"\"\"Handle canvas errors\"\"\"
        QMessageBox.critical(self, "Error", error_msg)
"""


# ============================================================================
# 3. UPDATE spawn_elements_pyqt.py - GridCanvas & BlockGraphicsItem
# ============================================================================

"""
In your GridCanvas.__init__(), add:

    def __init__(self, ...):
        super().__init__()
        # ... existing code ...
        
        # NEW: Add state machine
        from pyqt6_state_machines import CanvasStateMachine
        self.state_machine = CanvasStateMachine()
        self.state_machine.state_changed.connect(self._on_state_changed)


When a block is added in GridCanvas.addblock():

    def addblock(self, blocktype, x, y, blockid):
        # ... existing code ...
        
        # NEW: Update state machine
        if len(Utils.maincanvasblocks) == 0:
            # First block added
            self.state_machine.on_block_added()
        else:
            # Additional blocks
            self.state_machine.on_block_added()


When a block is modified:

    def _on_block_modified(self, blockid):
        \"\"\"Called when block properties change\"\"\"
        # NEW: Update canvas state
        self.state_machine.on_block_modified()


In your BlockGraphicsItem.__init__(), add:

    def __init__(self, x, y, blockid, blocktype, parentcanvas, mainwindow=None):
        super().__init__()
        # ... existing code ...
        
        # NEW: Add state machine
        from pyqt6_state_machines import BlockStateMachine
        self.state_machine = BlockStateMachine()
        self.state_machine.highlight_changed.connect(self._on_highlight_changed)


In BlockGraphicsItem.mousePressEvent():

    def mousePressEvent(self, event):
        # ... existing code ...
        
        # NEW: Update block state
        self.state_machine.on_selected()
        self.update()  # Redraw with highlight


Add highlight handling:

    def _on_highlight_changed(self, should_highlight):
        \"\"\"Update visual feedback when block selected\"\"\"
        self.is_highlighted = should_highlight
        self.update()  # Trigger repaint


Update paint() method to show selection:

    def paint(self, painter, option, widget):
        # ... existing code ...
        
        # NEW: Draw highlight border if selected
        if hasattr(self, 'is_highlighted') and self.is_highlighted:
            painter.setPen(QPen(QColor(0, 255, 0), 3))  # Green border
        else:
            painter.setPen(QPen(QColor(0, 0, 0), self.borderwidth))
        
        # ... rest of paint code ...
"""


# ============================================================================
# 4. UPDATE GUI_pyqt.py - RPiExecutionThread
# ============================================================================

"""
In your RPiExecutionThread.__init__(), add:

    def __init__(self, sshconfig):
        super().__init__()
        # ... existing code ...
        
        # NEW: Add device execution state machine
        from pyqt6_state_machines import DeviceExecutionMachine
        self.device_state = DeviceExecutionMachine()
        self.device_state.status_changed.connect(self._on_device_status_changed)


In your RPiExecutionThread.run(), add state machine calls:

    def run(self):
        # NEW: Connection state
        self.device_state.on_connection_start()
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            try:
                ssh.connect(...)
                # NEW: Connection succeeded
                self.device_state.on_connection_success()
            except Exception as e:
                # NEW: Connection failed
                self.device_state.on_connection_failed(str(e))
                return
            
            # ... existing upload code ...
            
            # NEW: Execution state
            self.device_state.on_execution_start()
            
            # ... existing execution code ...
            
            # NEW: Execution completed
            self.device_state.on_execution_complete()
            
        except Exception as e:
            # NEW: Execution error
            self.device_state.on_execution_error(str(e))


When execution is stopped:

    def stop(self):
        \"\"\"Stop execution\"\"\"
        with self.stoplock:
            self.shouldstop = True
        
        # NEW: Update state
        self.device_state.on_stop_signal()
"""


# ============================================================================
# 5. UPDATE Help_window.py & settings_window.py - Dialog Windows
# ============================================================================

"""
In Help_window.open():

    def open(self):
        # NEW: Notify main window
        if hasattr(self.parentcanvas, 'mainwindow'):
            self.parentcanvas.mainwindow.app_state_machine.on_help_open()
        
        self.show()
        self.raise_()
        self.activateWindow()


In Help_window.closeEvent():

    def closeEvent(self, event):
        # NEW: Notify main window
        if hasattr(self.parentcanvas, 'mainwindow'):
            self.parentcanvas.mainwindow.app_state_machine.on_help_close()
        
        event.accept()


Same pattern for settings_window.py:

    def open(self):
        if hasattr(self.parentcanvas, 'mainwindow'):
            self.parentcanvas.mainwindow.app_state_machine.on_settings_open()
        # ... existing code ...
    
    def closeEvent(self, event):
        if hasattr(self.parentcanvas, 'mainwindow'):
            self.parentcanvas.mainwindow.app_state_machine.on_settings_close()
        event.accept()
"""


# ============================================================================
# STATE MACHINE REFERENCE FOR YOUR PROJECT
# ============================================================================

"""
CanvasState Transitions:
    EMPTY → EDITING (when first block added)
    EDITING → COMPILING (when user clicks compile)
    COMPILING → IDLE (compile success) or ERROR (compile failure)
    IDLE → RUNNING (when user clicks run)
    RUNNING → PAUSED (when user clicks pause)
    PAUSED → RUNNING (when user clicks resume)
    RUNNING/PAUSED → IDLE (when execution stops)
    Any → ERROR (when error occurs)
    ERROR → EDITING (when user clears error)

MainWindowState Transitions:
    STARTUP → IDLE (when window fully initialized)
    IDLE → ELEMENTS_OPEN (when elements dialog opens)
    ELEMENTS_OPEN → IDLE (when elements dialog closes)
    IDLE → SETTINGS_OPEN (when settings dialog opens)
    SETTINGS_OPEN → IDLE (when settings dialog closes)
    IDLE → HELP_OPEN (when help dialog opens)
    HELP_OPEN → IDLE (when help dialog closes)
    Any → EXPORTING (during save/export)
    EXPORTING → IDLE (save/export complete)

BlockState Transitions:
    DESELECTED ↔ SELECTED (click/deselect)
    SELECTED → EDITING (when inspector opens)
    EDITING → SELECTED (when inspector closes)
    Any → ERROR (validation fails)
    ERROR → DESELECTED (error cleared)

DeviceExecutionState Transitions:
    IDLE → INITIALIZING (connection starting)
    INITIALIZING → RUNNING (connection succeeded, code running)
    INITIALIZING → ERROR (connection failed)
    RUNNING → STOPPED (execution completed or stopped by user)
    RUNNING → ERROR (execution error)
    ERROR → IDLE (when error cleared/user restarts)
"""


# ============================================================================
# TESTING YOUR STATE MACHINES
# ============================================================================

"""
Test in Python REPL:

from pyqt6_state_machines import CanvasStateMachine, CanvasState

# Create machine
sm = CanvasStateMachine()
print(sm.state)  # CanvasState.EMPTY

# Test transitions
sm.on_block_added()
print(sm.state)  # CanvasState.EDITING

# Test guard
if sm.can_compile():
    sm.on_compile_start()
    print(sm.state)  # CanvasState.COMPILING

# Simulate success
sm.on_compile_success()
print(sm.state)  # CanvasState.IDLE

# Test running
sm.on_run_start()
print(sm.state)  # CanvasState.RUNNING

# Test error
sm.on_run_error("Connection failed")
print(sm.state)  # CanvasState.ERROR
print(sm.error_message)  # "Connection failed"
"""


# ============================================================================
# BENEFITS OF STATE MACHINES IN YOUR PROJECT
# ============================================================================

"""
1. BUTTON MANAGEMENT
   - Automatically enable/disable buttons based on canvas state
   - Can't run without compiling first (guards prevent it)
   - Can't modify code while executing

2. ERROR TRACKING
   - Clear error messages tied to specific states
   - User knows exact state of application
   - Can't accidentally perform invalid operations

3. SIGNAL FLOW
   - State changes emit signals connected to UI updates
   - Decouples state logic from UI rendering
   - Easy to debug: just track state changes

4. DIALOG MANAGEMENT
   - Track which dialogs are open
   - Prevent opening multiple instances of same dialog
   - Automatically handle window state when dialogs close

5. EXECUTION SAFETY
   - RPi connection state tracked explicitly
   - Can't execute if not connected
   - Clear visibility into what's happening

6. FUTURE EXTENSIBILITY
   - Easy to add new states (PAUSE, RESUME, etc.)
   - Guards make adding restrictions simple
   - Signals provide integration points
"""
