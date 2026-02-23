import customtkinter as ctk
import tkinter as tk
from spawn_elements import spawning_elements
import ctypes
from ctypes import wintypes


class VerticalTabView:
    """Custom vertical tabview for Elements window"""
    def __init__(self, master, **kwargs):
        self.master = master
        self.current_tab = None
        self.tabs = {}
        
        # Main container
        self.container = ctk.CTkFrame(master, fg_color="#2B2B2B", **kwargs)
        
        # Left side - tab buttons (vertical)
        self.button_frame = ctk.CTkFrame(
            self.container, 
            width=120, 
            fg_color="#1F1F1F"
        )
        self.button_frame.pack(side="left", fill="y", padx=(0, 2))
        self.button_frame.pack_propagate(False)
        
        # Right side - tab content
        self.content_frame = ctk.CTkFrame(self.container, fg_color="#2B2B2B")
        self.content_frame.pack(side="right", fill="both", expand=True)
    
    def add(self, name):
        """Add a new tab with given name"""
        btn = ctk.CTkButton(
            self.button_frame,
            text=name,
            fg_color="#1F1F1F",
            hover_color="#1F538D",
            command=lambda: self.set(name),
            anchor="w",
            height=35,
            corner_radius=6
        )
        btn.pack(fill="x", padx=5, pady=3)
        
        tab_content = ctk.CTkFrame(self.content_frame, fg_color="#2B2B2B")
        
        self.tabs[name] = {
            "button": btn,
            "content": tab_content
        }
        
        if len(self.tabs) == 1:
            self.set(name)
        
        return tab_content
    
    def set(self, name):
        """Switch to specified tab"""
        if name not in self.tabs:
            return
        
        for tab_name, tab_data in self.tabs.items():
            tab_data["content"].pack_forget()
            tab_data["button"].configure(fg_color="#1F1F1F")
        
        self.tabs[name]["content"].pack(fill="both", expand=True)
        self.tabs[name]["button"].configure(fg_color="#1F538D")
        self.current_tab = name
    
    def get(self):
        """Get current tab name"""
        return self.current_tab
    
    def delete(self, name):
        """Delete a tab"""
        if name in self.tabs:
            self.tabs[name]["button"].destroy()
            self.tabs[name]["content"].destroy()
            del self.tabs[name]
            
            if self.tabs:
                first_tab = list(self.tabs.keys())[0]
                self.set(first_tab)
    
    def pack(self, **kwargs):
        self.container.pack(**kwargs)
    
    def grid(self, **kwargs):
        self.container.grid(**kwargs)
    
    def place(self, **kwargs):
        self.container.place(**kwargs)

