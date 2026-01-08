from enum import Enum, auto

from Imports import pyqtSignal, QObject

class CanvasState(Enum):
    IDLE = auto()
    ADDING_BLOCK = auto()
    ADDING_PATH = auto()
    MOVING_ITEM = auto()
    DELETING_ITEM = auto()

class CanvasStateMachine(QObject):
    state_changed = pyqtSignal(CanvasState)

    def __init__(self):
        super().__init__()
        self.state = CanvasState.IDLE
    
    def can_place_block(self):
        return self.state == CanvasState.IDLE

    def can_move_item(self):
        return self.state in {CanvasState.IDLE, CanvasState.MOVING_ITEM}
    
    def can_delete_item(self):
        return self.state == CanvasState.IDLE
    
    def can_add_path(self):
        return self.state == CanvasState.IDLE

    def can_idle(self):
        return self.state != CanvasState.IDLE

    def on_adding_block(self):
        if self.can_place_block():
            self.change_state(CanvasState.ADDING_BLOCK)
            return True
        return False

    def on_moving_item(self):
        if self.can_move_item():
            self.change_state(CanvasState.MOVING_ITEM)
            return True
        return False

    def on_deleting_item(self):
        if self.can_delete_item():
            self.change_state(CanvasState.DELETING_ITEM)
            return True
        return False
    
    def on_adding_path(self):
        if self.can_add_path():
            self.change_state(CanvasState.ADDING_PATH)
            return True
        return False
    
    def on_idle(self):
        if self.can_idle():
            self.change_state(CanvasState.IDLE)
            return True
        return False

    def change_state(self, new_state: CanvasState):
        if self.state != new_state:
            self.state = new_state
            self.state_changed.emit(self.state)
            print(f"State changed to: {self.state.name}")
        else:
            print(f"State remains: {self.state.name}")
    
    def current_state(self):
        if self.state == CanvasState.IDLE:
            return 'IDLE'
        elif self.state == CanvasState.ADDING_BLOCK:
            return 'ADDING_BLOCK'
        elif self.state == CanvasState.ADDING_PATH:
            return 'ADDING_PATH'
        elif self.state == CanvasState.MOVING_ITEM:
            return 'MOVING_ITEM'
        elif self.state == CanvasState.DELETING_ITEM:
            return 'DELETING_ITEM'

class AppStates(Enum):
    MAIN_WINDOW = auto()
    SETTINGS_DIALOG = auto()
    HELP_DIALOG = auto()
    ELEMENTS_DIALOG = auto()
    COMPILING = auto()

class AppStateMachine(QObject):

    state_changed = pyqtSignal(AppStates)
    window_opened = pyqtSignal(str)
    window_closed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.state = AppStates.MAIN_WINDOW
        self.open_windows = set()
    
    def can_open_window(self, window_name: str):
        return window_name not in self.open_windows and CanvasState.IDLE
    
    def can_close_window(self, window_name: str):
        return window_name in self.open_windows

    def can_compile(self):
        return self.state != AppStates.COMPILING
    
    def on_main_window(self):
        if self.can_go_to_main_window():
            self.change_state(AppStates.MAIN_WINDOW)
            return True
        return False
    
    def on_settings_dialog_open(self):
        if self.can_open_window('Settings'):
            self.open_windows.add('Settings')
            self.window_opened.emit('Settings')
            self.change_state(AppStates.SETTINGS_DIALOG)
            return True
        return False
    
    def on_settings_dialog_close(self):
        if self.can_close_window('Settings'):
            self.open_windows.discard('Settings')
            self.window_closed.emit('Settings')
            self.change_state(AppStates.MAIN_WINDOW)
            return True
        return False

    def on_help_dialog_open(self):
        if self.can_open_window('Help'):
            self.open_windows.add('Help')
            self.window_opened.emit('Help')
            self.change_state(AppStates.HELP_DIALOG)
            return True
        return False
    
    def on_help_dialog_close(self):
        if self.can_close_window('Help'):
            self.open_windows.discard('Help')
            self.window_closed.emit('Help')
            self.change_state(AppStates.MAIN_WINDOW)
            return True
        return False

    def on_elements_dialog_open(self):
        if self.can_open_window('Elements'):
            self.open_windows.add('Elements')
            self.window_opened.emit('Elements')
            self.change_state(AppStates.ELEMENTS_DIALOG)
            return True
        return False
    
    def on_elements_dialog_close(self):
        if self.can_close_window('Elements'):
            self.open_windows.discard('Elements')
            self.window_closed.emit('Elements')
            self.change_state(AppStates.MAIN_WINDOW)
            return True
        return False

    def on_compiling_start(self):
        if self.can_compile():
            self.change_state(AppStates.COMPILING)
            return True
        return False

    def on_compiling_finish(self):
        if self.state == AppStates.COMPILING:
            self.change_state(AppStates.MAIN_WINDOW)
            return True
        return False

    def change_state(self, new_state: AppStates):
        if self.state != new_state:
            self.state = new_state
            self.state_changed.emit(self.state)
            print(f"App state changed to: {self.state.name}")
        else:
            print(f"App state remains: {self.state.name}")