import customtkinter as ctk
import tkinter as tk
import random
from PIL import Image, ImageDraw, ImageTk, ImageFont
from Path_manager import PathManager
import Utils
top = None  # Module-level reference to the Toplevel window


#MARK: Spawning elements
class spawning_elements:
    def __init__(self, parent):
        self.placing_active = False
        self.perm_stop = False
        self.element_placed = False
        self.parent = parent  # Store parent reference
        self.elements_window = None
        self.element_spawner = Element_spawn()
        # Bind using named methods
        

    def on_return_pressed(self, event):
        print("Return pressed")
        """Handle Return key press"""
        self.stop_placing(self.parent)

    def on_escape_pressed(self, event):
        print("Escape pressed")
        """Handle Escape key press"""
        self.stop_placing(self.parent)

    def on_lButton_pressed(self, event):
        """Handle Space key press"""
        self.place(event)
    
    def start(self, parent, type):
        self.type = type
        self.perm_stop = False
        print("Start placement")
        
        # Hide window FIRST, before any bindings or operations
        if self.elements_window and self.elements_window.window:
            self.elements_window.is_hidden = True
            self.elements_window.window.withdraw()
        
        parent.bind_all("<Return>", self.on_return_pressed)
        parent.bind_all("<Escape>", self.on_escape_pressed)
        parent.bind("<Button-1>", self.on_lButton_pressed)

        
    def check_placing(self, parent, event):
        if self.perm_stop:
            return  # Exit if permanent stop is activated
        print(f"Checking placing: perm_stop={self.perm_stop}, placing_active={self.placing_active}")
        
        if self.element_placed == False and self.placing_active == True:
            self.element_spawner.Custom_shape_spawn(parent, self.type, event)
            self.placing_active = False  # Reset flag after one placement
            self.element_placed = True
            parent.update()
            return
    
    def place(self, event):
        print("Placement started")
        self.placing_active = True
        self.element_placed = False
        self.check_placing(self.parent, event)
    
    def stop_placing(self, parent):
        print("Placement stopped")
        """Stop the placement loop"""
        self.perm_stop = True
        self.placing_active = False
        self.element_placed = False
        parent.unbind_all("<Return>")
        parent.unbind_all("<Escape>")
        parent.unbind("<Button-1>")
        if self.elements_window:
        # Reset the hidden flag BEFORE calling open()
            self.elements_window.is_hidden = False
            self.elements_window.open()