#MARK: Elements Window Class
class ElementsWindow:
    """
    Class-based Elements Window with vertical tabs
    Manages the window lifecycle and tab content
    """
    
    _instance = None  # Singleton instance
    
    def __init__(self, parent):
        """Initialize the Elements Window"""
        self.parent = parent
        self.window = None
        self.tabview = None
        self.element_spawner = spawning_elements(self.parent)
        #self.is_focus = False
        self.is_hidden = False  
        self.element_spawner.elements_window = self
        
    @classmethod
    def get_instance(cls, parent):
        """Get or create singleton instance"""
        if cls._instance is None or not cls._instance.window or not cls._instance.window.winfo_exists():
            cls._instance = cls(parent)
        return cls._instance
    
    def open(self):
        """Create or raise the elements window"""
        # Validate parent
        try:
            if not self.parent.winfo_exists():
                return None
        except (tk.TclError, AttributeError):
            return None

        if self.window:
            self.is_hidden = False
            self.window.deiconify()
            # Re-bind focus events after reopening
            print("Elements window opened")
        
        # If window exists
        if self.window is not None and self.window.winfo_exists():
            # DON'T show if manually hidden
            
            
            if self.is_hidden:
                print("Window is hidden, not showing")
                return self.window  # Return without showing
            
            # Only show and raise if not hidden
            print("Raising existing elements window")
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
            return self.window
        
        # Create new window
        try:
            self._create_window()
            self._setup_tabs()
            self._bind_events()
            self.is_hidden = False
            return self.window
        except (tk.TclError, AttributeError) as e:
            print(f"Error creating elements window: {e}")
            return None

    
    def _create_window(self):
        """Create the toplevel window"""
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Add Element")
        self.window.geometry("550x400")
        self.window.attributes('-topmost', True)
        self.window.elements_window_instance = self
        # Hide from taskbar
        self.window.after(100, lambda: self._hide_from_taskbar())
        
        # Block management
        try:
            main_window = self.parent.main_window
            if main_window:
                main_window.block_menegment("elements_window", self.window)
            else:
                print("Warning: Could not access main window")
        except AttributeError:
            print("Warning: main_window attribute not found")
    
    def _setup_tabs(self):
        """Setup vertical tabview and populate tabs"""
        self.tabview = VerticalTabView(self.window)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        shapes_tab = self.tabview.add("Shapes")
        logic_tab = self.tabview.add("Logic")
        io_tab = self.tabview.add("I/O")
        
        # Populate tabs
        self._create_shapes_tab(shapes_tab)
        self._create_logic_tab(logic_tab)
        self._create_io_tab(io_tab)
        
        # Set default tab
        self.tabview.set("Shapes")
    
    def _bind_events(self):
        """Bind window events"""
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
    
    """def _on_focus_in(self, event):
        #Handle focus in event
        self.is_focus = True
        print("Elements window gained focus")

    def _on_focus_out(self, event):
        #Handle focus out event
        self.is_focus = False
        print("Elements window lost focus")"""
    
    def _on_close(self):
        """Handle window close event"""
        try:
            if self.window:
                self.window.destroy()
        except:
            pass
        self.window = None
        ElementsWindow._instance = None
    
    def _create_shapes_tab(self, tab):
        """Create content for Shapes tab"""
        ctk.CTkLabel(
            tab,
            text="Shape Elements",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        # Shape buttons
        shapes = [
            ("Start", "Start"),
            ("End", "End"),
            ("Timer", "Timer")
        ]
        
        for label, shape_type in shapes:
            btn = ctk.CTkButton(
                tab,
                text=label,
                command=lambda s=shape_type: self._spawn_shape(s),
                fg_color="#3A3A3A",
                hover_color="#4A4A4A"
            )
            btn.pack(fill="x", padx=20, pady=5)
    
    def _create_logic_tab(self, tab):
        """Create content for Logic tab"""
        ctk.CTkLabel(
            tab,
            text="Logic Elements",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        # Logic buttons
        logic_elements = [
            ("If", "If"),
            ("While", "While"), 
            ("For Loop", "For Loop")
        ]
        
        
        for label, logic_type in logic_elements:
            btn = ctk.CTkButton(
                tab,
                text=label,
                command=lambda s=logic_type: self._spawn_shape(s),
                fg_color="#3A3A3A",
                hover_color="#4A4A4A"
            )
            btn.pack(fill="x", padx=20, pady=5)
    
    def _create_io_tab(self, tab):
        """Create content for I/O tab"""
        ctk.CTkLabel(
            tab,
            text="Input/Output Elements",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        # I/O buttons
        io_elements = ["Input", "Output", "Print", "Read File"]
        
        for element in io_elements:
            btn = ctk.CTkButton(
                tab,
                text=element,
                fg_color="#3A3A3A",
                hover_color="#4A4A4A"
            )
            btn.pack(fill="x", padx=20, pady=5)
    
    def _spawn_shape(self, shape_type):
        """Spawn a shape element"""
        try:
            self.element_spawner.start(self.parent, shape_type)
            print(f"Spawned: {shape_type}")
        except Exception as e:
            print(f"Error spawning {shape_type}: {e}")
    
    def _hide_from_taskbar(self):
        """Hide window from taskbar and Alt+Tab using Windows API"""
        try:
            # Don't process if window was manually hidden
            if self.is_hidden:
                print("Window is manually hidden, skipping taskbar hide")
                return
            
            # Get window handle
            hwnd = ctypes.windll.user32.GetParent(self.window.winfo_id())
            
            # Windows API constants
            GWL_EXSTYLE = -20
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_NOACTIVATE = 0x08000000
            
            # Get current style
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            
            # Modify style to hide from taskbar
            style = (style | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE) & ~WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            
            # Apply the style change - CHECK is_hidden AGAIN before deiconify
            self.window.withdraw()
            if not self.is_hidden:  # ← ADD THIS CHECK
                print("Re-showing window after hiding from taskbar")
                self.window.deiconify()
            
            print("Successfully hidden from taskbar and Alt+Tab")
        except Exception as e:
            print(f"Error hiding from taskbar: {e}")

    
    def close(self):
        """Manually close the window"""
        if self.window:
            self.is_hidden = True
            # Unbind focus events to prevent them interfering while hidden
            self.window.withdraw()
            print("Elements window closed")
            self._on_close()


# Convenience function for backward compatibility
def open_elements(parent):
    """
    Open the elements window (backward compatible function)
    
    Args:
        parent: Parent widget (canvas)
        
    Returns:
        ElementsWindow instance or None
    """
    window = ElementsWindow.get_instance(parent)
    return window.open()
