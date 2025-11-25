from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QImage
from PIL import Image, ImageDraw, ImageFont
import random
import Utils


class spawning_elements:
    """Handles spawning and placing elements on the canvas"""
    
    def __init__(self, parent):
        self.placing_active = False
        self.perm_stop = False
        self.element_placed = False
        self.parent = parent
        self.elements_window = None
        self.element_spawner = Element_spawn()
    
    def start(self, parent, element_type):
        """Start placing an element"""
        self.type = element_type
        self.perm_stop = False
        print("Start placement")
        
        # Hide elements window
        if self.elements_window and self.elements_window.isVisible():
            self.elements_window.is_hidden = True
            self.elements_window.hide()
        
        # Connect mouse click to place element
        self.parent.mousePressEvent = self.on_mouse_press
        
    def on_mouse_press(self, event):
        print("Mouse Pressed")
        """Handle mouse press for placing element"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.place(event)
    
    def place(self, event):
        """Place the element at clicked position"""
        print("Placement started")
        self.placing_active = True
        self.element_placed = False
        self.check_placing(self.parent, event)
    
    def check_placing(self, parent, event):
        """Check and place element"""
        if self.perm_stop:
            return
        
        print(f"Checking placing: perm_stop={self.perm_stop}, placing_active={self.placing_active}")
        
        if not self.element_placed and self.placing_active:
            self.element_spawner.custom_shape_spawn(parent, self.type, event)
            self.placing_active = False
            self.element_placed = True
            self.stop_placing(parent)
    
    def stop_placing(self, parent):
        """Stop placement mode"""
        print("Placement stopped")
        self.perm_stop = True
        self.placing_active = False
        self.element_placed = False
        
        # Restore normal mouse handling
        parent.mousePressEvent = lambda e: None
        
        # Show elements window again
        if self.elements_window:
            self.elements_window.is_hidden = False
            self.elements_window.open()


class BlockWidget(QWidget):
    """Custom widget for visual programming blocks"""
    
    def __init__(self, parent, block_type, block_id):
        super().__init__(parent)
        self.block_type = block_type
        self.block_id = block_id
        self.canvas = parent
        
        # Generate image
        self.image = self.create_block_image()
        
        # Set size
        self.setFixedSize(self.image.width(), self.image.height())
        
        # Make transparent for non-rectangular shapes
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Add number input for timer blocks
        self.number_input = None
        if self.block_type == "Timer":
            self.create_timer_input()
    
    def create_timer_input(self):
        """Create number input field for timer block"""
        self.number_input = QLineEdit(self)
        self.number_input.setFixedSize(50, 20)
        
        # Position the input in the middle-right area of the block
        input_x = self.width() - 65  # 15px from right edge
        input_y = (self.height() - 20) // 2  # Center vertically
        self.number_input.move(input_x, input_y)
        
        # Style the input
        self.number_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #333;
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 12px;
                color: #333;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        
        # Set validator for numbers only
        self.number_input.setPlaceholderText("0")
        self.number_input.setText("1")
        
        # Ensure input stays on top
        self.number_input.raise_()
        self.number_input.show()
        
        # Store the value when changed
        self.number_input.textChanged.connect(self.on_timer_value_changed)
    
    def on_timer_value_changed(self, text):
        """Handle timer value changes"""
        # Store in Utils for later use
        if self.block_id in Utils.top_infos:
            Utils.top_infos[self.block_id]['timer_value'] = text
        print(f"Timer {self.block_id} value changed to: {text}")
    
    def create_block_image(self):
        """Create the block image using PIL"""
        if self.block_type == "Start":
            return self.create_start_end_image("Start", "#90EE90")
        elif self.block_type == "End":
            return self.create_start_end_image("End", "#FF6B6B")
        elif self.block_type == "Timer":
            return self.create_timer_image()
        elif self.block_type == "If":
            return self.create_if_image()
        else:
            return self.create_start_end_image(self.block_type, "#FFD700")
    
    def create_start_end_image(self, text, color, width=100, height=36, scale=3):
        """Create rounded rectangle with semicircular caps"""
        radius = height / 6
        semi_y_offset = (height - 2 * radius) / 2
        total_width = width + 2 * radius
        
        # Scale for high resolution
        img_width = int(total_width * scale)
        img_height = int(height * scale)
        scaled_width = int(width * scale)
        scaled_radius = radius * scale
        scaled_semi_offset = semi_y_offset * scale
        scaled_outline = 2 * scale
        
        # Create RGBA image
        img_rgba = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img_rgba)
        
        # Draw filled shapes
        draw.rectangle(
            [scaled_radius, 0, scaled_width + scaled_radius, img_height],
            fill=color + 'FF'
        )
        
        # Draw circles based on type
        if text == 'End':
            # Left white circle
            draw.ellipse(
                [0, scaled_semi_offset, 2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
                fill=color + 'FF'
            )
            draw.ellipse(
                [0, scaled_semi_offset, 2 * (scaled_radius-1), scaled_semi_offset + 2 * (scaled_radius-1)],
                fill='white'
            )
        
        if text == 'Start':
            # Right red circle
            draw.ellipse(
                [scaled_width, scaled_semi_offset, scaled_width + 2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
                fill=color + 'FF'
            )
            draw.ellipse(
                [scaled_width, scaled_semi_offset, scaled_width + 2 * (scaled_radius-1), scaled_semi_offset + 2 * (scaled_radius-1)],
                fill='red'
            )
        
        # Draw text
        try:
            font = ImageFont.truetype("arial.ttf", int(15 * scale))
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (img_width - text_width) // 2
        text_y = ((img_height - text_height) // 3) + 3
        draw.text((text_x, text_y), text, fill='black', font=font)
        
        # Draw outline
        if text == 'End':
            draw.ellipse(
                [0, scaled_semi_offset, 2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
                outline='black',
                width=int(scaled_outline)
            )
        if text == 'Start':
            draw.ellipse(
                [scaled_width, scaled_semi_offset, scaled_width + 2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
                outline='black',
                width=int(scaled_outline)
            )
        
        draw.line(
            [scaled_radius, int(scaled_outline/2), scaled_width + scaled_radius, int(scaled_outline/2)],
            fill='black',
            width=int(scaled_outline)
        )
        draw.line(
            [scaled_radius, img_height - int(scaled_outline/2), scaled_width + scaled_radius, img_height - int(scaled_outline/2)],
            fill='black',
            width=int(scaled_outline)
        )
        
        # Resize with antialiasing
        img_rgba_resized = img_rgba.resize((int(total_width), height), Image.LANCZOS)
        
        # Convert to QPixmap
        img_data = img_rgba_resized.tobytes("raw", "RGBA")
        qimage = QImage(img_data, int(total_width), height, QImage.Format.Format_RGBA8888)
        
        return QPixmap.fromImage(qimage)
    
    def create_timer_image(self):
        """Create timer block image with space for number input"""
        width = 140  # Increased width to accommodate input
        height = 36
        color = "#87CEEB"
        scale = 3
        text = "Timer"
        
        radius = height / 6
        semi_y_offset = (height - 2 * radius) / 2
        total_width = width + 2 * radius
        
        # Scale for high resolution
        img_width = int(total_width * scale)
        img_height = int(height * scale)
        scaled_width = int(width * scale)
        scaled_radius = radius * scale
        scaled_semi_offset = semi_y_offset * scale
        scaled_outline = 2 * scale
        
        # Create RGBA image
        img_rgba = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img_rgba)
        
        # Draw filled rectangle
        draw.rectangle(
            [scaled_radius, 0, scaled_width + scaled_radius, img_height],
            fill=color + 'FF'
        )
        
        # Left white circle (input)
        draw.ellipse(
            [0, scaled_semi_offset, 2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
            fill=color + 'FF'
        )
        draw.ellipse(
            [0, scaled_semi_offset, 2 * (scaled_radius-1), scaled_semi_offset + 2 * (scaled_radius-1)],
            fill='white'
        )
        
        # Right red circle (output)
        draw.ellipse(
            [scaled_width, scaled_semi_offset, scaled_width + 2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
            fill=color + 'FF'
        )
        draw.ellipse(
            [scaled_width, scaled_semi_offset, scaled_width + 2 * (scaled_radius-1), scaled_semi_offset + 2 * (scaled_radius-1)],
            fill='red'
        )
        
        # Draw "Timer" text on the left side
        try:
            font = ImageFont.truetype("arial.ttf", int(15 * scale))
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Position text on left side
        text_x = scaled_radius + int(10 * scale)
        text_y = ((img_height - text_height) // 2)
        draw.text((text_x, text_y), text, fill='black', font=font)
        
        # Draw outline
        draw.ellipse(
            [0, scaled_semi_offset, 2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
            outline='black',
            width=int(scaled_outline)
        )
        draw.ellipse(
            [scaled_width, scaled_semi_offset, scaled_width + 2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
            outline='black',
            width=int(scaled_outline)
        )
        draw.line(
            [scaled_radius, int(scaled_outline/2), scaled_width + scaled_radius, int(scaled_outline/2)],
            fill='black',
            width=int(scaled_outline)
        )
        draw.line(
            [scaled_radius, img_height - int(scaled_outline/2), scaled_width + scaled_radius, img_height - int(scaled_outline/2)],
            fill='black',
            width=int(scaled_outline)
        )
        
        # Resize with antialiasing
        img_rgba_resized = img_rgba.resize((int(total_width), height), Image.LANCZOS)
        
        # Convert to QPixmap
        img_data = img_rgba_resized.tobytes("raw", "RGBA")
        qimage = QImage(img_data, int(total_width), height, QImage.Format.Format_RGBA8888)
        return QPixmap.fromImage(qimage)
    
    def create_if_image(self):
        """Create if block image with 1 input and 2 outputs"""
        width = 100
        height = 72  # Double height for two outputs
        color = "#87CEEB"
        scale = 3
        
        radius = height / 12  # Adjusted for taller block
        total_width = width + 2 * radius
        
        # Scale for high resolution
        img_width = int(total_width * scale)
        img_height = int(height * scale)
        scaled_width = int(width * scale)
        scaled_radius = radius * scale
        scaled_outline = 2 * scale
        
        # Create RGBA image
        img_rgba = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img_rgba)
        
        # Draw main rectangle
        draw.rectangle(
            [scaled_radius, 0, scaled_width + scaled_radius, img_height],
            fill=color + 'FF'
        )
        
        # Left input circle (centered vertically)
        input_y_offset = (img_height - 2 * scaled_radius) / 2
        draw.ellipse(
            [0, input_y_offset, 2 * scaled_radius, input_y_offset + 2 * scaled_radius],
            fill=color + 'FF'
        )
        draw.ellipse(
            [0, input_y_offset, 2 * (scaled_radius-1), input_y_offset + 2 * (scaled_radius-1)],
            fill='white'
        )
        
        # Right output circle 1 (at 1/4 height)
        output1_y_offset = img_height / 4 - scaled_radius
        draw.ellipse(
            [scaled_width, output1_y_offset, scaled_width + 2 * scaled_radius, output1_y_offset + 2 * scaled_radius],
            fill=color + 'FF'
        )
        draw.ellipse(
            [scaled_width, output1_y_offset, scaled_width + 2 * (scaled_radius-1), output1_y_offset + 2 * (scaled_radius-1)],
            fill='red'
        )
        
        # Right output circle 2 (at 3/4 height)
        output2_y_offset = 3 * img_height / 4 - scaled_radius
        draw.ellipse(
            [scaled_width, output2_y_offset, scaled_width + 2 * scaled_radius, output2_y_offset + 2 * scaled_radius],
            fill=color + 'FF'
        )
        draw.ellipse(
            [scaled_width, output2_y_offset, scaled_width + 2 * (scaled_radius-1), output2_y_offset + 2 * (scaled_radius-1)],
            fill='red'
        )
        
        # Draw text
        try:
            font = ImageFont.truetype("arial.ttf", int(15 * scale))
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), "If", font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (img_width - text_width) / 2
        text_y = (img_height - text_height) / 2
        
        draw.text((text_x, text_y), "If", fill='black', font=font)
        
        # Draw outline
        draw.line(
            [scaled_radius, int(scaled_outline/2), scaled_width + scaled_radius, int(scaled_outline/2)],
            fill='black',
            width=int(scaled_outline)
        )
        draw.line(
            [scaled_radius, img_height - int(scaled_outline/2), scaled_width + scaled_radius, img_height - int(scaled_outline/2)],
            fill='black',
            width=int(scaled_outline)
        )
        
        draw.ellipse(
            [0, input_y_offset, 2 * scaled_radius, input_y_offset + 2 * scaled_radius],
            outline='black',
            width=int(scaled_outline)
        )
        draw.ellipse(
            [scaled_width, output1_y_offset, scaled_width + 2 * scaled_radius, output1_y_offset + 2 * scaled_radius],
            outline='black',
            width=int(scaled_outline)
        )
        draw.ellipse(
            [scaled_width, output2_y_offset, scaled_width + 2 * scaled_radius, output2_y_offset + 2 * scaled_radius],
            outline='black',
            width=int(scaled_outline)
        )
        
        # Downscale for final image
        img_rgba_resized = img_rgba.resize((int(total_width), height), Image.LANCZOS)
        
        # Convert to QPixmap
        img_data = img_rgba_resized.tobytes("raw", "RGBA")
        qimage = QImage(img_data, int(total_width), height, QImage.Format.Format_RGBA8888)
        
        return QPixmap.fromImage(qimage)
      
    def paintEvent(self, event):
        """Draw the block"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(0, 0, self.image)
    
    def mousePressEvent(self, event):
        """Handle mouse press on block"""
        # Check if clicked on connection circles
        if self.is_click_on_circle(event.pos()):
            self.handle_circle_click(event)
        else:
            # Let parent handle dragging
            super().mousePressEvent(event)
    
    def is_click_on_circle(self, pos):
        """Check if click is on a connection circle"""
        radius = self.height() / 5
        
        # Check input circle (left)
        in_x = radius
        in_y = self.height() / 2
        if (pos.x() - in_x) ** 2 + (pos.y() - in_y) ** 2 <= radius ** 2:
            return True
        
        # Check output circle(s) (right)
        out_x = self.width() - radius
        out_y = self.height() / 2
        if (pos.x() - out_x) ** 2 + (pos.y() - out_y) ** 2 <= radius ** 2:
            return True
        
        return False
    
    def handle_circle_click(self, event):
        """Handle click on connection circle"""
        radius = self.height() / 5
        pos = event.pos()
        
        # Determine which circle was clicked
        in_x = radius
        in_y = self.height() / 2
        
        if (pos.x() - in_x) ** 2 + (pos.y() - in_y) ** 2 <= radius ** 2:
            # Input circle clicked - finalize connection
            circle_center = (self.x() + in_x, self.y() + in_y)
            self.canvas.path_manager.finalize_connection(self, circle_center, 'in')
        else:
            # Output circle clicked - start connection
            out_x = self.width() - radius
            out_y = self.height() / 2
            circle_center = (self.x() + out_x, self.y() + out_y)
            self.canvas.path_manager.start_connection(self, circle_center, 'out')


class Element_spawn:
    """Spawns visual elements"""
    
    height = 36
    
    def custom_shape_spawn(self, parent, element_type, event):
        """Spawn a custom shape at the clicked position"""
        # Generate unique ID
        block_id = random.randint(10000, 99999)
        
        # Create block widget
        block = BlockWidget(parent, element_type, block_id)
        
        # Position at click location
        click_pos = event.pos()
        x, y = parent.snap_to_grid(click_pos.x(), click_pos.y(), block, during_drag=False)
        block.move(x, y)
        
        # Add to canvas
        parent.add_draggable_widget(block)
        
        # Store in Utils
        Utils.top_infos[block_id] = {
            'widget': block,
            'id': block_id,
            'type': element_type,
            'x': x,
            'y': y,
            'width': block.width(),
            'height': block.height(),
            'in_connections': [],
            'out_connections': []
        }
        
        print(f"Created block: {element_type} at ({x}, {y})")
