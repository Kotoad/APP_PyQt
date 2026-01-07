# State Machine Implementation Guide

## What You Need to Know

### Fundamentals

A **state machine** is a behavioral design pattern that manages an object or system with a **finite number of well-defined states** and **controlled transitions** between them.

**Key Elements:**

1. **States** - Predefined conditions where your system can exist (e.g., IDLE, ACTIVE, ERROR)
2. **Events** - Triggers that cause state transitions (e.g., START, STOP, RESET)
3. **Transitions** - Rules defining which states can move to which other states
4. **Guards** - Conditions that must be met before a transition occurs
5. **Actions** - Behavior executed when entering/exiting states or during transitions

**Why State Machines Matter:**

- **Clarity** - Makes complex behavior explicit and easy to understand
- **Safety** - Guards prevent invalid state combinations
- **Maintainability** - Easier to add new states or modify transitions
- **Testing** - Each state can be tested independently
- **Reduced Conditionals** - Replaces complex if-else chains

---

## What to Avoid

### ❌ 1. **Overcomplicating State Definitions**

**Problem:** Creating too many states leads to confusion and hard-to-follow transitions.

```python
# BAD - Too many granular states
class States(Enum):
    WAITING_PAYMENT = 1
    PAYMENT_APPROVED = 2
    ORDER_PROCESSING = 3
    ITEMS_PICKED = 4
    ITEMS_PACKED = 5
    AWAITING_SHIPMENT = 6
    SHIPPED = 7
    IN_DELIVERY = 8
    DELIVERED = 9
```

**Solution:** Group similar states into major categories.

```python
# GOOD - Simplified, meaningful states
class States(Enum):
    PENDING = 1      # Waiting for action
    ACTIVE = 2       # Being processed
    COMPLETED = 3    # Finished
    FAILED = 4       # Error state
```

### ❌ 2. **Ignoring Transition Logic**

**Problem:** Mixing state logic with application logic makes it impossible to track valid transitions.

```python
# BAD - State logic scattered everywhere
if user.status == "active":
    user.process()
    user.status = "processing"
    # ... more state changes buried in business logic
```

**Solution:** Centralize transition logic in the state machine itself.

```python
# GOOD - Clear, centralized transitions
class UserMachine(StateMachine):
    start = State('Start', initial=True)
    processing = State('Processing')
    complete = State('Complete', final=True)
    
    activate = start.to(processing)
    finish = processing.to(complete)
```

### ❌ 3. **Failing to Implement Guards**

**Problem:** Allowing invalid transitions corrupts your system state.

```python
# BAD - No validation
def transition_to_complete(self):
    self.state = State.COMPLETED  # Could happen from any state!
```

**Solution:** Add guard clauses to enforce valid transitions.

```python
# GOOD - Guards enforce rules
if self.state == State.ACTIVE:
    self.state = State.COMPLETED
else:
    raise InvalidTransitionError(f"Cannot complete from {self.state}")
```

Or using python-statemachine library:

```python
finish = processing.to(complete, cond='items_count > 0')
```

### ❌ 4. **Neglecting Entry/Exit Behavior**

**Problem:** States need setup and cleanup actions, but these are often forgotten.

```python
# BAD - No initialization when entering state
self.state = State.ACTIVE
# What about initializing timers, logging, or resources?
```

**Solution:** Implement state entry and exit hooks.

```python
# GOOD - Clear entry/exit handlers
def on_enter_active(self):
    self.start_timer()
    self.logger.info("Entered ACTIVE state")
    self.init_resources()

def on_exit_active(self):
    self.stop_timer()
    self.cleanup_resources()
```

### ❌ 5. **Not Documenting State Behavior**

**Problem:** Without documentation, new developers (or future you) can't understand the flow.

**Solution:** Document with state diagrams or state tables.

```
STATE TRANSITION TABLE
┌─────────────┬──────────────┬──────────────┬──────────────┐
│ Current     │ Event        │ Next         │ Condition    │
├─────────────┼──────────────┼──────────────┼──────────────┤
│ IDLE        │ start        │ RUNNING      │ -            │
│ RUNNING     │ pause        │ PAUSED       │ -            │
│ RUNNING     │ error        │ ERROR        │ -            │
│ PAUSED      │ resume       │ RUNNING      │ -            │
│ ERROR       │ reset        │ IDLE         │ -            │
└─────────────┴──────────────┴──────────────┴──────────────┘
```

### ❌ 6. **Using Raw Strings/Magic Numbers**

**Problem:** Hard to catch typos, inconsistent state references.

```python
# BAD - String-based states
if current_state == "actvie":  # Typo! Hard to catch
    pass
```

**Solution:** Use Python Enums for type safety.

```python
# GOOD - Enum-based states
from enum import Enum, auto

class States(Enum):
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    
# Now typos are caught at runtime
if current_state == States.RUNNING:
    pass
```

### ❌ 7. **Creating Monolithic State Handlers**

**Problem:** Putting all state logic in one massive method.

```python
# BAD - Everything in one handler
def handle_event(self, event):
    if self.state == State.IDLE:
        if event == 'start':
            # 50 lines of code
        elif event == 'shutdown':
            # 30 lines of code
    elif self.state == State.RUNNING:
        # ... more massive nesting
```

**Solution:** Use separate classes or methods for each state.

```python
# GOOD - Separate, testable handlers
def on_enter_idle(self):
    self.reset_resources()
    
def handle_start_from_idle(self):
    self.initialize_system()
    
def on_enter_running(self):
    self.start_processing()
```

### ❌ 8. **Not Testing State Transitions**

**Problem:** Complex state machines without tests cause silent bugs.

**Solution:** Test every state and transition.

```python
def test_transition_idle_to_running(self):
    sm = StateMachine()
    sm.start()
    assert sm.is_running
    
def test_invalid_transition_raises(self):
    sm = StateMachine()
    with pytest.raises(InvalidTransitionError):
        sm.pause()  # Can't pause from IDLE
```

---

## Best Practices Summary

| Practice | Benefit |
|----------|---------|
| Use **Enums** for states and events | Type safety, prevents typos |
| **Keep states simple** | Easier to understand, fewer transitions |
| **Centralize transitions** | One place to understand flow |
| **Implement guards** | Prevents invalid states |
| **Use entry/exit hooks** | Proper initialization and cleanup |
| **Document transitions** | Team clarity, future maintenance |
| **Separate state classes** | Better organization, easier testing |
| **Test thoroughly** | Catch edge cases early |
| **Use libraries** (python-statemachine) | Reduces boilerplate |

---

## Implementation Approaches

### 1. **Enum + Manual (Simplest)**
Best for: Simple machines with few states
- Lightweight, no dependencies
- Easy to understand
- Limited features

### 2. **Class-Based State Pattern (Most Flexible)**
Best for: Complex behavior per state
- Each state is a class
- Can inherit common behavior
- Excellent for GUI apps

### 3. **python-statemachine Library (Most Pythonic)**
Best for: Production systems
- Declarative syntax
- Built-in guards and hooks
- Active development
