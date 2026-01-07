"""
python-statemachine Library Implementation
Best for: Production systems, declarative syntax, powerful features
Install: pip install python-statemachine

This approach is most Pythonic and has the richest feature set.
Great for complex GUI applications requiring robust state management.
"""

from statemachine import StateMachine, State


class DocumentMachine(StateMachine):
    """
    A state machine for document lifecycle management.
    Could be used in a CustomTkinter GUI editor application.
    
    States: draft -> review -> approved -> published
    Plus error recovery paths.
    """
    
    # Define states
    draft = State("Draft", initial=True)
    review = State("In Review")
    approved = State("Approved")
    published = State("Published", final=True)
    rejected = State("Rejected")
    
    # Define transitions (events)
    submit_for_review = draft.to(review) | rejected.to(review)
    approve = review.to(approved)
    reject = review.to(rejected) | approved.to(rejected)
    publish = approved.to(published)
    revert = published.to(approved)
    
    # Machine initialization
    def __init__(self):
        self.content = ""
        self.review_comments = ""
        self.editor_name = "Anonymous"
        super().__init__()
    
    # Entry/Exit handlers
    def on_enter_draft(self):
        """Entering draft state"""
        print("[📝 DRAFT] Document ready for editing")
    
    def on_enter_review(self):
        """Entering review state"""
        print(f"[🔍 REVIEW] Document submitted for review")
        print(f"  Content length: {len(self.content)} chars")
    
    def on_enter_approved(self):
        """Entering approved state"""
        print("[✅ APPROVED] Document has been approved!")
    
    def on_enter_published(self):
        """Entering published state"""
        print("[🚀 PUBLISHED] Document is now live!")
    
    def on_enter_rejected(self):
        """Entering rejected state"""
        print(f"[❌ REJECTED] Document rejected")
        if self.review_comments:
            print(f"  Comments: {self.review_comments}")
    
    # Guards - conditions that must be true for transitions
    def can_submit_for_review(self) -> bool:
        """Only submit if content exists"""
        if not self.content or len(self.content.strip()) < 10:
            print("  ⚠️  Content too short (minimum 10 characters)")
            return False
        return True
    
    def can_approve(self) -> bool:
        """Always allowed"""
        return True
    
    def can_publish(self) -> bool:
        """Only publish if approved and content exists"""
        if not self.content:
            print("  ⚠️  Cannot publish empty document")
            return False
        return True
    
    # Custom transition handlers
    def after_submit_for_review(self):
        """Called after successful submit_for_review transition"""
        print(f"  ✓ Submitted by: {self.editor_name}")
    
    def after_reject(self):
        """Called after reject transition"""
        print("  • Ready to revise and resubmit")
    
    def after_publish(self):
        """Called after publish transition"""
        print("  • Notification sent to subscribers")
    
    # State query properties (auto-generated)
    @property
    def can_edit(self) -> bool:
        """Can edit only in draft or rejected states"""
        return self.current_state in (self.draft, self.rejected)
    
    @property
    def is_published(self) -> bool:
        """Check if document is published"""
        return self.current_state == self.published
    
    def get_allowed_events(self) -> list:
        """Get list of allowed events from current state"""
        return [event.name for event in self.current_state.from_states]


# ============================================================================
# EXAMPLE: Motion/Motor State Machine (Electrical Engineering Context)
# ============================================================================

from enum import Enum


