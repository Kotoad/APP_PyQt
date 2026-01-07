"""
Class-Based State Pattern Implementation
Best for: GUI applications, complex per-state behavior, Python GUI development
This is ideal for CustomTkinter applications with complex state logic
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, Optional


class StateID(Enum):
    """State identifiers"""
    IDLE = auto()
    EDITING = auto()
    VALIDATING = auto()
    SAVING = auto()
    ERROR = auto()
    SUCCESS = auto()


class State(ABC):
    """Abstract base class for all states"""
    
    def __init__(self, machine: 'FormStateMachine'):
        self.machine = machine
    
    @abstractmethod
    def enter(self):
        """Called when entering this state"""
        pass
    
    @abstractmethod
    def exit(self):
        """Called when leaving this state"""
        pass
    
    @abstractmethod
    def handle_event(self, event: str, data: Optional[dict] = None) -> bool:
        """
        Handle an event in this state
        Returns True if transition occurred, False if invalid transition
        """
        pass


class IdleState(State):
    """Initial state - waiting for user input"""
    
    def enter(self):
        print("[IDLE] Waiting for user input")
        self.machine.ui_callback("Waiting for input...", "info")
    
    def exit(self):
        print("[IDLE] Exiting idle state")
    
    def handle_event(self, event: str, data: Optional[dict] = None) -> bool:
        if event == "start_edit":
            self.machine.transition_to(StateID.EDITING)
            return True
        return False


class EditingState(State):
    """User is editing form - collect data"""
    
    def enter(self):
        print("[EDITING] Form editing started")
        self.machine.ui_callback("Editing form...", "info")
        self.machine.form_data = {}
    
    def exit(self):
        print("[EDITING] Exiting editing state")
    
    def handle_event(self, event: str, data: Optional[dict] = None) -> bool:
        if event == "submit":
            # Save form data before transitioning
            self.machine.form_data = data or {}
            self.machine.transition_to(StateID.VALIDATING)
            return True
        elif event == "cancel":
            self.machine.form_data = {}
            self.machine.transition_to(StateID.IDLE)
            return True
        return False


class ValidatingState(State):
    """Validate collected data"""
    
    def enter(self):
        print("[VALIDATING] Starting validation...")
        self.machine.ui_callback("Validating data...", "info")
        
        # Perform validation
        if self.validate_data():
            print("[VALIDATING] ✓ Validation passed")
            self.machine.transition_to(StateID.SAVING)
        else:
            print("[VALIDATING] ✗ Validation failed")
            self.machine.transition_to(StateID.ERROR)
    
    def exit(self):
        print("[VALIDATING] Exiting validation state")
    
    def validate_data(self) -> bool:
        """Custom validation logic"""
        data = self.machine.form_data
        
        # Check required fields
        if not data.get("name"):
            self.machine.error_message = "Name is required"
            return False
        
        if not data.get("email"):
            self.machine.error_message = "Email is required"
            return False
        
        # Check email format
        if "@" not in data.get("email", ""):
            self.machine.error_message = "Invalid email format"
            return False
        
        return True
    
    def handle_event(self, event: str, data: Optional[dict] = None) -> bool:
        # No manual events in this state - auto-transitions on enter()
        return False


class SavingState(State):
    """Persist data to backend"""
    
    def enter(self):
        print("[SAVING] Saving data...")
        self.machine.ui_callback("Saving data...", "info")
        
        # Simulate save operation
        if self.save_data():
            print("[SAVING] ✓ Data saved successfully")
            self.machine.transition_to(StateID.SUCCESS)
        else:
            print("[SAVING] ✗ Save failed")
            self.machine.transition_to(StateID.ERROR)
    
    def exit(self):
        print("[SAVING] Exiting saving state")
    
    def save_data(self) -> bool:
        """Simulate saving to database/API"""
        try:
            # In real app: make API call, save to database, etc.
            data = self.machine.form_data
            print(f"  Saving: {data}")
            return True
        except Exception as e:
            self.machine.error_message = str(e)
            return False
    
    def handle_event(self, event: str, data: Optional[dict] = None) -> bool:
        # No manual events - auto-transitions on enter()
        return False


class ErrorState(State):
    """Error occurred - allow retry or cancel"""
    
    def enter(self):
        print(f"[ERROR] ✗ {self.machine.error_message}")
        self.machine.ui_callback(f"Error: {self.machine.error_message}", "error")
    
    def exit(self):
        print("[ERROR] Exiting error state")
    
    def handle_event(self, event: str, data: Optional[dict] = None) -> bool:
        if event == "retry":
            self.machine.transition_to(StateID.EDITING)
            return True
        elif event == "cancel":
            self.machine.transition_to(StateID.IDLE)
            self.machine.form_data = {}
            return True
        return False


class SuccessState(State):
    """Operation completed successfully"""
    
    def enter(self):
        print("[SUCCESS] ✓ Operation completed!")
        self.machine.ui_callback("Saved successfully!", "success")
    
    def exit(self):
        print("[SUCCESS] Exiting success state")
        self.machine.form_data = {}
    
    def handle_event(self, event: str, data: Optional[dict] = None) -> bool:
        if event == "new_edit":
            self.machine.transition_to(StateID.IDLE)
            return True
        return False


class FormStateMachine:
    """Main state machine coordinating all states"""
    
    def __init__(self, ui_callback=None):
        self.states: Dict[StateID, State] = {
            StateID.IDLE: IdleState(self),
            StateID.EDITING: EditingState(self),
            StateID.VALIDATING: ValidatingState(self),
            StateID.SAVING: SavingState(self),
            StateID.ERROR: ErrorState(self),
            StateID.SUCCESS: SuccessState(self),
        }
        
        self.current_state: State = self.states[StateID.IDLE]
        self.current_state_id = StateID.IDLE
        self.ui_callback = ui_callback or self._default_callback
        
        # Data
        self.form_data: dict = {}
        self.error_message: str = ""
    
    def _default_callback(self, message: str, msg_type: str):
        """Default UI callback (prints to console)"""
        prefix = {"info": "ℹ️", "error": "❌", "success": "✓"}.get(msg_type, "•")
        print(f"  {prefix} UI: {message}")
    
    def transition_to(self, new_state_id: StateID):
        """Transition to a new state"""
        if new_state_id not in self.states:
            raise ValueError(f"Unknown state: {new_state_id}")
        
        # Exit current state
        self.current_state.exit()
        
        # Transition
        self.current_state_id = new_state_id
        self.current_state = self.states[new_state_id]
        
        # Enter new state
        self.current_state.enter()
    
    def send_event(self, event: str, data: Optional[dict] = None) -> bool:
        """Send event to current state"""
        print(f"\n>>> Event: {event}")
        success = self.current_state.handle_event(event, data)
        
        if not success:
            print(f"  ⚠️  Invalid event '{event}' for state {self.current_state_id}")
        
        return success
    
    @property
    def is_idle(self) -> bool:
        return self.current_state_id == StateID.IDLE
    
    @property
    def is_editing(self) -> bool:
        return self.current_state_id == StateID.EDITING
    
    @property
    def is_processing(self) -> bool:
        return self.current_state_id in (StateID.VALIDATING, StateID.SAVING)
    
    @property
    def is_error(self) -> bool:
        return self.current_state_id == StateID.ERROR


# ============================================================================
# EXAMPLE USAGE - Simulating GUI Application
# ============================================================================

if __name__ == "__main__":
    print("=== Class-Based State Machine (GUI Example) ===\n")
    
    def custom_ui_callback(message: str, msg_type: str):
        """Custom UI callback - could update CTkLabel in real GUI"""
        colors = {"info": "🔵", "error": "🔴", "success": "🟢"}
        print(f"  {colors.get(msg_type, '⚪')} UI UPDATE: {message}")
    
    # Create state machine
    sm = FormStateMachine(ui_callback=custom_ui_callback)
    sm.current_state.enter()  # Initialize
    
    # Simulate user workflow
    print("\n--- Scenario 1: Valid form submission ---")
    sm.send_event("start_edit")
    
    form_data = {
        "name": "John Doe",
        "email": "john@example.com",
    }
    sm.send_event("submit", form_data)
    
    # Wait for auto-transitions to complete
    print(f"\nFinal state: {sm.current_state_id}")
    
    # Try another workflow
    print("\n--- Scenario 2: Invalid form (error handling) ---")
    sm.send_event("new_edit")
    
    invalid_data = {
        "name": "Jane",
        # Missing email!
    }
    sm.send_event("submit", invalid_data)
    
    print(f"\nError message: {sm.error_message}")
    print(f"Current state: {sm.current_state_id}")
    
    # Retry after error
    print("\n--- Scenario 3: Retry after error ---")
    corrected_data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
    }
    sm.send_event("retry")
    sm.send_event("submit", corrected_data)
    
    print(f"\nFinal state: {sm.current_state_id}")
    print(f"✓ Workflow complete!")
