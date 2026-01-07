"""
Simple Enum + Manual Implementation
Best for: Learning, small GUIs, simple workflows
"""

from enum import Enum, auto


class OrderState(Enum):
    """Define all possible states"""
    PENDING = auto()      # Waiting for action
    PROCESSING = auto()   # Being processed
    COMPLETED = auto()    # Finished successfully
    FAILED = auto()       # Error occurred


class OrderMachine:
    """Simple state machine for order processing"""
    
    def __init__(self):
        self.state = OrderState.PENDING
        self.order_value = 0
        self.error_message = None
    
    # Guard conditions (verify if transition is allowed)
    def can_process(self) -> bool:
        """Can only process from PENDING state"""
        return self.state == OrderState.PENDING
    
    def can_complete(self) -> bool:
        """Can only complete from PROCESSING state and with value > 0"""
        return self.state == OrderState.PROCESSING and self.order_value > 0
    
    def can_fail(self) -> bool:
        """Can fail from PENDING or PROCESSING state"""
        return self.state in (OrderState.PENDING, OrderState.PROCESSING)
    
    def can_reset(self) -> bool:
        """Can reset from any non-pending state"""
        return self.state != OrderState.PENDING
    
    # Entry/Exit handlers
    def on_enter_processing(self):
        """Called when entering PROCESSING state"""
        print(f"[ENTERING PROCESSING] Initializing processing workflow")
        # Initialize timers, logs, resources, etc.
    
    def on_exit_processing(self):
        """Called when leaving PROCESSING state"""
        print(f"[EXITING PROCESSING] Cleaning up resources")
    
    def on_enter_completed(self):
        """Called when entering COMPLETED state"""
        print(f"[ENTERING COMPLETED] Order completed with value: {self.order_value}")
    
    def on_enter_failed(self):
        """Called when entering FAILED state"""
        print(f"[ENTERING FAILED] Error: {self.error_message}")
    
    # State transitions
    def process(self):
        """Transition: PENDING -> PROCESSING"""
        if not self.can_process():
            raise RuntimeError(f"Cannot process from {self.state}")
        
        self.on_exit_processing()
        self.state = OrderState.PROCESSING
        self.on_enter_processing()
    
    def complete(self):
        """Transition: PROCESSING -> COMPLETED"""
        if not self.can_complete():
            raise RuntimeError(f"Cannot complete from {self.state}. Order value: {self.order_value}")
        
        self.on_exit_processing()
        self.state = OrderState.COMPLETED
        self.on_enter_completed()
    
    def fail(self, error_msg: str):
        """Transition: Any -> FAILED"""
        if not self.can_fail():
            raise RuntimeError(f"Cannot fail from {self.state}")
        
        self.error_message = error_msg
        self.state = OrderState.FAILED
        self.on_enter_failed()
    
    def reset(self):
        """Transition: Any -> PENDING"""
        if not self.can_reset():
            raise RuntimeError(f"Cannot reset from {self.state}")
        
        self.state = OrderState.PENDING
        self.order_value = 0
        self.error_message = None
        print("[RESET] Machine returned to PENDING state")
    
    # Current state query
    @property
    def is_pending(self) -> bool:
        return self.state == OrderState.PENDING
    
    @property
    def is_processing(self) -> bool:
        return self.state == OrderState.PROCESSING
    
    @property
    def is_completed(self) -> bool:
        return self.state == OrderState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        return self.state == OrderState.FAILED


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=== Simple State Machine Example ===\n")
    
    order = OrderMachine()
    print(f"Initial state: {order.state}")
    
    # Valid transition
    print("\n1. Processing order...")
    order.process()
    print(f"Current state: {order.state}")
    
    # Set order value
    order.order_value = 100
    
    # Valid completion
    print("\n2. Completing order...")
    order.complete()
    print(f"Current state: {order.state}")
    
    # Reset for next cycle
    print("\n3. Resetting...")
    order.reset()
    print(f"Current state: {order.state}")
    
    # Try invalid transition (will raise error)
    print("\n4. Attempting invalid transition (no value)...")
    try:
        order.process()
        order.complete()  # Should fail - no order_value
    except RuntimeError as e:
        print(f"❌ Error caught: {e}")
    
    print("\n✓ State machine prevented invalid transition!")
