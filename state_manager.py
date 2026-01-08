from Imports import get_State_Machine

AppStateMachine, CanvasStateMachine = get_State_Machine()

class StateManager:
    """Central state management for entire application"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            print("Creating StateManager instance")
            cls._instance = super().__new__(cls)
        print("Returning StateManager instance")
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            print("Initializing StateManager")
            self.canvas_state = CanvasStateMachine()
            self.app_state = AppStateMachine()
            self.initialized = True
    
    @classmethod
    def get_instance(cls):
        print("Getting StateManager instance")
        return cls()