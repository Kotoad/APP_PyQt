"""
State Machine Testing Patterns & Comparisons

Best practices for testing state machines and choosing between implementations.
"""

import unittest
from enum import Enum, auto
from example_1_simple import OrderMachine, OrderState


# ============================================================================
# TESTING STATE MACHINES - Best Practices
# ============================================================================

class TestOrderMachine(unittest.TestCase):
    """Comprehensive test suite for state machine"""
    
    def setUp(self):
        """Initialize fresh machine for each test"""
        self.machine = OrderMachine()
    
    # Test 1: Initial State
    def test_initial_state_is_pending(self):
        """Verify initial state"""
        self.assertEqual(self.machine.state, OrderState.PENDING)
        self.assertTrue(self.machine.is_pending)
        self.assertFalse(self.machine.is_processing)
    
    # Test 2: Valid Transitions
    def test_valid_transition_pending_to_processing(self):
        """Test valid state transition"""
        self.machine.process()
        self.assertEqual(self.machine.state, OrderState.PROCESSING)
        self.assertTrue(self.machine.is_processing)
    
    def test_valid_transition_processing_to_completed(self):
        """Test complete workflow"""
        self.machine.order_value = 100
        self.machine.process()
        self.machine.complete()
        
        self.assertEqual(self.machine.state, OrderState.COMPLETED)
        self.assertTrue(self.machine.is_completed)
    
    # Test 3: Invalid Transitions (Guards)
    def test_cannot_complete_without_value(self):
        """Verify guard prevents invalid transition"""
        self.machine.process()
        # order_value is 0
        
        with self.assertRaises(RuntimeError):
            self.machine.complete()
    
    def test_cannot_process_from_processing(self):
        """Cannot double-process"""
        self.machine.process()
        
        with self.assertRaises(RuntimeError):
            self.machine.process()
    
    # Test 4: Multiple Transitions
    def test_complex_workflow(self):
        """Test complete multi-state workflow"""
        # Start
        self.assertEqual(self.machine.state, OrderState.PENDING)
        
        # Process
        self.machine.process()
        self.assertEqual(self.machine.state, OrderState.PROCESSING)
        
        # Set value
        self.machine.order_value = 150
        
        # Complete
        self.machine.complete()
        self.assertEqual(self.machine.state, OrderState.COMPLETED)
        
        # Reset
        self.machine.reset()
        self.assertEqual(self.machine.state, OrderState.PENDING)
        self.assertEqual(self.machine.order_value, 0)
    
    # Test 5: Error Handling
    def test_fail_transition(self):
        """Test error state transitions"""
        self.machine.process()
        self.machine.fail("Network error")
        
        self.assertEqual(self.machine.state, OrderState.FAILED)
        self.assertEqual(self.machine.error_message, "Network error")
    
    def test_error_recovery(self):
        """Test recovery from error state"""
        self.machine.process()
        self.machine.fail("Connection timeout")
        
        # Reset and retry
        self.machine.reset()
        self.assertEqual(self.machine.state, OrderState.PENDING)
        
        # Proceed again
        self.machine.order_value = 200
        self.machine.process()
        self.machine.complete()
        
        self.assertTrue(self.machine.is_completed)


# ============================================================================
# COMPARISON: Which Implementation to Use?
# ============================================================================

