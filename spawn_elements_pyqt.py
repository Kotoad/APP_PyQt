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

class BlockSignals(QObject):
    """Signal container for block interactions"""
    input_clicked = pyqtSignal(object, QPointF, str)  # block, center, type
    output_clicked = pyqtSignal(object, QPointF, str)  # block, center, type


class BlockGraphicsItem(QGraphicsItem, QObject):
    """Graphics item representing a block - renders with QPainter for perfect zoom quality"""

    def __init__(self, x, y, block_id, block_type, parent_canvas):
        super().__init__()
        
        self.signals = BlockSignals()
        self.block_id = block_id
        self.block_type = block_type
        self.canvas = parent_canvas
        
        self.value_1_name = "var1"
        self.operator = "=="
        self.value_2_name = "var2"
        self.switch_state = False
        # Block dimensions based on type
        self._setup_dimensions()
        
        # Set position
        self.setPos(x, y)
        
        # Make draggable and selectable
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        
        # Circle configuration
        self.radius = 6
        self.border_width = 2
        
        print(f"✓ BlockGraphicsItem created: {block_id} ({block_type}) at ({x}, {y})")

    def _setup_dimensions(self):
        """Set block dimensions based on type"""
        if self.block_type in ["If", "While"]:
            self.width = 100
            self.height = 54
        elif self.block_type == "Timer":
            self.width = 140
            self.height = 36
        elif self.block_type == "Switch":
            self.width = 100
            self.height = 54
        else:  # Start, End, or default
            self.width = 100
            self.height = 36

    def _get_block_color(self):
        """Get color for block type"""
        colors = {
            "Start": QColor("#90EE90"),      # Light green
            "End": QColor("#FF6B6B"),        # Red
            "Timer": QColor("#87CEEB"),     # Sky blue
            "If": QColor("#87CEEB"),        # Sky blue
            "While": QColor("#87CEEB"),     # Sky blue
            "Switch": QColor("#87CEEB"),    # Sky blue
        }
        return colors.get(self.block_type, QColor("#FFD700"))  # Default yellow

    def boundingRect(self):
        """Define the bounding rectangle for the item"""
        return QRectF(0, 0, self.width + 2 * self.radius, self.height)

    def paint(self, painter, option, widget):
        """Paint the block using QPainter"""
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Draw main block body
        self._draw_block_body(painter)
        
        # Draw text
        self._draw_text(painter)
        
        # Draw connection circles
        self._draw_connection_circles(painter)

    def _draw_block_body(self, painter):
        """Draw the main rounded rectangle body"""
        color = self._get_block_color()
        
        # Draw filled rounded rectangle
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor("black"), self.border_width))
        
        # Main body rectangle
        body_rect = QRectF(self.radius, 0, self.width, self.height)
        painter.drawRoundedRect(body_rect, 3, 3)

    def _draw_text(self, painter):
        """Draw block label text"""
        painter.setPen(QPen(QColor("black")))
        font = QFont("Arial", 10, QFont.Weight.Normal)
        painter.setFont(font)
        
        # Determine text
        if self.block_type == "Switch":
            text = "Variable"
        else:
            text = self.block_type
        
        # Draw text centered
        if self.block_type in ["If", "While", "Switch"]:
            text_rect = QRectF(self.radius, 0, self.width, self.height)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignHCenter, text)
            text_rect2 = QRectF(self.radius, 0, self.width, self.height)
            if self.block_type == "If":
                condition_text = f"{self.value_1_name} {self.operator} {self.value_2_name}"
            elif self.block_type == "While":
                condition_text = f"{self.value_1_name} {self.operator} {self.value_2_name}"
            elif self.block_type == "Switch":
                condition_text = f"{self.value_1_name}"
            painter.drawText(text_rect2, Qt.AlignmentFlag.AlignCenter, condition_text)
        else:
            text_rect = QRectF(self.radius, 0, self.width, self.height)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
        
        # For Switch blocks, draw ON/OFF labels
        # For Switch blocks, draw ON/OFF labels with colors based on state
        if self.block_type == "Switch":
            small_font = QFont("Arial", 8)
            painter.setFont(small_font)
            
            # ON label - GREEN if ON, GRAY if OFF
            
            on_rect = QRectF(self.radius + self.width - 35, self.height / 2 - 5, 30, 10)
            on_color = QColor("Green") if self.switch_state else QColor("Gray")
            painter.setPen(QPen(on_color))
            painter.drawText(on_rect, Qt.AlignmentFlag.AlignRight, "ON")
            
            # OFF label - RED if OFF, GRAY if ON
            off_rect = QRectF(self.radius + 5, self.height / 2 - 5, 30, 10)
            off_color = QColor("Red") if not self.switch_state else QColor("Gray")
            painter.setPen(QPen(off_color))
            painter.drawText(off_rect, Qt.AlignmentFlag.AlignLeft, "OFF")


    def _draw_connection_circles(self, painter):
        """Draw input/output connection circles"""
        painter.setPen(QPen(QColor("black"), self.border_width))
        
        # Input circle (white)
        if self.block_type != "Start":
            if self.block_type in ["If", "While", "Switch"]:
                in_y = 3 * self.height / 4
            else:
                in_y = self.height / 2
            
            in_circle = QRectF(0, in_y - self.radius, 2*self.radius, 2*self.radius)
            painter.setBrush(QBrush(QColor("white")))
            painter.drawEllipse(in_circle)
        
        # Output circle(s) (red)
        if self.block_type != "End":
            if self.block_type in ["If", "While"]:
                # Two output circles
                out_y1 = self.height / 4
                out_y2 = 3 * self.height / 4
                
                for out_y in [out_y1, out_y2]:
                    out_circle = QRectF(self.width + self.radius - self.radius, 
                                       out_y - self.radius, 2*self.radius, 2*self.radius)
                    painter.setBrush(QBrush(QColor("red")))
                    painter.drawEllipse(out_circle)
            else:
                # Single output circle
                if self.block_type == "Switch":
                    out_y = 3 * self.height / 4
                else:
                    out_y = self.height / 2
                
                out_circle = QRectF(self.width + self.radius - self.radius, 
                                   out_y - self.radius, 2*self.radius, 2*self.radius)
                painter.setBrush(QBrush(QColor("red")))
                painter.drawEllipse(out_circle)

    def connect_graphics_signals(self):
        """Connect graphics item circle click signals to event handler"""
        if self.block_id not in Utils.top_infos:
            return

        block_info = Utils.top_infos[self.block_id]
        block_graphics = block_info.get('widget')

        if block_graphics and hasattr(block_graphics, 'signals'):
            if hasattr(self.canvas, 'elements_events'):
                events = self.canvas.elements_events
                try:
                    block_graphics.signals.input_clicked.connect(events.on_input_clicked)
                    block_graphics.signals.output_clicked.connect(events.on_output_clicked)
                except Exception as e:
                    print(f"Error connecting signals for {self.block_id}: {e}")

    def itemChange(self, change, value):
        """Handle position/selection changes"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            pos = self.pos()
            if self.block_id in Utils.top_infos:
                Utils.top_infos[self.block_id]['x'] = pos.x()
                Utils.top_infos[self.block_id]['y'] = pos.y()
            
            # Update connected paths
            if hasattr(self.canvas, 'path_manager'):
                self.canvas.path_manager.update_paths_for_widget(self)
        
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        """Handle block selection and circle clicks"""
        self.setSelected(True)
        local_pos = event.pos()
        circle_type = self._check_click_on_circle(local_pos)
        
        print(f"Mouse press at {local_pos}, detected circle: {circle_type}")
        
        if circle_type:
            circle_center = self._get_circle_center(circle_type)
            if isinstance(circle_center, tuple):
                circle_center = QPointF(circle_center[0], circle_center[1])
            
            if circle_type.startswith('in'):
                print(f" → Input circle clicked: {circle_type} at {circle_center}")
                self.signals.input_clicked.emit(self, circle_center, circle_type)
            elif circle_type.startswith('out'):
                print(f" → Output circle clicked: {circle_type} at {circle_center}")
                self.signals.output_clicked.emit(self, circle_center, circle_type)
        
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle block deselection"""
        self.setSelected(False)
        super().mouseReleaseEvent(event)

    def _get_circle_center(self, circle_type):
        """Get circle center in scene coordinates"""
        radius = self.radius
        
        if circle_type == 'in':
            local_x = radius
            local_y = self.height / 2
        elif circle_type == 'in1':
            local_x = radius
            local_y = 3 * (self.height / 4)
        elif circle_type == 'out':
            local_x = self.width + self.radius
            local_y = self.height / 2
        elif circle_type == 'out1':
            local_x = self.width + self.radius
            local_y = self.height / 4
        elif circle_type == 'out2':
            local_x = self.width + self.radius
            local_y = 3 * (self.height / 4)
        
        # Convert to scene coordinates
        scene_pos = self.mapToScene(local_x, local_y)
        return (scene_pos.x(), scene_pos.y())

    def _check_click_on_circle(self, click_pos, radius_margin=5):
        """
        Determine which circle (if any) was clicked
        Returns: 'in', 'out', 'in1', 'out1', 'out2', or None
        """
        effective_radius = self.radius + radius_margin
        
        # Check input circles
        if self.block_type in ('If', 'While', 'Switch'):
            # One input at 3/4 height
            in_x, in_y = self.radius, 3 * (self.height / 4)
            dist_in = ((click_pos.x() - in_x)**2 + (click_pos.y() - in_y)**2)**0.5
            if dist_in <= effective_radius:
                return 'in1'
        else:
            # Standard input at center height
            in_x, in_y = self.radius, self.height / 2
            dist_in = ((click_pos.x() - in_x)**2 + (click_pos.y() - in_y)**2)**0.5
            if dist_in <= effective_radius:
                return 'in'
        
        # Check output circles
        out_x = self.width + self.radius
        
        if self.block_type in ('If', 'While'):
            # Two output circles
            out_y1 = self.height / 4
            out_y2 = 3 * (self.height / 4)
            
            dist_out1 = ((click_pos.x() - out_x)**2 + (click_pos.y() - out_y1)**2)**0.5
            dist_out2 = ((click_pos.x() - out_x)**2 + (click_pos.y() - out_y2)**2)**0.5
            
            if dist_out1 <= effective_radius:
                return 'out1'
            if dist_out2 <= effective_radius:
                return 'out2'
        elif self.block_type == 'Switch':
            # One output at 3/4 height
            out_y = 3 * (self.height / 4)
            dist_out = ((click_pos.x() - out_x)**2 + (click_pos.y() - out_y)**2)**0.5
            if dist_out <= effective_radius:
                return 'out2'
        else:
            # Standard output at center height
            out_y = self.height / 2
            dist_out = ((click_pos.x() - out_x)**2 + (click_pos.y() - out_y)**2)**0.5
            if dist_out <= effective_radius:
                return 'out'
        
        return None
    
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

        if self.elements_window and self.elements_window.isVisible():
            self.elements_window.is_hidden = True
            self.elements_window.hide()

        print(f"Before: {self.parent.mousePressEvent}")
        self.old_mousePressEvent = parent.mousePressEvent
        parent.mousePressEvent = self.on_mouse_press
        print(f"After: {self.parent.mousePressEvent}")
        parent.setFocus()
        print(f"Canvas enabled: {parent.isEnabled()}")
        parent.raise_()
        print("Canvas raised to top")

    def on_mouse_press(self, event):
        print("Mouse Pressed")
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
            print("Perm stop activated")
            return

        print(f"Checking placing: perm_stop={self.perm_stop}, placing_active={self.placing_active}")
        if not self.element_placed and self.placing_active:
            self.element_spawner.custom_shape_spawn(parent, self.type, event)
            self.placing_active = False
            self.element_placed = True

    def stop_placing(self, parent):
        """Stop placement mode"""
        print("Placement stopped")
        self.perm_stop = True
        self.placing_active = False
        self.element_placed = False

        parent.mousePressEvent = self.old_mousePressEvent

        if self.elements_window:
            self.elements_window.is_hidden = False
            self.elements_window.open()


class Elements_events(QObject):
    """Centralized event handler for block interactions"""
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.path_manager = canvas.path_manager if hasattr(canvas, 'path_manager') else None
        print("✓ ElementsEvents initialized")
        print(f" → path_manager: {self.path_manager}")

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
        block_id = f"{element_type}_{int(time.time() * 1000)}"
        scene_pos = parent.mapToScene(event.pos())
        x, y = scene_pos.x(), scene_pos.y()

        block_graphics = parent.add_block(element_type, x, y, block_id)
        print(f"Spawned {element_type} at ({x}, {y})")