#MARK: Element events
class Elements_events:
    def __init__(self):
        self.path_manager = None
        pass
    
    def on_canvas_click(self, event, top, canvas, type):
        canvas.update_idletasks()
        
        # Get ACTUAL canvas dimensions
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        circle_radius = Element_spawn.height / 5
        
        print(f"Canvas dimensions: {canvas_width}x{canvas_height}")
        print(f"Click position: ({event.x}, {event.y})")
        print(f"Circle radius: {circle_radius}")
        
        # Circle positions based on ACTUAL canvas size
        circle_in_center_x = circle_radius  # Left circle
        circle_in_center_y = canvas_height / 2
        
        if type == "If":
            # Right side circles for If type
            circle_out_center_x1 = canvas_width - circle_radius
            circle_out_center_y1 = (canvas_height - 2*circle_radius) / 4 + circle_radius
            circle_out_center_y2 = 3 * (canvas_height - 2*circle_radius) / 4 + circle_radius
            
            # Calculate distances
            distance_in_x = (event.x - circle_in_center_x)**2
            distance_in_y = (event.y - circle_in_center_y)**2
            distance_in = (distance_in_x + distance_in_y)**0.5
            distance_out1_x = (event.x - circle_out_center_x1)**2
            distance_out1_y = (event.y - circle_out_center_y1)**2
            distance_out1 = (distance_out1_x + distance_out1_y)**0.5
            distance_out2_x = (event.x - circle_out_center_x1)**2
            distance_out2_y = (event.y - circle_out_center_y2)**2
            distance_out2 = (distance_out2_x + distance_out2_y)**0.5
            print(f"event.x: {event.x}, event.y: {event.y}")
            print(f"center1: ({circle_out_center_x1}, {circle_out_center_y1}), center2: ({circle_out_center_x1}, {circle_out_center_y2})")
            print(f"Distances: in={distance_in:.1f}, out1={distance_out1:.1f}, out2={distance_out2:.1f}")
            
            if distance_in <= circle_radius:
                print("White circle clicked!")
                self.handle_circle_in_click(top, event.x_root, event.y_root, distance_in_x, distance_in_y)
            elif distance_out1 <= circle_radius:
                print("Red circle clicked!")
                self.handle_circle_out1_click(top, event.x_root, event.y_root, distance_out1_x, distance_out1_y)
            elif distance_out2 <= circle_radius:
                print("Green circle clicked!")
                self.handle_circle_out2_click(top, event.x_root, event.y_root, distance_out2_x, distance_out2_y)
            else:
                print("Canvas clicked, but not on any circle.")
        else:
            # For Start, End, Timer (2 circles)
            circle_out_center_x1 = canvas_width - circle_radius
            circle_out_center_y1 = canvas_height / 2
            
            distance_in_x = (event.x - circle_in_center_x)**2
            distance_in_y = (event.y - circle_in_center_y)**2
            distance_in = (distance_in_x + distance_in_y)**0.5
            distance_out1_x = (event.x - circle_out_center_x1)**2
            distance_out1_y = (event.y - circle_out_center_y1)**2
            distance_out1 = (distance_out1_x + distance_out1_y)**0.5
            
            print(f"event.x: {event.x}, event.y: {event.y}")
            print(f"center1: ({circle_out_center_x1}, {circle_out_center_y1})")
            print(f"Distances: in={distance_in:.1f}, out1={distance_out1:.1f}")
            
            if distance_in <= circle_radius:
                print("White circle clicked!")
                self.handle_circle_in_click(top, event.x_root, event.y_root, distance_in_x, distance_in_y)
            elif distance_out1 <= circle_radius:
                print("Red circle clicked!")
                self.handle_circle_out1_click(top, event.x_root, event.y_root, distance_out1_x, distance_out1_y)
            else:
                print("Canvas clicked, but not on any circle.")   
    
    def handle_circle_in_click(self, top,  circle_in_x, circle_in_y, distance_in_x, distance_in_y):
        # Do something when circle is clicked
        #print("White circle was clicked!")
        #print(top.winfo_id())
        for block_id, top_info in Utils.top_infos.items():
            if top_info["widget"] is top:
                circle_center = (
                    circle_in_x - distance_in_x,
                    circle_in_y - distance_in_y
                )
                print(f"event.x: {circle_in_x}, event.y: {circle_in_y}")
                print(f"distance_in_x: {distance_in_x}, distance_in_y: {distance_in_y}")
                print(f"Circle center: {circle_center}")
                if not hasattr(top.master, 'pathmanager'):
                    main_canvas = top.master  # GridCanvas
                    
                    # Convert to canvas coordinates for PathManager
                    canvas_x = circle_center[0] - main_canvas.winfo_rootx()
                    canvas_y = circle_center[1] - main_canvas.winfo_rooty()
                    canvas_circlecenter = (canvas_x, canvas_y)
                    
                    print(f"Screen circle center: {circle_center}")
                    print(f"Canvas circle center: {canvas_circlecenter}")
                    
                    # PathManager uses canvas coordinates internally
                    pathmgr = top.master.path_manager
                    pathmgr.finalize_connection(top, canvas_circlecenter, circle_type="in")
                else:
                    print("Warning: PathManager not initialized on canvas")
            else:
                #print(f"Top {top.winfo_id()} mismatch in stored infos")
                pass
        # Change color, trigger action, etc.
        
    def handle_circle_out1_click(self, top, circle_out_x, circle_out_y, distance_out1_x, distance_out1_y):
        # Do something when circle is clicked
        #print("White circle was clicked!")
        #print(top.winfo_id())
        
        for block_id, top_info in Utils.top_infos.items():
            if top_info["widget"] is top:
                circle_center = (
                    circle_out_x - distance_out1_x,
                    circle_out_y - distance_out1_y
                )
                print(f"event.x: {circle_out_x}, event.y: {circle_out_y}")
                print(f"distance_out1_x: {distance_out1_x}, distance_out1_y: {distance_out1_y}")
                print(f"Circle center: {circle_center}")
                if not hasattr(top.master, 'pathmanager'):
                    main_canvas = top.master  # GridCanvas
                    
                    # Convert to canvas coordinates for PathManager
                    canvas_x = circle_center[0] - main_canvas.winfo_rootx()
                    canvas_y = circle_center[1] - main_canvas.winfo_rooty()
                    canvas_circlecenter = (canvas_x, canvas_y)
                    
                    print(f"Screen circle center: {circle_center}")
                    print(f"Canvas circle center: {canvas_circlecenter}")
                    if top_info["type"] == "If":
                        circle_type = "out1"
                    else:
                        circle_type = "out"
                    # PathManager uses canvas coordinates internally
                    pathmgr = top.master.path_manager
                    pathmgr.start_connection(top, canvas_circlecenter, circle_type)
                else:
                    print("Warning: PathManager not initialized on canvas")
            else:
                #print(f"Top {top.winfo_id()} mismatch in stored infos")
                pass
    
    def handle_circle_out2_click(self, top, circle_out_x, circle_out_y, distance_out2_x, distance_out2_y):
        # Do something when circle is clicked
        #print("White circle was clicked!")
        #print(top.winfo_id())
        for block_id, top_info in Utils.top_infos.items():
            if top_info["widget"] is top:
                circle_center = (
                    circle_out_x - distance_out2_x,
                    circle_out_y - distance_out2_y
                )
                print(f"event.x: {circle_out_x}, event.y: {circle_out_y}")
                print(f"distance_out1_x: {distance_out2_x}, distance_out1_y: {distance_out2_y}")
                print(f"Circle center: {circle_center}")
                if not hasattr(top.master, 'pathmanager'):
                    main_canvas = top.master  # GridCanvas
                    
                    # Convert to canvas coordinates for PathManager
                    canvas_x = circle_center[0] - main_canvas.winfo_rootx()
                    canvas_y = circle_center[1] - main_canvas.winfo_rooty()
                    canvas_circlecenter = (canvas_x, canvas_y)
                    
                    print(f"Screen circle center: {circle_center}")
                    print(f"Canvas circle center: {canvas_circlecenter}")
                    
                    # PathManager uses canvas coordinates internally
                    pathmgr = top.master.path_manager
                    pathmgr.start_connection(top, canvas_circlecenter, circle_type="out2")
                else:
                    print("Warning: PathManager not initialized on canvas")
            else:
                #print(f"Top {top.winfo_id()} mismatch in stored infos")
                pass