"""
IMPLEMENTATION COMPARISON:

┌─────────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ Aspect          │ Enum+Manual  │ Class-Based  │ Library      │ For GUIs     │
├─────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ Learning Curve  │ Easy ⭐⭐     │ Moderate     │ Moderate     │ Easy-Moderate│
│                 │              │ ⭐⭐⭐       │ ⭐⭐⭐      │ ⭐⭐⭐      │
│ Boilerplate     │ More ⭐⭐     │ More ⭐⭐    │ Less ⭐⭐⭐  │ Minimal      │
│ Flexibility     │ High ⭐⭐⭐   │ Very High    │ Very High    │ Very High    │
│                 │              │ ⭐⭐⭐⭐    │ ⭐⭐⭐⭐   │ ⭐⭐⭐⭐   │
│ Testability     │ Good ⭐⭐⭐   │ Good ⭐⭐⭐  │ Excellent    │ Excellent    │
│                 │              │              │ ⭐⭐⭐⭐    │ ⭐⭐⭐⭐   │
│ Dependencies    │ None ⭐⭐⭐   │ None ⭐⭐⭐  │ 1 (library)  │ CustomTkinter│
│ Production Use  │ Small        │ Medium       │ Large        │ Professional │
│                 │ Projects     │ Projects     │ Projects     │ Apps        │
└─────────────────┴──────────────┴──────────────┴──────────────┴──────────────┘

WHEN TO USE EACH:

1. ENUM + MANUAL (example_1_simple.py)
   ✓ Simple state machines (3-7 states)
   ✓ Learning state machines
   ✓ No external dependencies wanted
   ✓ Quick prototyping
   ✓ Embedded systems or restricted environments
   
   ✗ Complex per-state behavior
   ✗ Many transitions
   ✗ Need robust guard system
   ✗ Large team (less standardized)

2. CLASS-BASED STATE PATTERN (example_2_class_based.py)
   ✓ Medium complexity (7-20 states)
   ✓ Rich per-state behavior needed
   ✓ GUI applications with state-specific actions
   ✓ Professional applications
   ✓ Easy to extend with new states
   
   ✗ More boilerplate code
   ✗ Larger initial setup time
   ✗ Not as declarative as library approach

3. PYTHON-STATEMACHINE LIBRARY (example_3_statemachine_lib.py)
   ✓ Large/complex state machines (20+ states)
   ✓ Production systems
   ✓ Need guards, conditions, hooks
   ✓ Declarative, readable syntax
   ✓ Active development and support
   ✓ Built-in history and introspection
   
   ✗ One additional dependency
   ✗ Learning library-specific syntax
   ✗ Overkill for very simple machines

4. CUSTOMTKINTER INTEGRATION (example_4_customtkinter_gui.py)
   ✓ GUI applications with complex workflows
   ✓ Form handling and validation
   ✓ Real-world Python GUI applications
   ✓ User interaction workflows
   
   ✗ For non-GUI projects
   ✗ Simple command-line tools

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RECOMMENDATION FOR YOUR USE CASES:

📊 THREE-PHASE TRANSFORMER CALCULATIONS
   → Use: Enum + Manual or Class-Based
   → Why: Electrical calculations have clear states (IDLE, CALCULATING, COMPLETE)
   → Complexity: Low-Medium

🎮 MINECRAFT MOD/GAME LOGIC
   → Use: Class-Based or Library
   → Why: Many states (IDLE, WALKING, JUMPING, ATTACKING, DEAD, RESPAWNING)
   → Complexity: Medium-High

📝 CUSTOMTKINTER GUI APPLICATION
   → Use: Library + CustomTkinter Integration
   → Why: Complex user workflows need robust state management
   → Complexity: High
   → Real example: Form validation, page navigation, async operations

📚 CLASSICAL LITERATURE ANALYSIS TOOL
   → Use: Enum + Manual or Class-Based
   → Why: Document processing has clear states (LOADING, PARSING, ANALYZING, COMPLETE)
   → Complexity: Low-Medium

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# ============================================================================
# TESTING PATTERNS - What to Test
# ============================================================================

class StateTransitionTestPattern:
    """
    Template for testing state machines.
    Follow this pattern for comprehensive test coverage.
    """
    
    def test_initial_state(self):
        """Every test file should verify initial state"""
        pass
    
    def test_valid_transitions(self):
        """Test all valid state transitions"""
        pass
    
    def test_invalid_transitions(self):
        """Test that invalid transitions raise errors or are prevented"""
        pass
    
    def test_guards(self):
        """Test guard conditions prevent invalid transitions"""
        pass
    
    def test_entry_exit_hooks(self):
        """Verify entry/exit handlers are called correctly"""
        pass
    
    def test_state_properties(self):
        """Test state query properties (is_active, etc.)"""
        pass
    
    def test_data_persistence(self):
        """Verify data is preserved across transitions"""
        pass
    
    def test_error_recovery(self):
        """Test recovery from error states"""
        pass
    
    def test_complex_workflows(self):
        """Test multi-state workflows"""
        pass


# ============================================================================
# COMMON PITFALLS - Checklist
# ============================================================================

"""
COMMON MISTAKES TO AVOID:

❌ 1. Not Testing Edge Cases
   What to do instead:
   - Test transitions from every state
   - Test with invalid data
   - Test error recovery paths
   
❌ 2. Putting Business Logic in State Handlers
   What to do instead:
   - Keep state handlers focused on state changes
   - Put business logic in separate methods
   - Call business logic FROM state handlers
   
   Bad:  def on_enter_processing(self):
             # 50 lines of calculation
   Good: def on_enter_processing(self):
             self.calculate_and_validate()

❌ 3. Mixing State Machine with UI Updates
   What to do instead:
   - Use callbacks for UI updates
   - Keep state machine independent from GUI
   - Let GUI observe state changes
   
   Bad:  def transition(self):
             self.update_button_color()
             self.state = NEW_STATE
             self.refresh_window()
   
   Good: sm.on_state_change.subscribe(gui.update_ui)

❌ 4. Not Documenting State Diagram
   What to do instead:
   - Create a state transition table or diagram
   - Document what triggers each transition
   - Include guard conditions in documentation
   
❌ 5. Ignoring Error States
   What to do instead:
   - Include ERROR state in every machine
   - Plan recovery paths
   - Log errors with context
   
❌ 6. Creating Too Many States
   What to do instead:
   - Group related states
   - Use sub-states or state attributes
   - Keep state count < 20 if possible

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BEST PRACTICES CHECKLIST:

✓ Define all states upfront
✓ List all valid transitions
✓ Identify guard conditions
✓ Plan entry/exit behavior
✓ Handle error cases
✓ Document state diagram
✓ Write tests for each state
✓ Test invalid transitions
✓ Keep states simple
✓ Separate state logic from business logic
✓ Use enums, not strings
✓ Implement proper error recovery
✓ Version control state definitions
✓ Log state transitions (especially in production)
✓ Consider performance for frequent transitions
"""


if __name__ == "__main__":
    # Run tests
    print("Running State Machine Tests...\n")
    unittest.main(verbosity=2)
