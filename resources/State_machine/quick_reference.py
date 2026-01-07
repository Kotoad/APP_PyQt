"""
STATE MACHINE QUICK REFERENCE GUIDE

A practical guide for implementing state machines in your projects.
"""

# ============================================================================
# QUICK START DECISION TREE
# ============================================================================

"""
Start here to choose the right approach for your project:

                    Need a State Machine?
                            ↓
                ┌───────────────────────────┐
                │                           │
          Simple?         Medium?         Complex?
       (3-5 states)    (5-15 states)    (15+ states)
             ↓               ↓               ↓
        Enum+Manual    Class-Based      Library
        
Quick Indicators:
- Simple: Calculator, Timer, LED control, Simple GUI
- Medium: Form workflows, Game logic, Motor control, Document editor
- Complex: Workflow engines, Complex GUIs, Distributed systems, ERP systems

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# ============================================================================
# IMPLEMENTATION SNIPPETS - Copy & Paste Ready
# ============================================================================

# SNIPPET 1: Minimal Enum-Based State Machine
from enum import Enum, auto

class State(Enum):
    IDLE = auto()
    ACTIVE = auto()
    DONE = auto()

class SimpleMachine:
    def __init__(self):
        self.state = State.IDLE
    
    def start(self):
        if self.state == State.IDLE:
            self.state = State.ACTIVE
    
    def finish(self):
        if self.state == State.ACTIVE:
            self.state = State.DONE
    
    @property
    def is_active(self):
        return self.state == State.ACTIVE


# SNIPPET 2: Class-Based Pattern Base
from abc import ABC, abstractmethod

class StateHandler(ABC):
    def __init__(self, machine):
        self.machine = machine
    
    @abstractmethod
    def enter(self): pass
    
    @abstractmethod
    def exit(self): pass
    
    @abstractmethod
    def handle(self, event): pass

class MyMachine:
    def __init__(self):
        self.state = None
        self.states = {}
    
    def transition(self, new_state):
        if self.state:
            self.state.exit()
        self.state = new_state
        self.state.enter()


# SNIPPET 3: Guard Function Pattern
def can_transition(from_state, to_state, data=None):
    """Check if transition is valid"""
    # Define rules
    rules = {
        ('IDLE', 'RUNNING'): lambda d: True,
        ('RUNNING', 'PAUSED'): lambda d: True,
        ('PAUSED', 'RUNNING'): lambda d: True,
        ('RUNNING', 'IDLE'): lambda d: d.get('health', 0) > 0,
    }
    
    key = (from_state, to_state)
    if key in rules:
        return rules[key](data or {})
    return False


# SNIPPET 4: Entry/Exit Handler Pattern
class MachineWithHooks:
    def __init__(self):
        self.state = 'IDLE'
        self.handlers = {
            'on_enter_RUNNING': self._on_enter_running,
            'on_exit_RUNNING': self._on_exit_running,
        }
    
    def transition_to(self, new_state):
        # Call exit handler
        handler = self.handlers.get(f'on_exit_{self.state}')
        if handler:
            handler()
        
        # Change state
        self.state = new_state
        
        # Call enter handler
        handler = self.handlers.get(f'on_enter_{self.state}')
        if handler:
            handler()
    
    def _on_enter_running(self):
        print("Starting resources...")
    
    def _on_exit_running(self):
        print("Cleaning up...")


# ============================================================================
# STATE MACHINE PATTERNS FOR SPECIFIC USE CASES
# ============================================================================

# PATTERN 1: Simple UI/Form Workflow
"""
States: EMPTY → FILLING → VALIDATING → SUBMITTED → DONE
Guards: Only submit if form not empty
Actions: Save data, show validation messages
"""

class FormMachine:
    class State(Enum):
        EMPTY = auto()
        FILLING = auto()
        VALIDATING = auto()
        SUBMITTED = auto()
        DONE = auto()
    
    def __init__(self):
        self.state = self.State.EMPTY
        self.data = {}
    
    def fill_form(self, data):
        if self.state == self.State.EMPTY:
            self.data = data
            self.state = self.State.FILLING
    
    def validate(self):
        if self.state == self.State.FILLING and self._is_valid():
            self.state = self.State.VALIDATING
    
    def submit(self):
        if self.state == self.State.VALIDATING:
            self.state = self.State.SUBMITTED
    
    def _is_valid(self):
        return len(self.data) > 0


# PATTERN 2: Device Control (LED, Motor, etc)
"""
States: OFF → STARTING → ON → STOPPING → OFF
Guards: Can't stop if not on
Actions: Initialize/cleanup hardware
"""

class DeviceController:
    class State(Enum):
        OFF = auto()
        STARTING = auto()
        ON = auto()
        STOPPING = auto()
    
    def __init__(self):
        self.state = self.State.OFF
    
    def turn_on(self):
        if self.state == self.State.OFF:
            self.state = self.State.STARTING
            self._init_hardware()
            self.state = self.State.ON
    
    def turn_off(self):
        if self.state == self.State.ON:
            self.state = self.State.STOPPING
            self._cleanup_hardware()
            self.state = self.State.OFF
    
    def _init_hardware(self):
        # Real initialization code
        pass
    
    def _cleanup_hardware(self):
        # Real cleanup code
        pass


# PATTERN 3: Processing Pipeline (Data Processing)
"""
States: PENDING → PROCESSING → SUCCESS / FAILED
Guards: Only process pending items
Actions: Log progress, update UI
"""

class ProcessingMachine:
    class State(Enum):
        PENDING = auto()
        PROCESSING = auto()
        SUCCESS = auto()
        FAILED = auto()
    
    def __init__(self, data):
        self.state = self.State.PENDING
        self.data = data
        self.result = None
        self.error = None
    
    def process(self):
        if self.state != self.State.PENDING:
            raise RuntimeError("Cannot process non-pending item")
        
        self.state = self.State.PROCESSING
        try:
            self.result = self._do_processing()
            self.state = self.State.SUCCESS
        except Exception as e:
            self.error = str(e)
            self.state = self.State.FAILED
    
    def _do_processing(self):
        # Actual processing logic
        return f"Processed: {self.data}"
    
    def retry(self):
        if self.state == self.State.FAILED:
            self.state = self.State.PENDING
            self.error = None


# PATTERN 4: Game Entity (Player, NPC, etc)
"""
States: IDLE → MOVING → ATTACKING → DEAD
Guards: Can't attack if too far
Actions: Animation, particle effects
"""

class GameEntity:
    class State(Enum):
        IDLE = auto()
        MOVING = auto()
        ATTACKING = auto()
        DEAD = auto()
    
    def __init__(self, x=0, y=0):
        self.state = self.State.IDLE
        self.x = x
        self.y = y
        self.health = 100
    
    def move_to(self, target_x, target_y):
        if self.state in (self.State.IDLE, self.State.ATTACKING):
            self.state = self.State.MOVING
            self._animate_movement(target_x, target_y)
            self.state = self.State.IDLE
    
    def attack(self, target):
        if self._can_attack(target):
            self.state = self.State.ATTACKING
            self._deal_damage(target)
            self.state = self.State.IDLE
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.state = self.State.DEAD
    
    def _can_attack(self, target):
        distance = abs(self.x - target.x) + abs(self.y - target.y)
        return self.state == self.State.IDLE and distance < 50
    
    def _animate_movement(self, tx, ty):
        # Animation code
        self.x = tx
        self.y = ty
    
    def _deal_damage(self, target):
        target.take_damage(10)


# ============================================================================
# KEY CONCEPTS TO REMEMBER
# ============================================================================

"""
CONCEPT 1: State is Exclusive
- Only ONE state active at a time
- No being in two states simultaneously
- If you need multiple independent states, use multiple machines

