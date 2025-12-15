from Imports import (QWidget, QLabel, QLineEdit,
QComboBox, QApplication, QStyleOptionComboBox,
pyqtProperty, QEasingCurve, QRectF,
Qt, QPoint, QPropertyAnimation, QRect,
pyqtSignal, QObject, QRegularExpression,
QPainter, QPen, QBrush, QColor,
QPixmap, QImage, QMouseEvent, QStandardItem,
QIntValidator, QRegularExpressionValidator,
QPainterPath, QFont, QStyledItemDelegate, QSortFilterProxyModel,
QStandardItemModel, QListWidget, QEvent, ctypes, sys, time,
QGraphicsPixmapItem, QGraphicsItem, QPointF)
from PIL import Image, ImageDraw, ImageFont
import random
from Imports import get_utils
Utils = get_utils()

items = ["=", "!=", "<=", ">=", "<", ">"]

class BlockSignals(QObject):
    """Signal container for block interactions"""
    input_clicked = pyqtSignal(object, QPointF, str)  # block, center, type
    output_clicked = pyqtSignal(object, QPointF, str)  # block, center, type

class BlockGraphicsItem(QGraphicsPixmapItem, QObject):
    """Graphics item representing a block on the canvas - displays images"""
    
    def __init__(self, x, y, block_id, block_type, parent_canvas):
        # Create image ONCE before calling super().__init__()
        self.block_image = self._create_block_image(block_type)
        
        # Initialize with the pixmap
        super().__init__(self.block_image)
        self.signals = BlockSignals()
        self.block_id = block_id
        self.block_type = block_type
        self.canvas = parent_canvas
        self.block_widget = None
        self.radius = 7
        # Set position
        self.setPos(x, y)
        
        # Make draggable and selectable
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        
        print(f"✓ BlockGraphicsItem created: {block_id} ({block_type}) at ({x}, {y})")
    
    def connect_graphics_signals(self):
        """Connect graphics item circle click signals to event handler"""
        if self.block_id not in Utils.top_infos:
            return

        block_info = Utils.top_infos[self.block_id]
        block_graphics = block_info.get('widget')

        if block_graphics and hasattr(block_graphics, 'signals'):  # Check for signals object
            # Find the ElementsEvents instance
            if hasattr(self.canvas, 'elements_events'):
                events = self.canvas.elements_events
                # Connect signals from signals object
                try:
                    block_graphics.signals.input_clicked.connect(events.on_input_clicked)
                    block_graphics.signals.output_clicked.connect(events.on_output_clicked)
                except Exception as e:
                    print(f"Error connecting signals for {self.block_id}: {e}")
    
    def _create_block_image(self, block_type):
        """Create the block image ONCE - cached"""
        print(f"  → Creating image for {block_type}")
        
        if block_type == "Start":
            return self._create_start_end_image("Start", "#90EE90")
        elif block_type == "End":
            return self._create_start_end_image("End", "#FF6B6B")
        elif block_type == "Timer":
            return self._create_timer_image()
        elif block_type == "If":
            return self._create_if_image()
        elif block_type == "While":
            return self._create_while_image()
        elif block_type == "Switch":
            return self._create_switch_image()
        else:
            return self._create_start_end_image(block_type, "#FFD700")
    
    def _create_start_end_image(self, text, color, width=100, height=36, scale=3):
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
        
        # Draw filled rectangle
        draw.rectangle(
            [scaled_radius, 0, scaled_width + scaled_radius, img_height],
            fill=color + 'FF'
        )
        
        # Draw circles based on type
        if text == 'End':
            draw.ellipse(
                [0, scaled_semi_offset, 2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
                fill=color + 'FF'
            )
            draw.ellipse(
                [0, scaled_semi_offset, 2 * (scaled_radius-1), scaled_semi_offset + 2 * (scaled_radius-1)],
                fill='white'
            )
        
        if text == 'Start':
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
        
        # Convert to QPixmap - RETURN EARLY
        img_data = img_rgba_resized.tobytes("raw", "RGBA")
        qimage = QImage(img_data, int(total_width), height, QImage.Format.Format_RGBA8888)
        return QPixmap.fromImage(qimage)
    
    def _create_timer_image(self):
        """Create timer block image"""
        width = 140
        height = 36
        color = "#87CEEB"
        scale = 3
        text = "Timer"
        
        radius = height / 6
        semi_y_offset = (height - 2 * radius) / 2
        total_width = width + 2 * radius
        
        img_width = int(total_width * scale)
        img_height = int(height * scale)
        scaled_width = int(width * scale)
        scaled_radius = radius * scale
        scaled_semi_offset = semi_y_offset * scale
        scaled_outline = 2 * scale
        
        img_rgba = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img_rgba)
        
        draw.rectangle(
            [scaled_radius, 0, scaled_width + scaled_radius, img_height],
            fill=color + 'FF'
        )
        
        draw.ellipse(
            [0, scaled_semi_offset, 2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
            fill=color + 'FF'
        )
        draw.ellipse(
            [0, scaled_semi_offset, 2 * (scaled_radius-1), scaled_semi_offset + 2 * (scaled_radius-1)],
            fill='white'
        )
        
        draw.ellipse(
            [scaled_width, scaled_semi_offset, scaled_width + 2 * scaled_radius, scaled_semi_offset + 2 * scaled_radius],
            fill=color + 'FF'
        )
        draw.ellipse(
            [scaled_width, scaled_semi_offset, scaled_width + 2 * (scaled_radius-1), scaled_semi_offset + 2 * (scaled_radius-1)],
            fill='red'
        )
        
        try:
            font = ImageFont.truetype("arial.ttf", int(15 * scale))
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = scaled_radius + int(10 * scale)
        text_y = ((img_height - text_height) // 2)
        draw.text((text_x, text_y), text, fill='black', font=font)
        
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
        
        img_rgba_resized = img_rgba.resize((int(total_width), height), Image.LANCZOS)
        img_data = img_rgba_resized.tobytes("raw", "RGBA")
        qimage = QImage(img_data, int(total_width), height, QImage.Format.Format_RGBA8888)
        return QPixmap.fromImage(qimage)
    
    def _create_if_image(self):
        """Create If block image"""
        """Create if block image with 1 input and 2 outputs"""
        width = 100
        height = 54 # Double height for two outputs
        color = "#87CEEB"
        scale = 3
        
        radius = height / 10  # Adjusted for taller block
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
        input_y_offset = 3 * img_height / 4 - scaled_radius
        draw.ellipse(
            [0 ,input_y_offset , 2 * scaled_radius, input_y_offset + 2 * scaled_radius],
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
        text_y = (img_height - text_height) / 5
        
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
    
    def _create_while_image(self):
        """Create While block image"""
        """Create if block image with 1 input and 2 outputs"""
        width = 100
        height = 54 # Double height for two outputs
        color = "#87CEEB"
        scale = 3
        
        radius = height / 10  # Adjusted for taller block
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
        input_y_offset = 3 * img_height / 4 - scaled_radius
        draw.ellipse(
            [0 ,input_y_offset , 2 * scaled_radius, input_y_offset + 2 * scaled_radius],
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
        
        bbox = draw.textbbox((0, 0), "While", font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (img_width - text_width) / 2
        text_y = (img_height - text_height) / 5
        
        draw.text((text_x, text_y), "While", fill='black', font=font)
        
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
    def _create_switch_image(self):
        """Create Switch block image"""
        self.Switch_width = 100  # Increased width to accommodate input
        self.Switch_height = 54
        color = "#87CEEB"
        scale = 3
        
        radius = self.Switch_height / 10
        semi_y_offset = (self.Switch_height - 2 * radius) / 2
        total_width = self.Switch_width + 2 * radius
        
        # Scale for high resolution
        img_width = int(total_width * scale)
        img_height = int(self.Switch_height * scale)
        scaled_width = int(self.Switch_width * scale)
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
        input_y_offset = 3 * img_height / 4 - scaled_radius
        draw.ellipse(
            [0, input_y_offset, 2 * scaled_radius, input_y_offset + 2 * scaled_radius],
            fill=color + 'FF'
        )
        draw.ellipse(
            [0, input_y_offset, 2 * (scaled_radius-1), input_y_offset + 2 * (scaled_radius-1)],
            fill='white'
        )
        
        # Right red circle (output)
        output2_y_offset = 3 * img_height / 4 - scaled_radius
        draw.ellipse(
            [scaled_width, output2_y_offset, scaled_width + 2 * scaled_radius, output2_y_offset + 2 * scaled_radius],
            fill=color + 'FF'
        )
        draw.ellipse(
            [scaled_width, output2_y_offset, scaled_width + 2 * (scaled_radius-1), output2_y_offset + 2 * (scaled_radius-1)],
            fill='red'
        )
        
        # Draw "Timer" text on the left side
        try:
            font = ImageFont.truetype("arial.ttf", int(15 * scale))
            font2 = ImageFont.truetype("arial.ttf", int(11 * scale))
        except:
            font = ImageFont.load_default()
        
        
        
        bbox = draw.textbbox((0, 0), "Variable", font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (4*scale) + (10 * scale)
        text_y = ((img_height - text_height) // 4)
        draw.text((text_x, text_y), "Variable", fill='black', font=font)
        
        bbox_on = draw.textbbox((0, 0), "ON", font=font2 )
        on_width = bbox_on[2] - bbox_on[0]
        on_height = bbox_on[3] - bbox_on[1]
        on_x = (4*scale) + (10 * scale)
        on_y = (img_height - on_height) - 30
        print(f"ON text position: ({on_x}, {on_y})")
        draw.text((on_x, on_y), "ON", fill='black', font=font2)
        
        bbox_off = draw.textbbox((0, 0), "OFF", font=font2)
        off_width = bbox_off[2] - bbox_off[0]
        off_height = bbox_off[3] - bbox_off[1]
        off_x = scaled_width - off_width -(4*scale)
        off_y = (img_height - off_height) - 30
        draw.text((off_x, off_y), "OFF", fill='black', font=font2)
        
        # Draw outline
        draw.ellipse(
            [0, input_y_offset, 2 * scaled_radius, input_y_offset + 2 * scaled_radius],
            outline='black',
            width=int(scaled_outline)
        )
        draw.ellipse(
            [scaled_width, output2_y_offset, scaled_width + 2 * scaled_radius, output2_y_offset + 2 * scaled_radius],
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
        img_rgba_resized = img_rgba.resize((int(total_width), self.Switch_height), Image.LANCZOS)
        
        # Convert to QPixmap
        img_data = img_rgba_resized.tobytes("raw", "RGBA")
        qimage = QImage(img_data, int(total_width), self.Switch_height, QImage.Format.Format_RGBA8888)
        return QPixmap.fromImage(qimage)
    
    def itemChange(self, change, value):
        """Handle position/selection changes"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Update stored position in Utils
            pos = self.pos()
            if self.block_id in Utils.top_infos:
                Utils.top_infos[self.block_id]['x'] = pos.x()
                Utils.top_infos[self.block_id]['y'] = pos.y()
            
            # Update connected paths
            if hasattr(self.canvas, 'path_manager'):
                self.canvas.path_manager.update_paths_for_widget(self)
        
        return super().itemChange(change, value)
    
    def mousePressEvent(self, event):
        """Handle block selection"""
        self.setSelected(True)
        local_pos = event.pos()
        circle_type = self._check_click_on_circle(local_pos)
        print(f"Mouse press at {local_pos}, detected circle: {circle_type}")
        if circle_type:
            # Get circle center in scene coordinates
            circle_center = self._get_circle_center(circle_type)
            
            if isinstance(circle_center, tuple):
                circle_center = QPointF(circle_center[0], circle_center[1])
            if circle_type.startswith('in'):
                print(f"  → Input circle clicked: {circle_type} at {circle_center}")
                self.signals.input_clicked.emit(self, circle_center, circle_type)
            elif circle_type.startswith('out'):
                print(f"  → Output circle clicked: {circle_type} at {circle_center}")
                self.signals.output_clicked.emit(self, circle_center, circle_type)
        
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle block deselection"""
        self.setSelected(False)
        super().mouseReleaseEvent(event)
    
    def _get_circle_center(self, circle_type):
        """Get circle center in scene coordinates"""
        radius = self.radius
        block_width = self.boundingRect().width()
        block_height = self.boundingRect().height()
        
        if circle_type == 'in':
            local_x = radius
            local_y = block_height / 2
        elif circle_type == 'in1':
            local_x = radius
            local_y = 3 * (block_height / 4)
        elif circle_type == 'out':
            local_x = block_width - radius
            local_y = block_height / 2
        elif circle_type == 'out1':
            local_x = block_width - radius
            local_y = block_height / 4
        elif circle_type == 'out2':
            local_x = block_width - radius
            local_y = 3 * (block_height / 4)
        
        # Convert to scene coordinates
        scene_pos = self.mapToScene(local_x, local_y)
        return (scene_pos.x(), scene_pos.y())
    
    def _check_click_on_circle(self, click_pos, radius_margin=5):
        """
        Determine which circle (if any) was clicked
        
        Returns: 'in', 'out', 'in1', 'out1', 'out2', or None
        """
        radius = self.radius
        effective_radius = radius + radius_margin
        block_height = self.boundingRect().height()
        block_width = self.boundingRect().width()
        
        # Check input circles
        if self.block_type in ('If', 'While'):
            # One input at 3/4 height
            in_x, in_y = radius, 3 * (block_height / 4)
            dist_in = ((click_pos.x() - in_x)**2 + (click_pos.y() - in_y)**2)**0.5
            if dist_in <= effective_radius:
                return 'in1'
        elif self.block_type == 'Switch':
            # One input at 3/4 height
            in_x, in_y = radius, 3 * (block_height / 4)
            dist_in = ((click_pos.x() - in_x)**2 + (click_pos.y() - in_y)**2)**0.5
            if dist_in <= effective_radius:
                return 'in1'
        else:
            # Standard input at center height
            in_x, in_y = radius, block_height / 2
            dist_in = ((click_pos.x() - in_x)**2 + (click_pos.y() - in_y)**2)**0.5
            if dist_in <= effective_radius:
                return 'in'
        
        # Check output circles
        out_x = block_width - radius
        
        if self.block_type in ('If', 'While'):
            # Two output circles
            out_y1 = block_height / 4
            out_y2 = 3 * (block_height / 4)
            dist_out1 = ((click_pos.x() - out_x)**2 + (click_pos.y() - out_y1)**2)**0.5
            dist_out2 = ((click_pos.x() - out_x)**2 + (click_pos.y() - out_y2)**2)**0.5
            
            if dist_out1 <= effective_radius:
                return 'out1'
            if dist_out2 <= effective_radius:
                return 'out2'
        elif self.block_type == 'Switch':
            # One output at 3/4 height
            out_y = 3 * (block_height / 4)
            dist_out = ((click_pos.x() - out_x)**2 + (click_pos.y() - out_y)**2)**0.5
            if dist_out <= effective_radius:
                return 'out2'
        else:
            # Standard output at center height
            out_y = block_height / 2
            dist_out = ((click_pos.x() - out_x)**2 + (click_pos.y() - out_y)**2)**0.5
            if dist_out <= effective_radius:
                return 'out'
        
        return None
    
    def contextMenuEvent(self, event):
        """Handle right-click context menu"""
        scene_pos = event.scenePos()
        self.canvas.show_block_context_menu(self, scene_pos)
        super().contextMenuEvent(event)

class PassiveListPopup(QListWidget):
    """
    A list widget designed to float as a tool window without stealing focus.
    """
    selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        # 1. Window Flags: Tool (no taskbar) + Frameless + Always on Top
        self.setWindowFlags(
            Qt.WindowType.Tool | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # 2. Attribute: Tell Qt NOT to activate this window when showing it
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # 3. Focus Policy: logical focus should never be here
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Styling
        self.setStyleSheet("""
            QListWidget { 
                border: 1px solid gray; 
                background: white; 
                font-size: 10px;
                color: #000000;
            }
            QListWidget::item:selected { 
                background: #0078d7; 
                color: white; 
            }
            QScrollBar:horizontal {
                height: 0px;
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                width: 0px;
                border: none;
                background: transparent;
            }
        """)
        
        # Handle item clicks
        self.itemClicked.connect(self._on_item_clicked)
        
        # Install global filter to handle clicking outside
        QApplication.instance().installEventFilter(self)

    def showEvent(self, event):
        # Windows-specific fix to prevent activation on click
        if sys.platform == "win32":
            self._apply_windows_no_activate()
        super().showEvent(event)

    def _apply_windows_no_activate(self):
        # Set WS_EX_NOACTIVATE (0x08000000)
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        try:
            hwnd = int(self.winId())
            user32 = ctypes.windll.user32
            # Handle 64-bit vs 32-bit API naming
            set_window_long = user32.SetWindowLongPtrW if hasattr(user32, "SetWindowLongPtrW") else user32.SetWindowLongW
            get_window_long = user32.GetWindowLongPtrW if hasattr(user32, "GetWindowLongPtrW") else user32.GetWindowLongW
            
            ex_style = get_window_long(hwnd, GWL_EXSTYLE)
            set_window_long(hwnd, GWL_EXSTYLE, ex_style | WS_EX_NOACTIVATE)
        except Exception:
            pass

    def eventFilter(self, source, event):
        # Close popup if user clicks anywhere else
        if self.isVisible() and event.type() == QEvent.Type.MouseButtonPress:
            global_pos = event.globalPosition().toPoint()
            # If click is NOT inside the popup, close it.
            # Note: We don't check the LineEdit here because the LineEdit will 
            # likely have its own logic or just keep focus naturally.
            if not self.geometry().contains(global_pos):
                self.hide()
        return super().eventFilter(source, event)

    def _on_item_clicked(self, item):
        self.selected.emit(item.text())
        self.hide()


class SearchableLineEdit(QLineEdit):
    """
    A QLineEdit that mimics a ComboBox. 
    It manages a passive popup list that filters based on input.
    """
    
    selected = pyqtSignal(str)
    MAX_WIDTH = 150
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.popup = PassiveListPopup()
        self.popup.selected.connect(self.set_text_and_hide)
        
        self.setStyleSheet("""
        QLineEdit {
            background-color: white;
            border: 1px solid #333;
            border-radius: 3px;
            font-size: 10px;
            color: #333;
        }
        """)
        self.all_items = []
        
        # Connect typing events
        self.textEdited.connect(self.update_popup)
        
        self.setFixedWidth(30)

    def addItem(self, text):
        self.all_items.append(str(text))

    def addItems(self, texts):
        self.all_items.clear()
        self.all_items.extend([str(t) for t in texts])
        print(f"All items added: {self.all_items}")

    def set_text_and_hide(self, text):
        self.setText(text)
        self.popup.hide()

    def update_popup(self, text):
        """Filter items and show popup."""
        self.popup.clear()
        
        if not text:
            self.popup.hide()
            return

        # Simple case-insensitive filter
        filtered = [item for item in self.all_items if text.lower() in item.lower()]
        
        if not filtered:
            self.popup.hide()
            return

        self.popup.addItems(filtered)
        
        # Select the first item by default for easy navigation
        self.popup.setCurrentRow(0)
        
        # Position the popup
        self._move_popup()
        self.popup.show()

    def _move_popup(self):
        """Align popup geometry to the bottom of the line edit."""
        rect = self.rect()
        bottomleft = self.mapToGlobal(rect.bottomLeft())
        
        # Calculate popup width based on content (max 150px)
        fm = self.fontMetrics()
        max_text_width = 0
        for item_text in range(self.popup.count()):
            item = self.popup.item(item_text)
            if item:
                w = fm.horizontalAdvance(item.text())
                max_text_width = max(max_text_width, w)
        
        # Add padding and cap at max width
        popup_width = min(max_text_width + 20, self.MAX_WIDTH)
        popup_width = max(popup_width, 30)  # Minimum 30px
        
        self.popup.setFixedWidth(popup_width)  # ← Now dynamic!
        
        itemheight = self.popup.sizeHintForRow(0)
        print(f"Item height: {itemheight}")
        count = self.popup.count()
        print(f"Item count: {count}")
        h = min(count * itemheight, itemheight * 5)  # Max 5 items visible
        print(f"Popup height: {h}")
        self.popup.setFixedHeight(h)
        self.popup.updateGeometry()
        self.popup.move(bottomleft)
        
    def keyPressEvent(self, event):
        """Forward navigation keys to the popup."""
        if not self.popup.isVisible():
            super().keyPressEvent(event)
            return

        if event.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up):
            # Forward arrow keys to list
            current_row = self.popup.currentRow()
            count = self.popup.count()
            
            if event.key() == Qt.Key.Key_Down:
                new_row = (current_row + 1) % count
            else:
                new_row = (current_row - 1 + count) % count
                
            self.popup.setCurrentRow(new_row)
            return
        
        elif event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            # Select current item on Enter
            if self.popup.currentItem():
                self.set_text_and_hide(self.popup.currentItem().text())
            return
        
        elif event.key() == Qt.Key.Key_Escape:
            self.popup.hide()
            return

        super().keyPressEvent(event)


class CustomSwitch(QWidget):
    """
    YOUR CustomSwitch - Has FULL control over circle size!
    """
    
    toggled = pyqtSignal(bool)
    clicked = pyqtSignal(bool)
    
    def __init__(self, parent=None, 
                 width=80, height=40,
                 bg_off_color="#e0e0e0",
                 bg_on_color="#4CAF50",
                 circle_color="#ffffff",
                 border_color="#999999",
                 animation_speed=300):
        super().__init__(parent)
        
        # State management
        self._is_checked = False
        self._circle_x = 0.0
        self._is_enabled = True
        
        # Size configuration - YOU CONTROL CIRCLE SIZE HERE!
        self.base_width = width
        self.base_height = height
        self.circle_diameter = height - 8  # <-- CIRCLE SIZE DEPENDS ON HEIGHT!
        self.padding = 4
        self.border_width = 2
        
        # Color configuration
        self.bg_off_color = bg_off_color
        self.bg_on_color = bg_on_color
        self.circle_color = circle_color
        self.border_color = border_color
        self.disabled_alpha = 0.5
        
        # Animation setup
        self.animation = QPropertyAnimation(self, b"circle_x")
        self.animation.setDuration(animation_speed)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._is_animating = False
        self.animation.stateChanged.connect(self.animation_state_changed)
        
        # Widget configuration
        self.setFixedSize(self.base_width, self.base_height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Initialize circle position
        self._update_circle_position(animate=False)
    
    @pyqtProperty(float)
    def circle_x(self):
        return self._circle_x
    
    @circle_x.setter
    def circle_x(self, value):
        self._circle_x = value
        self.update()
    
    def animation_state_changed(self, state):
        from PyQt6.QtCore import QAbstractAnimation
    
        if state == QAbstractAnimation.State.Running:
            self._is_animating = True
        else:  # Stopped
            self._is_animating = False

    
    def on_switch_changed(self):
        return self._is_checked
    
    def set_checked(self, state, emit_signal=True):
        if self._is_checked != state:
            self._is_checked = state
            self._update_circle_position(animate=True)
            if emit_signal:
                self.toggled.emit(self._is_checked)
            self.clicked.emit(self._is_checked)
    
    def toggle(self):
        self.set_checked(not self._is_checked)
    
    def set_enabled_custom(self, enabled):
        self._is_enabled = enabled
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if enabled 
            else Qt.CursorShape.ForbiddenCursor
        )
        self.update()
    
    def _update_circle_position(self, animate=True):
        if self._is_checked:
            end_pos = self.base_width - self.circle_diameter - self.padding
        else:
            end_pos = self.padding
        
        if animate:
            self.animation.setStartValue(self._circle_x)
            self.animation.setEndValue(end_pos)
            self.animation.start()
        else:
            self._circle_x = end_pos
    
    def mousePressEvent(self, event):
        if self._is_animating:
            event.ignore()
            return
        
        if event.button() == Qt.MouseButton.LeftButton and self._is_enabled:
            self.toggle()
    
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.update()
    
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self._is_enabled:
            painter.setOpacity(self.disabled_alpha)
        
        radius = self.base_height / 2
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.base_width, self.base_height, radius, radius)
        painter.setClipPath(path)

        # 2) BACKGROUND: USE SAME OUTER RECT (NO INSET)
        bg_rect = QRectF(0, 0, self.base_width, self.base_height)
        bg_color = QColor(self.bg_on_color if self._is_checked else self.bg_off_color)
        painter.fillRect(bg_rect, bg_color)

        # 3) BORDER: DRAW ON SAME RECT & RADIUS
        border_pen = QPen(QColor(self.border_color), self.border_width)
        painter.setPen(border_pen)
        painter.drawRoundedRect(bg_rect, radius, radius)

        # 4) FOCUS RECT: SLIGHTLY INSET, SAME SHAPE
        if self.hasFocus():
            focus_pen = QPen(QColor("#2196f3"), 2, Qt.PenStyle.SolidLine)
            painter.setPen(focus_pen)
            focus_margin = 2
            focus_rect = QRectF(
                focus_margin,
                focus_margin,
                self.base_width - 2 * focus_margin,
                self.base_height - 2 * focus_margin,
            )
            painter.drawRoundedRect(focus_rect, radius - focus_margin, radius - focus_margin)

        # 5) CIRCLE
        circle_rect = QRectF(
            self._circle_x,
            self.padding,
            self.circle_diameter,
            self.circle_diameter,
        )
        painter.setBrush(QBrush(QColor(self.circle_color)))
        painter.setPen(QPen(QColor("#cccccc"), 1))
        painter.drawEllipse(circle_rect)

        shadow_pen = QPen(QColor("#000000"), 1)
        shadow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(shadow_pen)
        painter.setOpacity(0.15)
        painter.drawEllipse(circle_rect.adjusted(1, 1, 1, 1))


class NoTruncateDelegate(QStyledItemDelegate):
    """Delegate that prevents text truncation"""
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        # Make the item wider
        size.setWidth(size.width() + 50)
        return size
    def paint(self, painter, option, index):
        # Use the parent's paint method to maintain original styling
        super().paint(painter, option, index)
        # The parent handles color preservation

class MaxWidthComboBox(QComboBox):
    def __init__(self, parent=None, max_popup_width=300, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._max_popup_width = max_popup_width
        self.setStyleSheet("""
            QComboBox::drop-down { width: 0px; border: none; }
            QComboBox::down-arrow { width: 0px; image: none; }
        """)

    def showPopup(self):
        super().showPopup()

        view = self.view()
        popup = view.parentWidget()   # usually the QFrame that draws the background

        # 1) Compute desired width based on contents
        fm = view.fontMetrics()
        max_text_width = 0
        for row in range(self.model().rowCount()):
            index = self.model().index(row, self.modelColumn())
            text = index.data()
            if text is None:
                continue
            w = fm.horizontalAdvance(str(text))
            max_text_width = max(max_text_width, w)

        # small padding for margins
        desired = max_text_width + 30
        desired = min(desired, self._max_popup_width)

        # 2) Apply to view (for text)
        view.setFixedWidth(desired)

        # 3) Apply to popup frame (for background)
        if popup is not None:
            geo = popup.geometry()
            geo.setWidth(desired)
            popup.setGeometry(geo)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Open dropdown if clicked anywhere on the widget"""
        if self.rect().contains(event.pos()):
            self.showPopup()
        else:
            super().mousePressEvent(event)

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

        print(f"Before: {self.parent.mousePressEvent}")
        self.old_mousePressEvent = parent.mousePressEvent
        parent.mousePressEvent = self.on_mouse_press
        print(f"After: {self.parent.mousePressEvent}")
        parent.setFocus()
        print(f"Canvas enabled: {parent.isEnabled()}")
        print(f"Canvas transparent for mouse: {parent.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)}")
        print(f"Canvas focus: {parent.hasFocus()}")
        parent.raise_()
        print("Canvas raised to top")
        
        
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
            print("Perm stop avtivated")
            return
        
        print(f"Checking placing: perm_stop={self.perm_stop}, placing_active={self.placing_active}")
        
        if not self.element_placed and self.placing_active:
            self.element_spawner.custom_shape_spawn(parent, self.type, event)
            self.placing_active = False
            self.element_placed = True
            print(f"After check_placing: placing_active={self.placing_active}, element_placed={self.element_placed}")

    
    def stop_placing(self, parent):
        """Stop placement mode"""
        print("Placement stopped")
        self.perm_stop = True
        self.placing_active = False
        self.element_placed = False
        
        # Restore normal mouse handling
        parent.mousePressEvent = self.old_mousePressEvent
        # Show elements window again
        if self.elements_window:
            self.elements_window.is_hidden = False
            self.elements_window.open()
    
#MARK: Elements_events
class Elements_events(QObject):
    """Centralized event handler for block interactions"""
    
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.path_manager = canvas.path_manager if hasattr(canvas, 'path_manager') else None
        
        print("✓ ElementsEvents initialized")
        print(f"  → path_manager: {self.path_manager}")
    
    def on_input_clicked(self, block, circle_center, circle_type):
        """Handle input circle clicks"""
        print(f"✓ on_input_clicked: {block.block_id} ({circle_type})")
        
        if self.path_manager:
            self.path_manager.finalize_connection(block, circle_center, circle_type)
    
    def on_output_clicked(self, block, circle_center, circle_type):
        """Handle output circle clicks"""
        print(f"✓ on_output_clicked: {block.block_id} ({circle_type})")
        
        if self.path_manager:
            self.path_manager.start_connection(block, circle_center, circle_type)


class Element_spawn:
    """Spawns visual elements"""
    
    height = 36
    
    def custom_shape_spawn(self, parent, element_type, event):
        """Spawn a custom shape at the clicked position"""
        # Generate unique ID
        block_id = f"{element_type}_{int(time.time() * 1000)}"
        
        Utils.top_infos[block_id] = {
            'widget': None,  # Will set after block created
            'id': block_id,
            'type': element_type,
            'x': 0, 'y': 0,  # Will update after positioning
            'width': 0, 'height': 0,
            'in_connections': [],
            'out_connections': [],
            'value_1': '--',  # Default values
            'value_1_type': '',
            'value_2': '',
            'value_2_type': '',
            'combo_value': '=',
            'switch_value': 'True',
        }
        
        # Create block widget
        block_id = f"{element_type}_{int(time.time() * 1000)}"
    
        # Get mouse position from canvas
        scene_pos = parent.mapToScene(event.pos())
        x, y = scene_pos.x(), scene_pos.y()
        
        # Create graphics item block
        block_graphics = parent.add_block(element_type, x, y, block_id)
        
        print(f"Spawned {element_type} at ({x}, {y})")