#MARK: Element spawn
class Element_spawn:
    height = 36
    width = 100
    
    def __init__(self):
        # Widget configuration dictionary
        self.widget_configs = {
            'Start': {
                'creator': Creating_elemets.create_Start_End,
                'height': self.height,
                'type': 'Start',
                'has_entry': False,
                'has_optionbox': False
            },
            'End': {
                'creator': Creating_elemets.create_Start_End,
                'height': self.height,
                'type': 'End',
                'has_entry': False,
                'has_optionbox': False
            },
            'Timer': {
                'creator': Creating_elemets.create_timer,
                'height': self.height,
                'type': 'Timer',
                'has_entry': True,
                'entry_config': {
                    'width': 30,
                    'height': 20,
                    'x_offset': 10,  # Offset from center
                    'y_offset': -10
                },
                'has_optionbox': False
            },
            'If': {
                'creator': Creating_elemets.create_if,
                'height': self.height + 25,
                'type': 'If',
                'has_entry': False,
                'has_optionbox': True,
                'optionbox_config': {
                    'values': ['>', '<', '==', '!='],
                    'width': 50,
                    'x_offset': 5,
                    'y_offset': -10
                }
            },
            'While': {
                'creator': Creating_elemets.create_while,
                'height': self.height + 25,
                'type': 'While',
                'has_entry': False,
                'has_optionbox': False
            }
        }
        
        self.elements_events = Elements_events()
        
    
    def create_start(self, parent, event, **kwargs):
        """Create Start element"""
        photo = Creating_elemets.create_Start_End(
            self,
            width=self.width,
            height=self.height,
            scale=3,
            fill='yellow',
            outline="#000000",
            outline_width=2,
            type='Start'
        )
        return photo
    
    def create_end(self, parent, event, **kwargs):
        """Create End element"""
        photo = Creating_elemets.create_Start_End(
            self,
            width=self.width,
            height=self.height,
            scale=3,
            fill='yellow',
            outline="#000000",
            outline_width=2,
            type='End'
        )
        return photo
    
    def create_timer(self, parent, event, **kwargs):
        """Create Mid element"""
        photo = Creating_elemets.create_timer(
            self,
            width=self.width,
            height=self.height,
            scale=3,
            fill='yellow',
            outline="#000000",
            outline_width=2,
            type='Timer'
        )
        return photo

    def create_if(self, parent, event, **kwargs):
        photo = Creating_elemets.create_if(
            self,
            width=self.width,
            height=self.height+25,
            scale=3,
            fill='yellow',
            outline="#000000",
            outline_width=2,
            type='If'
        )
        return photo
    
    def create_while(self, parent, event, **kwargs):
        photo = Creating_elemets.create_while(
            self,
            width=self.width,
            height=self.height+25,
            scale=3,
            fill='yellow',
            outline="#000000",
            outline_width=2,
            type='While'
        )
        return photo

    def _add_widgets(self, top, canvas, config, total_width, element_height):
        """Add entry boxes, option menus, etc. based on configuration"""
        
        # Add entry if configured
        if config.get('has_entry', False):
            entry_cfg = config['entry_config']
            entry = ctk.CTkEntry(
                top,
                width=entry_cfg['width'],
                height=entry_cfg['height'],
                fg_color="#FFFFFF",
                text_color="#000000",
                border_width=1,
                corner_radius=3
            )
            
            # Calculate position
            x_pos = total_width // 2 + entry_cfg.get('x_offset', 0)
            y_pos = element_height // 2 + entry_cfg.get('y_offset', 0)
            entry.place(x=x_pos, y=y_pos)
            
            # Bind events
            def on_entry_submit(event):
                value = entry.get()
                print(f"Entry value: {value}")
                canvas.focus_set()
            
            entry.bind("<Return>", on_entry_submit)
            entry.bind("<KP_Enter>", on_entry_submit)
            top.entry_widget = entry
        
        # Add optionbox if configured
        if config.get('has_optionbox', False):
            opt_cfg = config['optionbox_config']
            optionbox = ctk.CTkOptionMenu(
                top,
                values=opt_cfg['values'],
                width=opt_cfg['width'],
                fg_color="#FFFFFF",
                text_color="#000000",
                button_color="#CCCCCC",
                button_hover_color="#AAAAAA"
            )
            
            # Calculate position
            x_pos = total_width // 2 + opt_cfg.get('x_offset', 0)
            y_pos = element_height // 2 + opt_cfg.get('y_offset', 0)
            optionbox.place(x=x_pos, y=y_pos)
            top.optionbox_widget = optionbox

    def _configure_window(self, top, parent, event, total_width, element_height, type):
        """Configure window position and appearance"""
        screenx = event.x_root
        screeny = event.y_root
        snapped_x, snapped_y = parent.snap_to_grid(screenx, screeny, top, during_drag=False)
        
        top.wm_attributes('-topmost', True)
        top.attributes('-toolwindow', True)
        top.geometry(f'+{snapped_x}+{snapped_y}')
        top.configure(bg='magenta')
        
        try:
            top.wm_attributes('-transparentcolor', 'magenta')
        except tk.TclError:
            pass
        
        # Register with block management
        block_id = id(top)
        mainwindow = parent.main_window
        if mainwindow:
            mainwindow.block_menegment(block_id, top)
        
        parent.add_draggable_widget(top)
        
        Utils.top_infos[block_id] = {
            'widget': top,
            'id': block_id,
            'type': type,
            'x': snapped_x,
            'y': snapped_y,
            'width': self.width,
            'height': element_height,
            'in_connections': [],
            'out_connections': []
        }

    
    def Custom_shape_spawn(self, parent, type, event):
        global top
        
        # Get configuration for this type
        config = self.widget_configs.get(type)
        if config is None:
            print(f"Unknown type: {type}")
            return None
        
        if not hasattr(parent, 'path_manager'):
            parent.path_manager = PathManager(parent)
        
        top = tk.Toplevel(parent)
        top.overrideredirect(True)
        top.update_idletasks()
        
        # Element dimensions
        radius = self.height / 4
        total_width = self.width + 2 * radius
        element_height = config['height']
        
        # Create the PIL image using configured creator
        photo = config['creator'](
            self,
            width=self.width,
            height=element_height,
            scale=3,
            fill='yellow',
            outline="#000000",
            outline_width=2,
            type=config.get('type', type)
        )
        
        # Create canvas
        canvas = tk.Canvas(
            top,
            width=int(total_width),
            height=int(element_height),
            bg='magenta',
            highlightthickness=0,
            bd=0
        )
        canvas.pack(fill='both', expand=True)
        canvas.create_image(0, 0, image=photo, anchor='nw')
        canvas.image = photo
        canvas.bind("<Button-1>", lambda e, t=top, c=canvas, ty=type: 
                    self.elements_events.on_canvas_click(e, t, c, ty))
        
        # Add widgets based on configuration
        self._add_widgets(top, canvas, config, total_width, element_height)
        
        # Position and configure window
        self._configure_window(top, parent, event, total_width, element_height, type)
        
        return top

    