CONCEPT 2: Transitions are Explicit
- Define exactly which states lead where
- Use guards to validate transitions
- Prevent invalid state combinations

CONCEPT 3: States Encapsulate Behavior
- Each state can have different behavior for same event
- Use entry/exit handlers for setup/cleanup
- Keep state logic centralized

CONCEPT 4: Guards Prevent Errors
- Check conditions before transitions
- Raise errors for invalid transitions
- Use guard clauses liberally

CONCEPT 5: Testing is Critical
- Test every state
- Test every transition
- Test invalid transitions
- Test guard conditions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# ============================================================================
# ANTI-PATTERNS - What NOT to Do
# ============================================================================

"""
❌ ANTI-PATTERN 1: String-Based States
Bad:  if self.state == "running":
Good: if self.state == State.RUNNING:

❌ ANTI-PATTERN 2: State Machine in UI
Bad:  Button → state = PROCESSING → update_button
Good: Button → state_machine.process() → machine calls UI.update()

❌ ANTI-PATTERN 3: Too Many States
Bad:  10+ states with unclear purpose
Good: Group states, use 5-8 clear states

❌ ANTI-PATTERN 4: No Error State
Bad:  Only happy path states
Good: Include ERROR state, plan recovery

❌ ANTI-PATTERN 5: Business Logic in Handlers
Bad:  def on_enter_processing(self):
           # 100 lines of calculation
Good: def on_enter_processing(self):
           self.process()  # Call method that does work

❌ ANTI-PATTERN 6: Forgetting Entry/Exit
Bad:  state = NEW
Good: on_exit_old(); state = NEW; on_enter_new()

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# ============================================================================
# FILES PROVIDED IN THIS SET
# ============================================================================

"""
📁 State Machine Learning Package
├── state_machine_guide.md
│   └─ Comprehensive guide covering fundamentals, what to avoid,
│      and best practices
│
├── example_1_simple.py
│   └─ Enum + Manual approach
│      Best for: Learning, simple projects
│      States: 4 (PENDING, PROCESSING, COMPLETED, FAILED)
│      Use case: Order processing workflow
│
├── example_2_class_based.py
│   └─ Class-based State Pattern
│      Best for: GUI applications, complex behavior
│      States: 6 (IDLE, EDITING, VALIDATING, SAVING, ERROR, SUCCESS)
│      Use case: Form validation workflow
│
├── example_3_statemachine_lib.py
│   └─ python-statemachine library (production-ready)
│      Best for: Large projects, declarative syntax
│      Examples: Document lifecycle, Motor control
│      Install: pip install python-statemachine
│
├── example_4_customtkinter_gui.py
│   └─ Integration with CustomTkinter GUI
│      Best for: Real GUI applications
│      States: Form submission workflow with UI
│      Install: pip install customtkinter python-statemachine
│
├── testing_and_comparison.py
│   └─ Testing patterns and implementation comparison
│      Contains: Test examples, checklist, anti-patterns
│
└── quick_reference.py (this file)
    └─ Copy-paste snippets and quick decision guide

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# ============================================================================
# YOUR NEXT STEPS
# ============================================================================

