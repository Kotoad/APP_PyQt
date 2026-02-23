import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
import Elements_window
from Path_manager import PathManager
from ctypes import windll, wintypes, pointer, byref
import ctypes as ct
import Utils
import code_compiler
import os
from PIL import Image
import random
try:
    from pynput import mouse
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("Warning: pynput module not found.")

Options = ["Int", "Char"]

class GridCanvas(ctk.CTkCanvas):
    def __init__(self, parent, grid_size = 25, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.grid_size = grid_size
        self.dragged_widget = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        self._destroyed = False
        self.widget_nodes = {}
        self.bind("<Configure>", self.draw_grid)
        self.after(100, self.draw_grid)
        self.bind("<Destroy>", self._on_destroy)
    
    def _on_destroy(self, event):
        """Handle widget destruction"""
        self._destroyed = True
    #MARK: Grid drawing
    def draw_grid(self, event=None):
        if self._destroyed or self.is_dragging:
            return

        try:
            if not self.winfo_exists():
                return
        except (tk.TclError, AttributeError):
            return
        
        sx, sy = Utils.get_dpi_for_monitor(self.winfo_id())
        """Draw the visible grid lines on the canvas"""
        self.delete("grid_line")  # Remove existing grid lines
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:  # Skip if canvas not properly initialized
            return
        
        # Draw vertical lines
        for x in range(0, width + self.grid_size, self.grid_size):
            #print(f"Drawing x line at {x}")
            x = x * sx
            #print(f"Scaled x line at {x}")
            self.create_line(x, 0, x, height, fill="lightgray", width=1, tags="grid_line")
            
        
        # Draw horizontal lines
        for y in range(0, height + self.grid_size, self.grid_size):
            #print(f"Drawing y line at {y}")
            y = y * sy
            #print(f"Scaled y line at {y}")
            self.create_line(0, y, width, y, fill="lightgray", width=1, tags="grid_line")
            
        # Send grid lines to back
        self.tag_lower("grid_line")
    #MARK: Snapping and dragging
    def snap_to_grid(self, x, y, widget, during_drag):
        #Snap coordinates to the nearest grid intersection
        if not during_drag:
            widget.update_idletasks()

        
        height = widget.winfo_height()     
        grid_height = (round(height/self.grid_size))*self.grid_size
        #print(f"Widget height: {height}, Calculated grid height: {grid_height}")
        if height > grid_height:
            #print("Increasing grid height by one grid size")
            grid_height += self.grid_size
        elif height < self.grid_size:
            #print("Height less than grid size, setting to grid size")
            grid_height += self.grid_size
        if height == self.grid_size:
            #print("Height equals grid size, centering")
            height_offset = grid_height/2
        else:
            #print("Calculating height offset")
            height_offset = (grid_height - height)/2
        #print(f"Height: {height}, Grid height: {grid_height}, Height offset: {height_offset}")
        """round_x = round(x / self.grid_size)
        round_y = round(y / self.grid_size) 
        Grid_rounded_x = (round_x * self.grid_size)
        Grid_rounded_y = (round_y * self.grid_size)
        Grid_rounded_y_height_offset = Grid_rounded_y + height_offset
        snapped_x = int(Grid_rounded_x)
        snapped_y = int(Grid_rounded_y_height_offset)"""
        #print(f"snapped before adjustment: {snapped_x}, {snapped_y}")
        #print(f"Differences: {abs(x - snapped_x)}, {abs(y - snapped_y)}")
        
            
        snapped_x = int(round(x / self.grid_size) * self.grid_size)
        snapped_y = int((round(y / self.grid_size) * self.grid_size)+ height_offset)
        if (abs(y - snapped_y)) > (self.grid_size/2):
            print("Adjusting snapped_y upwards")
            snapped_y = int(snapped_y - self.grid_size)
        """print(f"Original {x}, {y}") 
        print(f"Rounded {round_x}, {round_y}")
        print(f"Grid {Grid_rounded_x, Grid_rounded_y}")
        print(f"Grid + height_offset {Grid_rounded_y_height_offset}")
        print(f"Snapped {snapped_x}, {snapped_y}")"""
        return snapped_x, snapped_y

    def on_canvas_click(self, event, widget):
        """Handle mouse click on canvas with DPI compensation"""
        for block_id, widget_info in Utils.top_infos.items():
            if widget_info['widget'] is widget:
                widget.update_idletasks()
                # ✅ Just calculate the actual offset from the widget's top-left
                self.offset_root_x = event.x_root - widget.winfo_rootx()
                self.offset_root_y = event.y_root - widget.winfo_rooty()
                
                
                self.dragged_widget = widget_info
                self.is_dragging = True
                #print("Clicked widget for dragging")
                
                if not isinstance(widget, (tk.Toplevel, ctk.CTkToplevel)):
                    widget.wm_attributes("-topmost", True)
                break

                
    def on_canvas_drag(self, event, widget):
        """Handle dragging of widgets with DPI compensation"""
        if self.dragged_widget and self.dragged_widget['widget'] is widget:
            sx, sy = Utils.get_dpi_for_monitor(self.winfo_id())

            # convert logical screen coords to canvas-local coords
            new_x = ((event.x_root - self.offset_root_x)/sx)
            new_y = ((event.y_root - self.offset_root_y)/sy)
            new_x = int(new_x)
            new_y = int(new_y)
            
            try:
                widget.wm_attributes("-topmost", True)
                widget.geometry(f"+{new_x}+{new_y}")
                self.dragged_widget['x'] = new_x
                self.dragged_widget['y'] = new_y
                if hasattr(self, 'path_manager'):
                    PathManager.update_paths_for_widget(self.path_manager, widget)
                #widget.update_idletasks()
            except Exception as e:
                print(f"Error placing widget: {e}")
                return
            
    def on_canvas_release(self, event, widget):
        """Handle mouse release - snap to grid"""
        if self.dragged_widget and self.dragged_widget['widget'] is widget:
            snapped_x, snapped_y = self.snap_to_grid(self.dragged_widget['x'], self.dragged_widget['y'], widget, during_drag=False)
            widget.wm_attributes("-topmost", True)
            widget.geometry(f"+{snapped_x}+{snapped_y}")
            self.dragged_widget['x'] = snapped_x
            self.dragged_widget['y'] = snapped_y
            self.dragged_widget = None
            self.is_dragging = False
            self.after_idle(self.draw_grid)
    
    
#MARK: Widget management
    def add_draggable_widget(self, widget):
        """Add a widget to the canvas that can be dragged and snapped"""
        
        # Get widget dimensions
        widget.update()
      
        try:
            widget.wm_attributes("-topmost", True)
        except Exception as e:
            print(f"Error setting topmost: {e}")
        
        widget.bind("<Button-1>", lambda e, w=widget: self.on_canvas_click(e, w))
        widget.bind("<B1-Motion>", lambda e, w=widget: self.on_canvas_drag(e, w))
        widget.bind("<ButtonRelease-1>", lambda e, w=widget: self.on_canvas_release(e, w))
    
    def remove_widget(self, widget):
        """Remove widget and its associated nodes"""
        # Remove from canvas widgets list
        Utils.top_infos = [w for w in Utils.top_infos if w['widget'] != widget]
        # Remove widget from canvas
        widget.destroy()

#MARK: Hybrid occlusion manager

class GlobalMouseListener:
    """
    FIXED VERSION using pynput library
    Much more reliable than Windows API hooks
    """
    
    def __init__(self):
        if not PYNPUT_AVAILABLE:
            print("WARNING: pynput not installed")
            print("Install with: pip install pynput")
            self.available = False
            return
        
        self.available = True
        self.listener = None
        self.on_click_callback = None
        self.running = False
    
    def set_callback(self, callback):
        """Set callback function(x, y, button_name)"""
        self.on_click_callback = callback
    
    def _on_click(self, x, y, button, pressed):
        """Called on any mouse click anywhere on system"""
        if pressed and self.on_click_callback:  # Only on button down
            try:
                # Convert button to string
                button_name = str(button).lower()
                if 'left' in button_name:
                    button_name = 'left'
                elif 'right' in button_name:
                    button_name = 'right'
                elif 'middle' in button_name:
                    button_name = 'middle'
                else:
                    button_name = 'unknown'
                
                if button_name != 'left':
                    return
                # Call callback
                self.on_click_callback(x, y, button_name)
                
            except Exception as e:
                print(f"Error in mouse callback: {e}")
    
    def start(self):
        """Start listening for global mouse clicks"""
        if not self.available:
            print("Mouse listener not available - pynput not installed")
            return
        
        if self.running:
            print("Mouse listener already running")
            return
        
        try:
            self.running = True
            self.listener = mouse.Listener(on_click=self._on_click)
            self.listener.start()
            print("✓ Global mouse listener started (pynput)")
            
        except Exception as e:
            print(f"✗ Failed to start mouse listener: {e}")
            self.running = False
    
    def stop(self):
        """Stop listening"""
        if not self.running:
            return
        
        try:
            if self.listener:
                self.listener.stop()
            self.running = False
            print("Global mouse listener stopped")
        except Exception as e:
            print(f"Error stopping listener: {e}")

class HybridOcclusionManager:
    def __init__(self, root):
        self.root = root
        self.user32 = windll.user32
        try:
            self.dwmapi = windll.dwmapi
        except:
            self.dwmapi = None
    
    def get_monitor_from_point(self, x, y):
        MONITOR_DEFAULTTONEAREST = 2
        point = wintypes.POINT(x, y)
        try:
            return self.user32.MonitorFromPoint(point, MONITOR_DEFAULTTONEAREST)
        except:
            return None
    
    def is_window_cloaked(self, hwnd):
        if not self.dwmapi:
            return False
        DWMWA_CLOAKED = 14
        cloaked = wintypes.DWORD()
        try:
            result = self.dwmapi.DwmGetWindowAttribute(
                hwnd, DWMWA_CLOAKED,
                ct.byref(cloaked), ct.sizeof(cloaked)
            )
            return result == 0 and cloaked.value != 0
        except:
            return False
    
    def should_show_window(self, window, main_window):
        try:
            # Check 1: Different monitor?
            mouse_x = self.root.winfo_pointerx()
            mouse_y = self.root.winfo_pointery()
            main_x = main_window.winfo_rootx() + (main_window.winfo_width() // 2)
            main_y = main_window.winfo_rooty() + (main_window.winfo_height() // 2)
            
            mouse_mon = self.get_monitor_from_point(mouse_x, mouse_y)
            main_mon = self.get_monitor_from_point(main_x, main_y)
            
            if mouse_mon and main_mon and mouse_mon != main_mon:
                if main_window.focus_displayof() is not None:
                    return True
                elif main_window.focus_displayof() is None:
                    return False
            
            # Check 2: Has focus?
            if main_window.focus_displayof() is not None:
                return True
            
            try:
                if Elements_window.elements_window and Elements_window.elements_window.winfo_exists():
                    if Elements_window.elements_window.focus_displayof() is not None:
                        return True
            except:
                pass
            
            # Check 3: Basic occlusion
            try:
                hwnd = self.user32.GetParent(window.winfo_id())
                if not self.user32.IsWindowVisible(hwnd):
                    return False
                if self.is_window_cloaked(hwnd):
                    return False
            except:
                pass
            
            return False
            
        except Exception as e:
            print(f"Error: {e}")
            return True
class Main_window():  
#MARK: Main window
    def __init__(self):
        #super().__init__();
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(2)
        except:
            try:
                windll.user32.SetProcessDPIAware()
            except:
                pass
        self.root = ctk.CTk()
        self.root.title("Custom Tkinter App")
        self.remove_title_bar_but_keep_in_taskbar()
        self.root.after(0, lambda:self.root.state('zoomed'))
        self.root.file_menu_win = None
        self.occlusion_manager = HybridOcclusionManager(self.root)
        self.root.grid_columnconfigure(0, weight=1)  # Canvas column expands
        self.root.grid_columnconfigure(1, weight=0)  # Variable frame stays fixed width
        self.root.grid_rowconfigure(1, weight=1)
        self.variable_frame = None  # Add this line to track the frame state
        self.variable_frame_visible = False  # Track visibility
        self.variable_row_count = 1
        self.create_menu_bar()
        self.create_canvas_frame()
        #self.setut_focus_hendlers()
        try:
            self.global_mouse_listener = GlobalMouseListener()
            self.global_mouse_listener.set_callback(self._on_global_click)
            self.global_mouse_listener.start()
        except ImportError as e:
            print(f"Mouse listener unavailable: {e}")
        self.global_mouse_listener = None
        self._check_app_focus()
        self.blockIDs = {}
    
    def remove_title_bar_but_keep_in_taskbar(self):
        GWL_STYLE = -16
        WS_CAPTION = 0x00C00000
        WS_THICKFRAME = 0x00040000
        WS_MINIMIZEBOX = 0x00020000
        WS_SYSMENU = 0x00080000
        WS_VISIBLE = 0x10000000
        hwnd = ct.windll.user32.GetParent(self.root.winfo_id())
        style = ct.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        style = (style & ~WS_CAPTION & ~WS_THICKFRAME) | WS_VISIBLE | WS_SYSMENU | WS_MINIMIZEBOX
        ct.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
        ct.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x27)
    #MARK: Focus handlers for block windows
    def block_menegment(self, block_id, window):
        self.blockIDs[block_id] = window

    def _on_global_click(self, x, y, button):
        """
        Called when ANY mouse click happens ANYWHERE on the system
        Even on different applications on different monitors!
        """
        #print(f"Global {button} click detected at ({x}, {y})")
        
        # Get which monitor was clicked
        mouse_monitor = self.get_monitor_from_point(x, y)
        
        # Get which monitor your main window is on
        main_x = self.root.winfo_rootx() + (self.root.winfo_width() // 2)
        main_y = self.root.winfo_rooty() + (self.root.winfo_height() // 2)
        main_monitor = self.get_monitor_from_point(main_x, main_y)
        
        # Check if clicked on different monitor
        if mouse_monitor != main_monitor:
            
            # Force show all elements
            if self.root.focus_displayof() is not None:
                #print(f"Clicked on DIFFERENT monitor - keeping elements visible")
                self._force_show_elements()
        else:
            #print(f"Clicked on SAME monitor")
            # Check if clicked inside your app
            if self._is_click_inside_app(x, y):
                if self.root.focus_displayof() is not None:
                    #print("Click inside app - keeping visible")
                    self._force_show_elements()
            else:
                #print("Click outside app on same monitor - may hide")
                # Let normal occlusion detection handle it
                pass
    
    def _force_show_elements(self):
        """Force show all element windows"""
        for block_id, window in Utils.top_infos.items():
            try:
                if window.winfo_exists() and not window.winfo_viewable():
                    window.deiconify()
                    window.wm_attributes("-topmost", True)
            except:
                pass
    
    def _is_click_inside_app(self, x, y):
        """Check if click coordinates are inside your app windows"""
        try:
            # Check main window
            main_x = self.root.winfo_rootx()
            main_y = self.root.winfo_rooty()
            main_w = self.root.winfo_width()
            main_h = self.root.winfo_height()
            
            if main_x <= x <= main_x + main_w and main_y <= y <= main_y + main_h:
                return True
            
            # Check element windows
            for window_id, window in self.blockIDs.items():
                if not window.winfo_exists():
                    continue
                    
                win_x = window.winfo_rootx()
                win_y = window.winfo_rooty()
                win_w = window.winfo_width()
                win_h = window.winfo_height()
                
                if win_x <= x <= win_x + win_w and win_y <= y <= win_y + win_h:
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking click position: {e}")
            return False
    
    def get_monitor_from_point(self, x, y):
        """Get monitor handle for coordinates"""
        MONITOR_DEFAULTTONEAREST = 2
        point = wintypes.POINT(x, y)
        try:
            return windll.user32.MonitorFromPoint(point, MONITOR_DEFAULTTONEAREST)
        except:
            return None
    
    def _check_app_focus(self):
        try:
            windows_to_remove = []
            
            for window_id, window in self.blockIDs.items():
                try:
                    if not window.winfo_exists():   
                        windows_to_remove.append(window_id)
                        continue
                    
                     # ← ADD THIS: Skip Elements window if it's intentionally hidden
                    if hasattr(window, 'elements_window_instance'):
                        if window.elements_window_instance.is_hidden:
                            #print(f"Skipping hidden window {window_id}")
                            continue
                    
                    should_show = self.occlusion_manager.should_show_window(window, self.root)
                    is_visible = window.winfo_viewable()
                    
                    if should_show and not is_visible:
                        print(f"Showing window {window}")
                        window.deiconify()
                        window.wm_attributes("-topmost", True)
                    elif not should_show and is_visible:
                        window.withdraw()
                        
                except Exception as e:
                    print(f"Error: {e}")
                    windows_to_remove.append(window_id)
            
            for window_id in windows_to_remove:
                del self.blockIDs[window_id]
                
        except Exception as e:
            print(f"Error: {e}")
        
        self.root.after(150, self._check_app_focus)
    
    #MARK: Canvas frame
    def create_canvas_frame(self):
        canvas_frame = ctk.CTkFrame(self.root)
        canvas_frame.grid(row=1, column=0, sticky="nsew")
        canvas_frame.grid_propagate(False)
        canvas_frame.grid_columnconfigure(0, weight=1)
        canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas = GridCanvas(
            canvas_frame, 
            bg="#2B2B2B",
            highlightthickness=1,
            highlightbackground="gray"
        )
        self.canvas.main_window = self
        self.canvas.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    #MARK: Menu bar
    def create_menu_bar(self):
        self.top_bar = ctk.CTkFrame(self.root, height=40, fg_color="#2B2B2B")
        self.top_bar.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.file_btn = ctk.CTkButton(self.top_bar, text="File", fg_color="#2B2B2B", hover_color="#3A3A3A", command=lambda: self.file_menu_open())
        self.edit_btn = ctk.CTkButton(self.top_bar, text="Edit", fg_color="#2B2B2B", hover_color="#3A3A3A", command=lambda: Elements_window.open_elements(self.canvas))
        self.compile_btn = ctk.CTkButton(self.top_bar, text="Run", fg_color="#2B2B2B", hover_color="#3A3A3A", command= lambda: code_compiler.Codecompiler.Start())
        self.variables_btn = ctk.CTkButton(self.top_bar, text="Variables", fg_color="#2B2B2B", hover_color="#3A3A3A", command= lambda: self.toggle_variables())
        
        self.file_btn.pack(side="left", padx=6, pady=6)
        self.edit_btn.pack(side="left", padx=6, pady=6)
        self.compile_btn.pack(side="right", padx=6, pady=6)
        self.variables_btn.pack(side="left", padx=6, pady=6)
    
    def file_menu_open(self):
        win = getattr(self.root, "file_menu_win", None)
        if win and win.winfo_exists():
            win.destroy()
            self.root.file_menu_win = None
        else:
            self.root.file_menu_win = self.file_menu(self.file_btn)

    def file_menu(self, btn):
        self.root.update_idletasks()
        
        file_options_frame = ctk.CTkToplevel(self.root, fg_color="#3A3A3A")
        file_options_frame.overrideredirect(True)
        file_options_frame.attributes('-topmost', True)
        self.block_menegment("file_menu", file_options_frame)
        self.root.update_idletasks()
        btn.update_idletasks()    

        btn_x = btn.winfo_rootx()
        btn_y = btn.winfo_rooty()
        btn_h = btn.winfo_height()

        popup_w, popup_h = 139, 150

        x = btn_x
        y = btn_y + btn_h

        file_options_frame.geometry(f"{popup_w}x{popup_h}+{x}+{y}")
        
        exit_btn = ctk.CTkButton(file_options_frame, text="Exit", fg_color="#3A3A3A", hover_color="#4A4A4A", command=self.root.destroy)
        exit_btn.pack(fill="x", padx=10, pady=5)
        return file_options_frame
    
    def toggle_variables(self):
        """Toggle the variable frame visibility"""
        if self.variable_frame_visible:
            # Hide the frame
            if self.variable_frame and self.variable_frame.winfo_exists():
                self.variable_frame.grid_forget()  # Remove from grid
            self.variable_frame_visible = False
        else:
            # Show the frame
            if self.variable_frame is None or not self.variable_frame.winfo_exists():
                # Create frame if it doesn't exist
                self.variable_frame = ctk.CTkScrollableFrame(self.root, fg_color="#2B2B2B")
                self.variable_frame.configure(width=300)
            
                # Show the frame
            self.variable_frame.grid(row=1, column=1, sticky="nse")
            self.variable_frame_visible = True
        
        self.variable_frame.grid_columnconfigure(0, weight=1)
        self.variable_frame.grid_rowconfigure(2, weight=1) 
        self.variables_menu = ctk.CTkFrame(self.variable_frame, height=40, fg_color="#2B2B2B")
        self.variables_menu.grid(row=0, column=0, columnspan=2, sticky="nsew")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        add_icon = ctk.CTkImage(
            light_image=Image.open(os.path.join(current_dir, "test_images", "chat_light.png")),
            size=(20, 20)  # Adjust size as needed
        )
        
        self.new_row_btn = ctk.CTkButton(
            self.variables_menu, 
            image=add_icon,
            text="",  # Empty text to show only image
            width=40,  # Set button width
            height=40,  # Set button height
            fg_color="#2B2B2B",
            hover_color="#3A3A3A",
            command= lambda: self.add_new_variable()  # Add your command here
        )
        self.new_row_btn.pack(side="left", padx=6, pady=6)
        
    
        
    def add_new_variable(self):
        print(f"Adding variable at row {self.variable_row_count}")

        
        def on_name_submit(event, ):
            # This function is called when user presses Enter
            var_name = name.get()
            var_pin = PIN.get()
            
            if var_name:
                Utils.variables[var_name] = {
                    'name': var_name,
                    'PIN': var_pin
                }
            self.canvas.focus_set()
        
        def on_PIN_submit(event):
            # This function is called when user presses Enter
            var_name = name.get()
            var_pin = PIN.get()
            
            if var_name:
                Utils.variables[var_name] = {
                    'name': var_name,
                    'PIN': var_pin
                }
            self.canvas.focus_set()
        
        name = ctk.CTkEntry(
            self.variable_frame,
            height=28,
            fg_color="#2B2B2B",
            placeholder_text=f"Variable {self.variable_row_count}"
        )
        PIN = ctk.CTkEntry(
            self.variable_frame,
            height=28,
            fg_color="#2B2B2B",
            placeholder_text=f"PIN"
        )
        name.grid(row=self.variable_row_count, column=0, sticky="nw", padx=5, pady=2)
        PIN.grid(row=self.variable_row_count, column=1, sticky="ew", padx=5, pady=2)
        
        #name.bind("<Button-1>", on_entry_click)      # Gain focus on click
        name.bind("<Return>", on_name_submit)       # Submit on Enter
        name.bind("<FocusOut>", on_name_submit)
        #PIN.bind("<Button-1>", on_entry_click)      # Gain focus on click
        PIN.bind("<Return>", on_PIN_submit)
        PIN.bind("<FocusOut>", on_PIN_submit)
    # Submit on Enter   
        
        self.variable_row_count += 1 
        
        
       
        
    def run(self):
        def on_closing():
            if hasattr(self, 'global_mouse_listener') and self.global_mouse_listener:
                try:
                    self.global_mouse_listener.stop()
                except:
                    pass
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    app = Main_window()
    app.run()