#MARK: Element creation
class Creating_elemets:
    def create_Start_End(self, width=100, height=36, scale=3,
                    fill='yellow', outline='#000000',
                    outline_width=2, type='NONE'):
        """
        Create high-quality rounded rectangle with semicircular caps using PIL.
        Uses alpha masking to prevent edge bleeding while maintaining quality.
        """
        # Calculate dimensions
        radius = height / 6
        semi_y_offset = (height - 2 * radius) / 2
        total_width = width + 2 * radius
        
        # Scale up for high resolution rendering
        img_width = int(total_width * scale)
        img_height = int(height * scale)
        scaled_width = int(width * scale)
        scaled_radius = radius * scale
        scaled_semi_offset = semi_y_offset * scale
        #print(f"Scaled semi offset{scaled_semi_offset}, Scaled radius {scaled_radius}, semi offset {semi_y_offset}, radius {radius}, scaled {scale}")
        scaled_outline = outline_width * scale
        
        # Step 1: Create shape with ALPHA CHANNEL at high resolution
        img_rgba = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img_rgba)
        
        # Draw filled shapes (with full opacity)
        draw.rectangle(
            [scaled_radius, 0, scaled_width + scaled_radius, img_height],
            fill=fill + (255,) if isinstance(fill, tuple) else fill,
            outline=None
        )
        if type == 'End':
            draw.ellipse(
                [0, scaled_semi_offset,
                2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
                fill=fill + (255,) if isinstance(fill, tuple) else fill,
                outline=None
            )
            
            draw.ellipse(
            [0, scaled_semi_offset,
            2 * (scaled_radius-1), scaled_semi_offset + 2 * (scaled_radius-1)],
            fill='white',
            outline=None
            )
        if type == 'Start':
            draw.ellipse(
                [scaled_width, scaled_semi_offset,
                scaled_width + 2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
                fill=fill + (255,) if isinstance(fill, tuple) else fill,
                outline=None
            )
            
            draw.ellipse(
                [scaled_width, scaled_semi_offset,
                scaled_width + 2 * (scaled_radius-1), scaled_semi_offset + 2 * (scaled_radius-1)],
                fill='red',
                outline=None
            )
        
        try:
            font = ImageFont.truetype("arial.ttf", int(15 * scale))  # Adjust size as needed
        except:
            font = ImageFont.load_default()  # Fallback to default font
        
        text = str(type)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text on the image
        text_x = (img_width - text_width) // 2
        text_y = ((img_height - text_height) // 3)+3
        #print(f"Image height{img_height}, text height {text_height}") 
        draw.text((text_x, text_y), text, fill='black', font=font)
        
        
        # Draw outline with cheap antialiasing
        if outline:
            
            # Main outline pass
            if type == 'End':
                draw.ellipse(
                    [0, scaled_semi_offset,
                    2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
                    outline=outline,
                    width=int(scaled_outline)
                )
                
            if type == 'Start':
                draw.ellipse(
                    [scaled_width, scaled_semi_offset,
                    scaled_width + 2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
                    outline=outline,
                    width=int(scaled_outline)
                )
            
            draw.line(
                [scaled_radius, int(scaled_outline/2),
                scaled_width + scaled_radius, int(scaled_outline/2)],
                fill=outline,
                width=int(scaled_outline)
            )
            
            draw.line(
                [scaled_radius, img_height - int(scaled_outline/2),
                scaled_width + scaled_radius, img_height - int(scaled_outline/2)],
                fill=outline,
                width=int(scaled_outline)
            )
        
        # Step 2: Resize WITH LANCZOS (shape will be smooth)
        img_rgba_resized = img_rgba.resize((int(total_width), int(height)), Image.LANCZOS)
        
        # Step 3: Convert alpha to binary (sharp edges) to prevent blending
        # This is the KEY - make alpha either 0 or 255, no in-between
        alpha = img_rgba_resized.split()[3]  # Get alpha channel
        alpha_data = alpha.load()
        
        # Convert semi-transparent pixels to either fully transparent or fully opaque
        threshold = 128  # Adjust if needed (0-255)
        for y in range(alpha.height):
            for x in range(alpha.width):
                if alpha_data[x, y] < threshold:
                    alpha_data[x, y] = 0  # Fully transparent
                else:
                    alpha_data[x, y] = 255  # Fully opaque
        
        # Step 4: Composite onto magenta background
        img_final = Image.new('RGB', (int(total_width), int(height)), (255, 0, 255))
        img_final.paste(img_rgba_resized, (0, 0), alpha)
        
        return ImageTk.PhotoImage(img_final)
    #MARK: - Timer creation
    def create_timer(self, width=100, height=36, scale=3,
                    fill='yellow', outline='#000000',
                    outline_width=2, type='NONE'):
        """
        Create high-quality rounded rectangle with semicircular caps using PIL.
        Uses alpha masking to prevent edge bleeding while maintaining quality.
        """
        # Calculate dimensions
        radius = height / 6
        semi_y_offset = (height - 2 * radius) / 2
        total_width = width + 2 * radius
        
        # Scale up for high resolution rendering
        img_width = int(total_width * scale)
        img_height = int(height * scale)
        scaled_width = int(width * scale)
        scaled_radius = radius * scale
        scaled_semi_offset = semi_y_offset * scale
        #print(f"Scaled semi offset{scaled_semi_offset}, Scaled radius {scaled_radius}, semi offset {semi_y_offset}, radius {radius}, scaled {scale}")
        scaled_outline = outline_width * scale
        
        # Step 1: Create shape with ALPHA CHANNEL at high resolution
        img_rgba = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img_rgba)
        
        # Draw filled shapes (with full opacity)
        draw.rectangle(
            [scaled_radius, 0, scaled_width + scaled_radius, img_height],
            fill=fill + (255,) if isinstance(fill, tuple) else fill,
            outline=None
        )
        
        draw.ellipse(
            [0, scaled_semi_offset,
            2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
            fill=fill + (255,) if isinstance(fill, tuple) else fill,
            outline=None
        )
        
        draw.ellipse(
            [scaled_width, scaled_semi_offset,
            scaled_width + 2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
            fill=fill + (255,) if isinstance(fill, tuple) else fill,
            outline=None
        )
        
        draw.ellipse(
            [0, scaled_semi_offset,
            2 * (scaled_radius-1), scaled_semi_offset + 2 * (scaled_radius-1)],
            fill='white',
            outline=None
        )
        
        draw.ellipse(
            [scaled_width, scaled_semi_offset,
            scaled_width + 2 * (scaled_radius-1), scaled_semi_offset + 2 * (scaled_radius-1)],
            fill='red',
            outline=None
        )
        
        try:
            font = ImageFont.truetype("arial.ttf", int(15 * scale))  # Adjust size as needed
        except:
            font = ImageFont.load_default()  # Fallback to default font
        
        text = "Timer"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text on the image
        text_x = 60
        text_y = ((img_height - text_height) // 3)+3
        #print(f"Image height{img_height}, text height {text_height}") 
        draw.text((text_x, text_y), text, fill='black', font=font)
        
        
        # Draw outline with cheap antialiasing
        if outline:
            
            # Main outline pass
            draw.ellipse(
                [0, scaled_semi_offset,
                2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
                outline=outline,
                width=int(scaled_outline)
            )
            
            draw.ellipse(
                [scaled_width, scaled_semi_offset,
                scaled_width + 2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
                outline=outline,
                width=int(scaled_outline)
            )
            
            draw.line(
                [scaled_radius, int(scaled_outline/2),
                scaled_width + scaled_radius, int(scaled_outline/2)],
                fill=outline,
                width=int(scaled_outline)
            )
            
            draw.line(
                [scaled_radius, img_height - int(scaled_outline/2),
                scaled_width + scaled_radius, img_height - int(scaled_outline/2)],
                fill=outline,
                width=int(scaled_outline)
            )
        
        # Step 2: Resize WITH LANCZOS (shape will be smooth)
        img_rgba_resized = img_rgba.resize((int(total_width), int(height)), Image.LANCZOS)
        
        # Step 3: Convert alpha to binary (sharp edges) to prevent blending
        # This is the KEY - make alpha either 0 or 255, no in-between
        alpha = img_rgba_resized.split()[3]  # Get alpha channel
        alpha_data = alpha.load()
        
        # Convert semi-transparent pixels to either fully transparent or fully opaque
        threshold = 128  # Adjust if needed (0-255)
        for y in range(alpha.height):
            for x in range(alpha.width):
                if alpha_data[x, y] < threshold:
                    alpha_data[x, y] = 0  # Fully transparent
                else:
                    alpha_data[x, y] = 255  # Fully opaque
        
        # Step 4: Composite onto magenta background
        img_final = Image.new('RGB', (int(total_width), int(height)), (255, 0, 255))
        img_final.paste(img_rgba_resized, (0, 0), alpha)
        
        return ImageTk.PhotoImage(img_final)
    #MARK: - If creation
    def create_if(self, width=100, height=36, scale=3,
                        fill='yellow', outline='#000000',
                        outline_width=2, type='NONE'):
            """
            Create high-quality rounded rectangle with semicircular caps using PIL.
            Uses alpha masking to prevent edge bleeding while maintaining quality.
            """
            # Calculate dimensions
            radius = height / 10
            semi_y_offset = (height - 2 * radius) / 2
            semi_y_offset1 = (height - 2 * radius) / 4
            semi_y_offset2 = 3 * (height - 2 * radius) / 4
            total_width = width + 2 * radius
            
            # Scale up for high resolution rendering
            img_width = int(total_width * scale)
            img_height = int(height * scale)
            scaled_width = int(width * scale)
            scaled_radius = radius * scale
            scaled_semi_offset = semi_y_offset * scale
            scaled_semi_offset1 = semi_y_offset1 * scale
            scaled_semi_offset2 = semi_y_offset2 * scale
            #print(f"Scaled semi offset{scaled_semi_offset}, Scaled radius {scaled_radius}, semi offset {semi_y_offset}, radius {radius}, scaled {scale}")
            scaled_outline = outline_width * scale
            
            # Step 1: Create shape with ALPHA CHANNEL at high resolution
            img_rgba = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img_rgba)
            
            # Draw filled shapes (with full opacity)
            draw.rectangle(
                [scaled_radius, 0, scaled_width + scaled_radius, img_height],
                fill=fill + (255,) if isinstance(fill, tuple) else fill,
                outline=None
            )
            
            draw.ellipse(
                [0, scaled_semi_offset,
                2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
                fill=fill + (255,) if isinstance(fill, tuple) else fill,
                outline=None
            )
            
            draw.ellipse(
                [scaled_width, scaled_semi_offset1,
                scaled_width + 2 * scaled_radius, scaled_semi_offset1 + 2 * scaled_radius],
                fill=fill + (255,) if isinstance(fill, tuple) else fill,
                outline=None
            )
            
            draw.ellipse(
                [scaled_width, scaled_semi_offset2,
                scaled_width + 2 * scaled_radius, scaled_semi_offset2 + 2 * scaled_radius],
                fill=fill + (255,) if isinstance(fill, tuple) else fill,
                outline=None
            )
            
            draw.ellipse(
                [0, scaled_semi_offset,
                2 * (scaled_radius-1), scaled_semi_offset + 2 * (scaled_radius-1)],
                fill='white',
                outline=None
            )
            
            draw.ellipse(
                [scaled_width, scaled_semi_offset1,
                scaled_width + 2 * (scaled_radius-1), scaled_semi_offset1 + 2 * (scaled_radius-1)],
                fill='red',
                outline=None
            )
            
            draw.ellipse(
                [scaled_width, scaled_semi_offset2,
                scaled_width + 2 * (scaled_radius-1), scaled_semi_offset2 + 2 * (scaled_radius-1)],
                fill='green',
                outline=None
            )
            
            try:
                font = ImageFont.truetype("arial.ttf", int(15 * scale))  # Adjust size as needed
            except:
                font = ImageFont.load_default()  # Fallback to default font
            
            text = "Timer"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Center the text on the image
            text_x = 60
            text_y = ((img_height - text_height) // 3)+3
            #print(f"Image height{img_height}, text height {text_height}") 
            draw.text((text_x, text_y), text, fill='black', font=font)
            
            
            # Draw outline with cheap antialiasing
            if outline:
                
                # Main outline pass
                draw.ellipse(
                    [0, scaled_semi_offset,
                    2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
                    outline=outline,
                    width=int(scaled_outline)
                )
                
                draw.ellipse(
                    [scaled_width, scaled_semi_offset1,
                    scaled_width + 2 * scaled_radius, scaled_semi_offset1 + 2 * scaled_radius],
                    outline=outline,
                    width=int(scaled_outline)
                )
                
                draw.ellipse(
                    [scaled_width, scaled_semi_offset2,
                    scaled_width + 2 * scaled_radius, scaled_semi_offset2 + 2 * scaled_radius],
                    outline=outline,
                    width=int(scaled_outline)
                )
                
                draw.line(
                    [scaled_radius, int(scaled_outline/2),
                    scaled_width + scaled_radius, int(scaled_outline/2)],
                    fill=outline,
                    width=int(scaled_outline)
                )
                
                draw.line(
                    [scaled_radius, img_height - int(scaled_outline/2),
                    scaled_width + scaled_radius, img_height - int(scaled_outline/2)],
                    fill=outline,
                    width=int(scaled_outline)
                )
            
            # Step 2: Resize WITH LANCZOS (shape will be smooth)
            img_rgba_resized = img_rgba.resize((int(total_width), int(height)), Image.LANCZOS)
            
            # Step 3: Convert alpha to binary (sharp edges) to prevent blending
            # This is the KEY - make alpha either 0 or 255, no in-between
            alpha = img_rgba_resized.split()[3]  # Get alpha channel
            alpha_data = alpha.load()
            
            # Convert semi-transparent pixels to either fully transparent or fully opaque
            threshold = 128  # Adjust if needed (0-255)
            for y in range(alpha.height):
                for x in range(alpha.width):
                    if alpha_data[x, y] < threshold:
                        alpha_data[x, y] = 0  # Fully transparent
                    else:
                        alpha_data[x, y] = 255  # Fully opaque
            
            # Step 4: Composite onto magenta background
            img_final = Image.new('RGB', (int(total_width), int(height)), (255, 0, 255))
            img_final.paste(img_rgba_resized, (0, 0), alpha)
            
            return ImageTk.PhotoImage(img_final)
    #MARK: - While creation
    def create_while(self, width=100, height=36, scale=3,
                        fill='yellow', outline='#000000',
                        outline_width=2, type='NONE'):
            """
            Create high-quality rounded rectangle with semicircular caps using PIL.
            Uses alpha masking to prevent edge bleeding while maintaining quality.
            """
            # Calculate dimensions
            radius = height / 10
            semi_y_offset = (height - 2 * radius) / 2
            semi_y_offset1 = (height - 2 * radius) / 4
            semi_y_offset2 = 3 * (height - 2 * radius) / 4
            total_width = width + 2 * radius
            
            # Scale up for high resolution rendering
            img_width = int(total_width * scale)
            img_height = int(height * scale)
            scaled_width = int(width * scale)
            scaled_radius = radius * scale
            scaled_semi_offset = semi_y_offset * scale
            scaled_semi_offset1 = semi_y_offset1 * scale
            scaled_semi_offset2 = semi_y_offset2 * scale
            #print(f"Scaled semi offset{scaled_semi_offset}, Scaled radius {scaled_radius}, semi offset {semi_y_offset}, radius {radius}, scaled {scale}")
            scaled_outline = outline_width * scale
            
            # Step 1: Create shape with ALPHA CHANNEL at high resolution
            img_rgba = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img_rgba)
            
            # Draw filled shapes (with full opacity)
            draw.rectangle(
                [scaled_radius, 0, scaled_width + scaled_radius, img_height],
                fill=fill + (255,) if isinstance(fill, tuple) else fill,
                outline=None
            )
            
            draw.ellipse(
                [0, scaled_semi_offset,
                2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
                fill=fill + (255,) if isinstance(fill, tuple) else fill,
                outline=None
            )
            
            draw.ellipse(
                [scaled_width, scaled_semi_offset1,
                scaled_width + 2 * scaled_radius, scaled_semi_offset1 + 2 * scaled_radius],
                fill=fill + (255,) if isinstance(fill, tuple) else fill,
                outline=None
            )
            
            draw.ellipse(
                [scaled_width, scaled_semi_offset2,
                scaled_width + 2 * scaled_radius, scaled_semi_offset2 + 2 * scaled_radius],
                fill=fill + (255,) if isinstance(fill, tuple) else fill,
                outline=None
            )
            
            draw.ellipse(
                [0, scaled_semi_offset,
                2 * (scaled_radius-1), scaled_semi_offset + 2 * (scaled_radius-1)],
                fill='white',
                outline=None
            )
            
            draw.ellipse(
                [scaled_width, scaled_semi_offset1,
                scaled_width + 2 * (scaled_radius-1), scaled_semi_offset1 + 2 * (scaled_radius-1)],
                fill='red',
                outline=None
            )
            
            draw.ellipse(
                [scaled_width, scaled_semi_offset2,
                scaled_width + 2 * (scaled_radius-1), scaled_semi_offset2 + 2 * (scaled_radius-1)],
                fill='green',
                outline=None
            )
            
            try:
                font = ImageFont.truetype("arial.ttf", int(15 * scale))  # Adjust size as needed
            except:
                font = ImageFont.load_default()  # Fallback to default font
            
            text = "Timer"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Center the text on the image
            text_x = 60
            text_y = ((img_height - text_height) // 3)+3
            #print(f"Image height{img_height}, text height {text_height}") 
            draw.text((text_x, text_y), text, fill='black', font=font)
            
            
            # Draw outline with cheap antialiasing
            if outline:
                
                # Main outline pass
                draw.ellipse(
                    [0, scaled_semi_offset,
                    2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
                    outline=outline,
                    width=int(scaled_outline)
                )
                
                draw.ellipse(
                    [scaled_width, scaled_semi_offset1,
                    scaled_width + 2 * scaled_radius, scaled_semi_offset1 + 2 * scaled_radius],
                    outline=outline,
                    width=int(scaled_outline)
                )
                
                draw.ellipse(
                    [scaled_width, scaled_semi_offset2,
                    scaled_width + 2 * scaled_radius, scaled_semi_offset2 + 2 * scaled_radius],
                    outline=outline,
                    width=int(scaled_outline)
                )
                
                draw.line(
                    [scaled_radius, int(scaled_outline/2),
                    scaled_width + scaled_radius, int(scaled_outline/2)],
                    fill=outline,
                    width=int(scaled_outline)
                )
                
                draw.line(
                    [scaled_radius, img_height - int(scaled_outline/2),
                    scaled_width + scaled_radius, img_height - int(scaled_outline/2)],
                    fill=outline,
                    width=int(scaled_outline)
                )
            
            # Step 2: Resize WITH LANCZOS (shape will be smooth)
            img_rgba_resized = img_rgba.resize((int(total_width), int(height)), Image.LANCZOS)
            
            # Step 3: Convert alpha to binary (sharp edges) to prevent blending
            # This is the KEY - make alpha either 0 or 255, no in-between
            alpha = img_rgba_resized.split()[3]  # Get alpha channel
            alpha_data = alpha.load()
            
            # Convert semi-transparent pixels to either fully transparent or fully opaque
            threshold = 128  # Adjust if needed (0-255)
            for y in range(alpha.height):
                for x in range(alpha.width):
                    if alpha_data[x, y] < threshold:
                        alpha_data[x, y] = 0  # Fully transparent
                    else:
                        alpha_data[x, y] = 255  # Fully opaque
            
            # Step 4: Composite onto magenta background
            img_final = Image.new('RGB', (int(total_width), int(height)), (255, 0, 255))
            img_final.paste(img_rgba_resized, (0, 0), alpha)
            
            return ImageTk.PhotoImage(img_final)