class MotorState(Enum):
    """Motor operation states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class MotorMachine(StateMachine):
    """
    State machine for AC induction motor control.
    Typical in electrical engineering applications.
    """
    
    # States
    stopped = State("Stopped", initial=True)
    starting = State("Starting")
    running = State("Running")
    stopping = State("Stopping")
    error = State("Error")
    
    # Transitions
    start = stopped.to(starting) | error.to(starting)
    run = starting.to(running)
    stop = running.to(stopping)
    idle = stopping.to(stopped)
    fault = running.to(error) | starting.to(error)
    clear_fault = error.to(stopped)
    
    def __init__(self):
        self.speed_rpm = 0
        self.current_amps = 0.0
        self.voltage_volts = 0.0
        self.temperature_celsius = 25.0
        self.fault_code = None
        super().__init__()
    
    # Operational limits (guards)
    def can_run(self) -> bool:
        """Check if motor can run safely"""
        if self.temperature_celsius > 80:
            self.fault_code = "OVERTEMP"
            print(f"  ❌ Temperature too high: {self.temperature_celsius}°C")
            return False
        
        if self.voltage_volts < 200 or self.voltage_volts > 250:
            self.fault_code = "UNDERVOLT"
            print(f"  ❌ Voltage out of range: {self.voltage_volts}V")
            return False
        
        return True
    
    def can_stop(self) -> bool:
        """Always safe to stop"""
        return True
    
    def can_clear_fault(self) -> bool:
        """Allow clearing fault if conditions normalized"""
        if self.temperature_celsius > 60:
            print("  ⚠️  Temperature still elevated, wait before clearing fault")
            return False
        return True
    
    # State handlers
    def on_enter_starting(self):
        """Initialize motor starting sequence"""
        print("[⚡ STARTING] Initiating soft-start sequence...")
        print(f"  Target voltage: {self.voltage_volts:.1f}V")
        print(f"  Ramp time: 2.5 seconds")
    
    def on_enter_running(self):
        """Motor is running"""
        self.speed_rpm = 1450  # Typical 4-pole induction motor
        self.current_amps = 5.2
        print(f"[🔄 RUNNING] Motor operating normally")
        print(f"  Speed: {self.speed_rpm} RPM")
        print(f"  Current: {self.current_amps:.1f}A")
    
    def on_exit_running(self):
        """Stop motor operation"""
        self.speed_rpm = 0
        self.current_amps = 0.0
    
    def on_enter_stopping(self):
        """Graceful motor shutdown"""
        print("[⏹️  STOPPING] Executing controlled stop...")
        print(f"  Deceleration ramp: 1.5 seconds")
    
    def on_enter_error(self):
        """Handle motor fault"""
        self.speed_rpm = 0
        print(f"[🚨 ERROR] Motor fault detected!")
        print(f"  Fault code: {self.fault_code}")
        print(f"  Temperature: {self.temperature_celsius:.1f}°C")
    
    # Monitoring properties
    @property
    def is_running(self) -> bool:
        return self.current_state == self.running
    
    @property
    def is_safe_to_service(self) -> bool:
        """Check if motor is safe for maintenance"""
        return self.current_state == self.stopped and self.temperature_celsius < 40


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("EXAMPLE 1: Document Management State Machine")
    print("=" * 60)
    
    doc = DocumentMachine()
    print(f"\nInitial state: {doc.current_state}")
    
    # Add content
    print("\n1. Writing document...")
    doc.content = "This is an important document that needs review."
    doc.editor_name = "Alice"
    
    # Submit for review
    print("\n2. Submitting for review...")
    if doc.submit_for_review():
        print("✓ Submitted successfully")
    else:
        print("✗ Could not submit")
    
    # Approve
    print("\n3. Approving document...")
    doc.approve()
    
    # Publish
    print("\n4. Publishing...")
    doc.publish()
    print(f"Final state: {doc.current_state}")
    
    # Try to revert from published
    print("\n5. Reverting from published...")
    doc.revert()
    print(f"State after revert: {doc.current_state}")
    
    # Reject from approved
    print("\n6. Rejecting document...")
    doc.review_comments = "Needs more technical details"
    doc.reject()
    
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Motor Control State Machine")
    print("=" * 60)
    
    motor = MotorMachine()
    print(f"\nInitial state: {motor.current_state}")
    
    # Set operating parameters
    motor.voltage_volts = 230.0
    motor.temperature_celsius = 35.0
    
    # Start motor
    print("\n1. Starting motor...")
    motor.start()
    motor.run()
    
    # Check status
    print(f"\n2. Motor status:")
    print(f"  Running: {motor.is_running}")
    print(f"  Safe to service: {motor.is_safe_to_service}")
    
    # Simulate temperature rise
    print("\n3. Temperature rise detected...")
    motor.temperature_celsius = 85.0
    motor.fault()
    
    # Clear fault
    print("\n4. Cooling motor...")
    motor.temperature_celsius = 45.0
    
    print("\n5. Clearing fault...")
    if motor.clear_fault():
        print("✓ Fault cleared")
    else:
        print("✗ Cannot clear fault yet")
    
    motor.start()
    motor.run()
    print(f"\n✓ Motor recovered and running!")
