"""
State Machine Integration with CustomTkinter GUI
Best for: Real-world Python GUI applications

This example shows how to integrate state machines with CustomTkinter
for professional GUI applications. Perfect for your Python + GUI development.

Dependencies:
    pip install customtkinter python-statemachine
"""

import customtkinter as ctk
from statemachine import StateMachine, State
from typing import Optional


# ============================================================================
# STATE MACHINE DEFINITION
# ============================================================================

class FormMachine(StateMachine):
    """State machine for form submission workflow"""
    
    # States
    idle = State("Idle", initial=True)
    editing = State("Editing")
    validating = State("Validating")
    submitting = State("Submitting")
    success = State("Success", final=True)
    error = State("Error")
    
    # Transitions
    start_edit = idle.to(editing)
    submit_form = editing.to(validating)
    validation_passed = validating.to(submitting)
    validation_failed = validating.to(error)
    submit_success = submitting.to(success)
    submit_failed = submitting.to(error)
    retry = error.to(editing)
    reset = (error | success).to(idle)
    
    def __init__(self, gui_callback=None):
        self.gui_callback = gui_callback
        self.form_data = {}
        self.error_message = ""
        super().__init__()
    
    def _ui_update(self, message: str, msg_type: str):
        """Send UI update to callback"""
        if self.gui_callback:
            self.gui_callback(message, msg_type)
    
    # Entry handlers
    def on_enter_idle(self):
        self._ui_update("Ready for input", "info")
    
    def on_enter_editing(self):
        self._ui_update("Editing form...", "info")
    
    def on_enter_validating(self):
        # Simulate validation
        self._ui_update("Validating data...", "info")
        
        # Simple validation
        if not self.form_data.get("name"):
            self.error_message = "Name is required"
            self.validation_failed()
        elif not self.form_data.get("email"):
            self.error_message = "Email is required"
            self.validation_failed()
        elif "@" not in self.form_data.get("email", ""):
            self.error_message = "Invalid email format"
            self.validation_failed()
        else:
            self.validation_passed()
    
    def on_enter_submitting(self):
        self._ui_update("Submitting form...", "info")
        # Simulate API call
        try:
            # In real app: make HTTP request, save to DB, etc.
            self._ui_update(f"Submitted: {self.form_data['name']}", "success")
            self.submit_success()
        except Exception as e:
            self.error_message = str(e)
            self.submit_failed()
    
    def on_enter_success(self):
        self._ui_update("✓ Form submitted successfully!", "success")
    
    def on_enter_error(self):
        self._ui_update(f"❌ {self.error_message}", "error")


# ============================================================================
# CUSTOMTKINTER GUI APPLICATION
# ============================================================================

class FormApp(ctk.CTk):
    """CustomTkinter GUI for form submission with state machine"""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("State Machine Form Application")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Create state machine with GUI callback
        self.sm = FormMachine(gui_callback=self.update_ui)
        
        # Initialize GUI
        self.setup_ui()
        self.update_ui("Ready for input", "info")
    
    def setup_ui(self):
        """Build the GUI layout"""
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="User Registration Form",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(self, fg_color="#1f6aa5", corner_radius=8)
        self.status_frame.pack(fill="x", padx=20, pady=10)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Status: Ready",
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        self.status_label.pack(pady=10)
        
        # Form frame
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Name field
        ctk.CTkLabel(form_frame, text="Name:").pack(anchor="w", pady=(0, 5))
        self.name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your name"
        )
        self.name_entry.pack(fill="x", pady=(0, 15))
        
        # Email field
        ctk.CTkLabel(form_frame, text="Email:").pack(anchor="w", pady=(0, 5))
        self.email_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your email"
        )
        self.email_entry.pack(fill="x", pady=(0, 15))
        
        # Phone field
        ctk.CTkLabel(form_frame, text="Phone (optional):").pack(anchor="w", pady=(0, 5))
        self.phone_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter your phone"
        )
        self.phone_entry.pack(fill="x", pady=(0, 20))
        
        # Buttons frame
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        # Submit button
        self.submit_btn = ctk.CTkButton(
            button_frame,
            text="Submit",
            command=self.on_submit,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.submit_btn.pack(fill="x", pady=5)
        
        # Retry button (initially hidden)
        self.retry_btn = ctk.CTkButton(
            button_frame,
            text="Retry",
            command=self.on_retry,
            fg_color="#ff9500",
            hover_color="#ff7f00",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        
        # Reset button (initially hidden)
        self.reset_btn = ctk.CTkButton(
            button_frame,
            text="Reset",
            command=self.on_reset,
            fg_color="#555555",
            hover_color="#444444",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        
        # State display (for debugging)
        self.state_label = ctk.CTkLabel(
            self,
            text=f"Current State: {self.sm.current_state.id}",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.state_label.pack(pady=10)
    
    def on_submit(self):
        """Handle submit button click"""
        if self.sm.current_state == self.sm.idle:
            self.sm.start_edit()
        
        if self.sm.current_state == self.sm.editing:
            # Collect form data
            self.sm.form_data = {
                "name": self.name_entry.get(),
                "email": self.email_entry.get(),
                "phone": self.phone_entry.get(),
            }
            # Trigger submission
            self.sm.submit_form()
    
    def on_retry(self):
        """Handle retry button click"""
        self.sm.retry()
    
    def on_reset(self):
        """Handle reset button click"""
        self.clear_form()
        self.sm.reset()
    
    def clear_form(self):
        """Clear form fields"""
        self.name_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
    
    def update_ui(self, message: str, msg_type: str):
        """Update UI based on state machine state"""
        # Color mapping
        colors = {
            "info": "#1f6aa5",
            "success": "#0f7c3d",
            "error": "#c41e3a",
        }
        
        # Update status bar
        self.status_frame.configure(fg_color=colors.get(msg_type, "#1f6aa5"))
        self.status_label.configure(text=f"Status: {message}")
        
        # Update state display
        self.state_label.configure(
            text=f"Current State: {self.sm.current_state.id} | "
                 f"Form: {self.sm.form_data.get('name', 'N/A')}"
        )
        
        # Update button visibility based on state
        current_state = self.sm.current_state
        
        if current_state == self.sm.idle:
            self.submit_btn.configure(text="Start", state="normal")
            self.retry_btn.pack_forget()
            self.reset_btn.pack_forget()
            self.enable_form_fields(True)
        
        elif current_state == self.sm.editing:
            self.submit_btn.configure(text="Submit", state="normal")
            self.retry_btn.pack_forget()
            self.reset_btn.pack_forget()
            self.enable_form_fields(True)
        
        elif current_state in (self.sm.validating, self.sm.submitting):
            self.submit_btn.configure(state="disabled")
            self.retry_btn.pack_forget()
            self.reset_btn.pack_forget()
            self.enable_form_fields(False)
        
        elif current_state == self.sm.success:
            self.submit_btn.pack_forget()
            self.retry_btn.pack_forget()
            self.reset_btn.pack(fill="x", pady=5)
            self.enable_form_fields(False)
        
        elif current_state == self.sm.error:
            self.submit_btn.pack_forget()
            self.retry_btn.pack(fill="x", pady=5)
            self.reset_btn.pack(fill="x", pady=5)
            self.enable_form_fields(True)
    
    def enable_form_fields(self, enabled: bool):
        """Enable/disable form input fields"""
        state = "normal" if enabled else "disabled"
        self.name_entry.configure(state=state)
        self.email_entry.configure(state=state)
        self.phone_entry.configure(state=state)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Set appearance mode
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and run app
    app = FormApp()
    app.mainloop()
