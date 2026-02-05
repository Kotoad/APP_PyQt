from Imports import (QWidget, QLabel, QLineEdit, math,
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

#MARK: - BlockGraphicsItem
class BlockGraphicsItem(QGraphicsItem, QObject):
    """Graphics item representing a block - renders with QPainter for perfect zoom quality"""

    def __init__(self, x, y, block_id, block_type, parent_canvas, main_window=None, name=None):
        super().__init__()
        print(f'Initializing BlockGraphicsItem: {block_id} of type {block_type} at ({x}, {y}) on canvas {parent_canvas}, name: {name if name else "N/A"}')
        self.signals = BlockSignals()
        self.state_manager = Utils.state_manager
        if main_window is not None:
            self.main_window = main_window
        elif hasattr(parent_canvas, 'main_window'):
            self.main_window = parent_canvas.main_window
        else:
            self.main_window = QApplication.instance().activeWindow()
        #print(f"Main window in BlockGraphicsItem: {self.main_window}")
        self.border_color = QColor("black")

        self.block_id = block_id
        self.block_type = block_type
        self.canvas = parent_canvas
        self.canvas_id = None
        self.name = name
        self.grid_size = 25
        #print(f"self.canvas: {self.canvas}, self.block_id: {self.block_id}, self.block_type: {self.block_type}, self.x: {x}, self.y: {y}, self.name: {self.name}")
        self.value_1_name = "N"
        if self.block_type == "Basic_operations":
            self.operator = "+"
        elif self.block_type == "Exponential_operations":
            self.operator = "^"
        elif self.block_type == "Random_number":
            self.operator = "rand"
        elif self.block_type in ("If", "While", "Switch"):
            self.operator = "=="
        self.value_2_name = "N"
        self.result_var_name = "N"
        self.switch_state = False
        self.sleep_time = "1000"
        self.PWM_value = "128"
        # Block dimensions based on type
        self._setup_dimensions()
        
        # Set position
        self.setPos(x, y)
        
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        
        # Circle configuration
        self.radius = 6
        self.border_width = 2
        
        print(f"✓ BlockGraphicsItem created: {block_id} ({block_type}) at ({x}, {y})")

    def _setup_dimensions(self):
        v_count = 0
        d_count = 0
        """Set block dimensions based on type"""
        if self.block_type in ["If", "While", "Switch", "Button"]:
            self.width = 100
            self.height = 54
        elif self.block_type in ["Timer","Basic_operations", "Exponential_operations",
                                "Random_number", "Blink_LED", "PWM_LED"]:
            self.width = 150
            self.height = 36
        elif self.block_type in [ "Start", "End", "While_true", "Toggle_LED"]:
            self.width = 100
            self.height = 36
        elif self.block_type == "Function":
            #print(f"Utils.variables['function_canvases']: {Utils.variables['function_canvases']}")
            for canvas, canvas_info in Utils.canvas_instances.items():
                if canvas_info.get('ref') == 'function' and canvas_info.get('name') == self.name:
                    self.canvas_id = canvas_info.get('id')
                    break
            #print(f"Calculating dimensions for function block: {self.name} in canvas {self.canvas_id}")
            for f_id, f_info in Utils.variables['function_canvases'][self.canvas_id].items():
                v_count += 1
            for f_id, f_info in Utils.devices['function_canvases'][self.canvas_id].items():
                d_count += 1
            
            if v_count >= d_count:
                count = v_count
            else:
                count = d_count
            self.width = 150
            self.height = 15 + (count * 20)
        else:  #Fallback for other blocks
            print(f"[Warning] Unknown block type '{self.block_type}', using default dimensions.")
            self.width = 100
            self.height = 36

    def _calculate_dimensions(self, painter):
        """Recalculate block dimensions based on current properties"""
        self._setup_dimensions()
        self._calculate_width_from_text(painter)
        self.prepareGeometryChange()

    def _get_block_color(self):
        """Get color for block type"""
        colors = {
            "Start": QColor("#90EE90"),      # Light green
            "End": QColor("#FF6B6B"),        # Red
            "Timer": QColor("#02B488"),     # Sky blue
            "If": QColor("#87CEEB"),        # Sky blue
            "While": QColor("#87CEEB"),     # Sky blue
            "Switch": QColor("#87CEEB"),    # Sky blue
            "Button": QColor("#D3D3D3"),    # Light gray
            "While_true": QColor("#87CEEB"),     # Sky blue
            "Function": QColor("#FFA500"),  # Orange
            "Basic_operations": QColor("#9900FF"),  # Light orange
            "Exponential_operations": QColor("#9900FF"),      # Purple
            "Random_number": QColor("#9900FF"),  # Purple
            "Blink_LED": QColor("#57A139"),      # Yellow
            "Toggle_LED": QColor("#57A139"),     # Yellow
            "PWM_LED": QColor("#57A139"),        # Yellow
        }
        return colors.get(self.block_type, QColor("#FFD700"))  # Default yellow

    def boundingRect(self):
        """Define the bounding rectangle for the item"""
        return QRectF(0, 0, self.width + 2 * self.radius, self.height)

    def paint(self, painter, option, widget):
        """Paint the block using QPainter"""

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        self._calculate_dimensions(painter)

        # Draw main block body
        self._draw_block_body(painter)
        
        # Draw text
        self._draw_text(painter)
        
        # Draw connection circles
        self._draw_connection_circles(painter)

    def _calculate_width_from_text(self, painter):
        """Calculate required width based on text content"""
        font = QFont("Arial", 8, QFont.Weight.Normal)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        
        text_to_measure = ""
        
        # --- Determine the text string exactly as you do in _draw_text ---
        if self.block_type in ["If", "While"]:
            text_to_measure = f"{self.value_1_name} {self.operator} {self.value_2_name}"
        elif self.block_type == "Timer":
            text_to_measure = f"Wait {self.sleep_time} ms"
        elif self.block_type == "Switch":
            text_to_measure = f"{self.value_1_name}"
        elif self.block_type == "Button":
            text_to_measure = f"{self.value_1_name}"
        elif self.block_type in ["Basic_operations", "Exponential_operations", "Random_number"]:
            text_to_measure = f"{self.result_var_name} = {self.value_1_name} {self.operator} {self.value_2_name}"
        elif self.block_type == "Blink_LED":
            text_to_measure = f"{self.value_1_name} - {self.sleep_time} ms"
        elif self.block_type == "PWM_LED":
            text_to_measure = f"{self.value_1_name} - {self.PWM_value}"
        elif self.block_type == "Toggle_LED":
            text_to_measure = f"{self.value_1_name}"
        elif self.block_type == "Function":
             # Function blocks calculate height in _setup_dimensions, but here we check width
             longest_line = metrics.horizontalAdvance(self.name)
             
             # Check variables
             if self.canvas_id in Utils.variables['function_canvases']:
                 for v in Utils.variables['function_canvases'][self.canvas_id].values():
                     w = metrics.horizontalAdvance(v['name'])
                     if w > longest_line: longest_line = w
                     
             # Check devices
             if self.canvas_id in Utils.devices['function_canvases']:
                 for d in Utils.devices['function_canvases'][self.canvas_id].values():
                     w = metrics.horizontalAdvance(d['name'])
                     if w > longest_line: longest_line = w
             
             text_to_measure = " " * int(longest_line / metrics.averageCharWidth()) # Approximate for below logic

        # --- Update Width ---
        if text_to_measure:
            text_width = metrics.horizontalAdvance(text_to_measure)

            text_width = (math.ceil(text_width/self.grid_size)*self.grid_size)+25
            #print(f"Calculated text width for block '{self.block_id}' ({self.block_type}): {text_width}")
            self.width = max(self.width, text_width)

    def _draw_block_body(self, painter):
        """Draw the main rounded rectangle body"""
        color = self._get_block_color()
        
        # Draw filled rounded rectangle
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(self.border_color, self.border_width))
        
        # Main body rectangle
        body_rect = QRectF(self.radius, 0, self.width, self.height)
        painter.drawRoundedRect(body_rect, 3, 3)

    def _draw_text(self, painter):
        """Draw block label text"""
        #print("Drawing text for block:", self.block_type)
        painter.setPen(QPen(QColor("black")))
        font = QFont("Arial", 8, QFont.Weight.Normal)
        painter.setFont(font)
        
        # Determine text
        text = self.block_type
        # Draw text centered
        if self.block_type in ["If", "While", "Button"]:
            text_rect = QRectF(self.radius, 0, self.width, self.height)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignHCenter, text)
            text_rect2 = QRectF(self.radius, 0, self.width, self.height)
            if self.block_type == "If":
                condition_text = f"{self.value_1_name} {self.operator} {self.value_2_name}"
            elif self.block_type == "While":
                condition_text = f"{self.value_1_name} {self.operator} {self.value_2_name}"
            elif self.block_type == "Button":
                condition_text = f"{self.value_1_name}"
            len = painter.fontMetrics().boundingRect(condition_text).width()
            painter.drawText(text_rect2, Qt.AlignmentFlag.AlignCenter, condition_text)
        elif self.block_type == "Timer":
            text_rect = QRectF(self.radius, 0, self.width, self.height)
            timer_text = f"Wait {self.sleep_time} ms"
            len = painter.fontMetrics().boundingRect(timer_text).width()
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, timer_text)
        elif self.block_type == "Button":
            ON_rect = QRectF(self.radius, 5, self.width-10, self.height)
            OFF_rect = QRectF(self.radius, 0, self.width-10, self.height-5)
            device_text = f"{self.value_1_name}"
            len = painter.fontMetrics().boundingRect(device_text).width()
            painter.drawText(QRectF(self.radius+5, 5, self.width, self.height), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeading, text)
            painter.drawText(QRectF(self.radius, 0, self.width, self.height), Qt.AlignmentFlag.AlignCenter, device_text)
            painter.drawText(ON_rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight, "ON")
            painter.drawText(OFF_rect, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight, "OFF")
        elif self.block_type == "Function":
            #print(f"Drawing function block text for: {self.block_type}")
            name_rect = QRectF(self.radius, 0, self.width, self.height)
            painter.drawText(name_rect, Qt.AlignmentFlag.AlignHCenter, self.name)

            # Draw variable/device list
            small_font = QFont("Arial", 8)
            painter.setFont(small_font)
            y_offset = 20
            longest = 0
            for v_id, v_info in Utils.variables['function_canvases'][self.canvas_id].items():
                #print(f"   Drawing variable: {v_info['name']}")
                var_text = f"{v_info['name']}"
                var_rect = QRectF(self.radius + 10, y_offset, self.width - 20, 15)
                current_len = painter.fontMetrics().boundingRect(var_text).width()
                if current_len > longest:
                    longest = current_len
                painter.drawText(var_rect, Qt.AlignmentFlag.AlignLeft, var_text)
                y_offset += 20
            len += longest
            y_offset = 20
            for d_id, d_info in Utils.devices['function_canvases'][self.canvas_id].items():
                #print(f"   Drawing device: {d_info['name']}")
                dev_text = f"{d_info['name']}"
                dev_rect = QRectF(self.radius + 10, y_offset, self.width - 20, 15)
                current_len = painter.fontMetrics().boundingRect(dev_text).width()
                if current_len > longest:
                    longest = current_len
                painter.drawText(dev_rect, Qt.AlignmentFlag.AlignRight, dev_text)
                y_offset += 20
            len += longest

        elif self.block_type == "Switch":
            small_font = QFont("Arial", 8)
            painter.setFont(small_font)
            #print(f"Drawing Switch labels, state: {self.switch_state}")
            #print(f"Current block data: {Utils.main_canvas['blocks'].get(self.block_id, {})}")
            
            dev_text = f"{self.value_1_name}"
            dev_rect = QRectF(self.radius, 0, self.width, self.height)
            len = painter.fontMetrics().boundingRect(dev_text).width()
            painter.drawText(dev_rect, Qt.AlignmentFlag.AlignCenter, dev_text)

            on_rect = QRectF(self.radius + self.width - 35, self.height / 2 - 5, 30, 10)
            on_color = QColor("Green") if self.switch_state else QColor("Gray")
            painter.setPen(QPen(on_color))
            painter.drawText(on_rect, Qt.AlignmentFlag.AlignRight, "ON")
            
            off_rect = QRectF(self.radius + 5, self.height / 2 - 5, 30, 10)
            off_color = QColor("Red") if not self.switch_state else QColor("Gray")
            painter.setPen(QPen(off_color))
            painter.drawText(off_rect, Qt.AlignmentFlag.AlignLeft, "OFF")
        
        elif self.block_type in ["Basic_operations", "Exponential_operations", "Random_number"]:
            math_text = f"{self.result_var_name} = {self.value_1_name} {self.operator} {self.value_2_name}"
            math_rect = QRectF(self.radius, 0, self.width, self.height)
            len = painter.fontMetrics().boundingRect(math_text).width()
            painter.drawText(math_rect, Qt.AlignmentFlag.AlignCenter, math_text)
        elif self.block_type in ["Toggle_LED",]:
            device_text = f"{self.value_1_name}"
            device_rect = QRectF(self.radius, 0, self.width, self.height)
            len = painter.fontMetrics().boundingRect(device_text).width()
            painter.drawText(device_rect, Qt.AlignmentFlag.AlignCenter, device_text)
        elif self.block_type in ["Blink_LED"]:
            device_text = f"{self.value_1_name} - {self.sleep_time} ms"
            device_rect = QRectF(self.radius, 0, self.width, self.height)
            len = painter.fontMetrics().boundingRect(device_text).width()
            painter.drawText(device_rect, Qt.AlignmentFlag.AlignCenter, device_text)
        elif self.block_type in ["PWM_LED"]:
            device_text = f"{self.value_1_name} - {self.PWM_value}"
            device_rect = QRectF(self.radius, 0, self.width, self.height)
            len = painter.fontMetrics().boundingRect(device_text).width()
            painter.drawText(device_rect, Qt.AlignmentFlag.AlignCenter, device_text)
        else:
            text_rect = QRectF(self.radius, 0, self.width, self.height)
            len = painter.fontMetrics().boundingRect(text).width()
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

    def _draw_connection_circles(self, painter):
        """Draw input/output connection circles"""
        painter.setPen(QPen(QColor("black"), self.border_width))
        
        # Input circle (white)
        if self.block_type != "Start":
            if self.block_type in ["If", "While", "Switch", "Button"]:
                in_y = 3 * self.height / 4
            else:
                in_y = self.height / 2
            
            in_circle = QRectF(0, in_y - self.radius, 2*self.radius, 2*self.radius)
            painter.setBrush(QBrush(QColor("white")))
            painter.drawEllipse(in_circle)
        
        # Output circle(s) (red)
        if self.block_type != "End":
            if self.block_type in ["If", "While", "Button"]:
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
                if self.block_type in ("Switch"):
                    out_y = 3 * self.height / 4
                else:
                    out_y = self.height / 2
                
                out_circle = QRectF(self.width + self.radius - self.radius, 
                                   out_y - self.radius, 2*self.radius, 2*self.radius)
                painter.setBrush(QBrush(QColor("red")))
                painter.drawEllipse(out_circle)
    #MARK: - Event Handling
    def connect_graphics_signals(self):
        """Connect graphics item circle click signals to event handler"""
        #print(f"        Self: {self}")
        #print(f"        canvas: {self.canvas}")
        if self.canvas.reference == 'canvas':
            #print("   Connecting signals for main canvas block")
            if self.block_id not in Utils.main_canvas['blocks']:
                return
            else:
                #print(f"   Found block in main canvas: {self.block_id}")
                block_info = Utils.main_canvas['blocks'][self.block_id]
        else:
            #print("   Connecting signals for function canvas block")
            for f_id, f_info in Utils.functions.items():
                if self.canvas == f_info.get('canvas'):
                    if self.block_id not in f_info['blocks']:
                        return
                    else:
                        #print(f"   Found block in function {f_id}: {self.block_id}")
                        block_info = f_info['blocks'][self.block_id]
                        break
        #print(f"✓ Connecting signals for block: {self.block_id}")
        block_graphics = block_info.get('widget')
        #print(f"   block_graphics: {block_graphics}")
        if block_graphics and hasattr(block_graphics, 'signals'):
            #print(f"   block_graphics.signals: {block_graphics.signals}")
            #print(f"   canvas: {self.canvas if hasattr(self.canvas, 'elements_events') else 'No canvas events'}")
            if hasattr(self.canvas, 'elements_events'):
                #print(f"   canvas.elements_events: {self.canvas.elements_events}")
                events = self.canvas.elements_events
                try:
                    block_graphics.signals.input_clicked.connect(events.on_input_clicked)
                    block_graphics.signals.output_clicked.connect(events.on_output_clicked)
                    #print(f"   Signals connected for {self.block_id}")
                except Exception as e:
                    print(f"Error connecting signals for {self.block_id}: {e}")

    def snap_to_grid(self, x, y):
        #Snap coordinates to the nearest grid intersection
        
        height = self.height     
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
        snapped_y = int(Grid_rounded_y_height_offset)
        print(f"snapped before adjustment: {snapped_x}, {snapped_y}")
        print(f"Differences: {abs(x - snapped_x)}, {abs(y - snapped_y)}")"""
        
            
        snapped_x = int(round(x / self.grid_size) * self.grid_size - self.radius)
        snapped_y = int((round(y / self.grid_size) * self.grid_size)+ height_offset)
        if (abs(y - snapped_y)) > (self.grid_size/2):
            #print("Adjusting snapped_y upwards")
            snapped_y = int(snapped_y - self.grid_size)
        """print(f"Original {x}, {y}") 
        print(f"Rounded {round_x}, {round_y}")
        print(f"Grid {Grid_rounded_x, Grid_rounded_y}")
        print(f"Grid + height_offset {Grid_rounded_y_height_offset}")
        print(f"Snapped {snapped_x}, {snapped_y}")"""
        return snapped_x, snapped_y

    def itemChange(self, change, value):
        """Handle position/selection changes"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene():
            # Snap to grid on move
            new_pos = value
            snapped_x, snapped_y = self.snap_to_grid(new_pos.x(), new_pos.y())
            return QPointF(snapped_x, snapped_y)

        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if self.state_manager.canvas_state.on_moving_item():
                #print(f"Block {self.block_id} moved to {value}")
                #print(f"Z value before move: {self.zValue()}")
                self.setZValue(1)  # Bring to front while moving
                #print(f"Z value {self.zValue()} set for moving block {self.block_id}")
                pos = self.pos()
                pos_x = pos.x()
                pos_y = pos.y()
                if self.canvas.reference == 'canvas':
                    if self.block_id in Utils.main_canvas['blocks']:
                        Utils.main_canvas['blocks'][self.block_id]['x'] = pos_x
                        Utils.main_canvas['blocks'][self.block_id]['y'] = pos_y
                else:
                    for f_id, f_info in Utils.functions.items():
                        if self.canvas == f_info.get('canvas'):
                            if self.block_id in f_info['blocks']:
                                f_info['blocks'][self.block_id]['x'] = pos_x
                                f_info['blocks'][self.block_id]['y'] = pos_y
                                break
                
                # Update connected paths
                if hasattr(self.canvas, 'path_manager'):
                    self.canvas.path_manager.update_paths_for_widget(self)
                

                if hasattr(self.canvas, 'inspector_frame_visible') and self.canvas.inspector_frame_visible:
                    if self.canvas.last_inspector_block and self.canvas.last_inspector_block.block_id == self.block_id:
                        self.main_window.update_pos(self.canvas.last_inspector_block)
        
        return super().itemChange(change, value)
    #MARK: - Mouse Events
    def mousePressEvent(self, event):
        """Handle block selection and circle clicks"""
        self.setSelected(True)
        local_pos = event.pos()
        circle_type = self._check_click_on_circle(local_pos)
        
        print(f"Mouse press at {local_pos}, detected circle: {circle_type}")
        
        if event.button() == Qt.MouseButton.LeftButton:
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
                self.ungrabMouse()
                event.accept()
                return  # Prevent further processing if circle clicked
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle block deselection"""
        self.setSelected(False)
        print("Current state before release:", self.state_manager.canvas_state.current_state())
        if self.state_manager.canvas_state.current_state() == 'MOVING_ITEM':
            print("Setting state to IDLE after move")
            self.setZValue(0)  # Reset Z value after moving
            self.state_manager.canvas_state.on_idle()
        super().mouseReleaseEvent(event)
    
    #MARK: - Hover Events
    def hoverEnterEvent(self, event):
        # Change color or show handle when mouse touches block
        print("Mouse entered block!")
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.border_color = QColor("blue")
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        # Reset color when mouse leaves
        print("Mouse left block!")
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.border_color = QColor("black")
        self.update()
        super().hoverLeaveEvent(event)

    #MARK: - Circle Detection
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
        if self.block_type in ('If', 'While', 'Switch', 'Button'):
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
        
        if self.block_type in ('If', 'While', 'Button'):
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
    
#MARK: - spawning_elements
class spawning_elements:
    """Handles spawning and placing elements on the canvas"""
    def __init__(self, parent, elements_window=None):
        self.placing_active = False
        self.perm_stop = False
        self.element_placed = False
        self.parent = parent
        self.elements_window = elements_window
        self.element_spawner = Element_spawn()
        self.state_manager = Utils.state_manager

    def start(self, parent, element_type, name=None):
        """Start placing an element"""
        self.type = element_type
        self.name = name
        self.perm_stop = False
        self.parent = parent
        self.placing_active = True
        self.element_placed = False
        print("Start placement")
        #print(f"parent: {parent}, element_type: {element_type}")
        if self.elements_window and self.elements_window.isVisible():
            self.elements_window.is_hidden = True
            self.elements_window.hide()

        #print(f"Before: {parent.mousePressEvent}")
        self.old_mousePressEvent = parent.mousePressEvent
        parent.mousePressEvent = self.on_mouse_press
        #print(f"After: {parent.mousePressEvent}")
        parent.setFocus()
        #print(f"Canvas enabled: {parent.isEnabled()}")
        parent.raise_()
        #print("Canvas raised to top")

    def on_mouse_press(self, event):
        #print("Mouse Pressed")
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
            #print("Perm stop activated")
            return

        #print(f"Checking placing: perm_stop={self.perm_stop}, placing_active={self.placing_active}")
        if not self.element_placed and self.placing_active:
            self.element_spawner.custom_shape_spawn(parent, self.type, event, self.name)
            self.placing_active = False
            self.element_placed = True
            #print(f"Element placed: {self.type}, at {event.pos()}, Placement active: {self.placing_active}, Element placed: {self.element_placed}")

    def stop_placing(self, parent):
        """Stop placement mode"""
        print("Placement stopped")
        self.perm_stop = True
        self.placing_active = False
        self.element_placed = False
        print("Current state before idle:", self.state_manager.canvas_state.current_state())
        self.state_manager.canvas_state.on_idle()
        print("Current state after idle:", self.state_manager.canvas_state.current_state())
        parent.mousePressEvent = self.old_mousePressEvent
        #print("Restored original mousePressEvent")
        if self.elements_window:
            print("Re-opening ElementsWindow")
            self.elements_window.is_hidden = True
            self.elements_window.open()

#MARK: - Elements_events
class Elements_events(QObject):
    """Centralized event handler for block interactions"""
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.path_manager = canvas.path_manager if hasattr(canvas, 'path_manager') else None
        self.inspector_frame_visible = canvas.inspector_frame_visible if hasattr(canvas, 'inspector_frame_visible') else None
        self.state_manager = Utils.state_manager
        #print(f"Instantiating ElementsEvents for canvas: {canvas}")
        #print(f" → inspector_panel: {self.inspector_frame_visible}")
        #print("✓ ElementsEvents initialized")
        #print(f" → path_manager: {self.path_manager}")

    def on_input_clicked(self, block, circle_center, circle_type):
        """Handle input circle clicks"""
        #print(f"✓ on_input_clicked: {block.block_id} ({circle_type})")
        if self.path_manager:
            print("Current state before finalizing connection:", self.state_manager.canvas_state.current_state())
            self.path_manager.finalize_connection(block, circle_center, circle_type)
            

    def on_output_clicked(self, block, circle_center, circle_type):
        """Handle output circle clicks"""
        #print(f"✓ on_output_clicked: {block.block_id} ({circle_type})")
        if self.path_manager:
            print("Current state before adding path:", self.state_manager.canvas_state.current_state())
            if self.state_manager.canvas_state.on_adding_path():
                print("Adding path...")
                self.path_manager.start_connection(block, circle_center, circle_type)

#MARK: - Element_spawn
class Element_spawn:
    """Spawns visual elements"""
    height = 36

    def custom_shape_spawn(self, parent, element_type, event, name=None):
        """Spawn a custom shape at the clicked position"""
        #print(f"Spawning element: {element_type}")
        block_id = f"{element_type}_{int(time.time() * 1000)}"
        scene_pos = parent.mapToScene(event.pos())
        x, y = scene_pos.x(), scene_pos.y()

        parent.add_block(element_type, x, y, block_id, name)
        #print(f"Spawned {element_type} at ({x}, {y})")