"""
1. UNDERSTAND THE BASICS
   → Read: state_machine_guide.md
   → Run: example_1_simple.py

2. CHOOSE YOUR APPROACH
   - Simple project? → Use example_1_simple.py as template
   - Complex GUI? → Use example_4_customtkinter_gui.py as template
   - Medium project? → Use example_2_class_based.py as template

3. IMPLEMENT
   → Copy the template for your approach
   → Replace states with your specific states
   → Define your transitions
   → Add guards for invalid transitions
   → Implement entry/exit handlers

4. TEST
   → Write tests following pattern in testing_and_comparison.py
   → Test valid transitions
   → Test invalid transitions
   → Test error recovery

5. INTEGRATE
   → Connect with your GUI (if applicable)
   → Add logging for debugging
   → Monitor state transitions in production

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUESTIONS YOU MIGHT HAVE:

Q: Can a state machine call another state machine?
A: Yes! Hierarchical state machines are useful for complex systems.
   The inner machine becomes the action of the outer machine.

Q: How do I handle async operations?
A: Make transitions trigger async operations, use callbacks when done.
   Or use threading/asyncio with state as outcome tracker.

Q: How do I persist state?
A: Save state enum value or ID to database/file.
   Restore on load and continue from saved state.

Q: How do I debug state machines?
A: Log every state transition with timestamp and data.
   Implement state_changed() callback for monitoring.

Q: Can states have attributes?
A: Yes! Each state instance can have data. Use machine attributes
   or state-specific attributes depending on design.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESOURCES FOR DEEPER LEARNING:

- python-statemachine docs: https://python-statemachine.readthedocs.io/
- State Pattern (Design Patterns): https://refactoring.guru/design-patterns/state
- Finite State Machines in Game Dev: Various game dev resources
- UML State Machine Diagrams: For complex visualization

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
