from Imports import (QWidget, QLabel, QLineEdit,
                QComboBox, QApplication, QStyleOptionComboBox,
                pyqtProperty, QEasingCurve, QRectF,
                Qt, QPoint, QPropertyAnimation, QRect,
                pyqtSignal, QObject, QRegularExpression,
                QPainter, QPen, QBrush, QColor,
                QPixmap, QImage, QMouseEvent, QStandardItem,
                QIntValidator, QRegularExpressionValidator,
                QPainterPath, QFont, QStyledItemDelegate)
from PIL import Image, ImageDraw, ImageFont
import random
from Imports import get_utils
Utils = get_utils()

items = ["=", "!=", "<=", ">=", "<", ">"]

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
    #MARK: CREATE BLOCK FROM DATA
    def create_block_from_data(self, block_id, block_type, x, y, value_1='', value_2='', combo_value='', switch_value=False):
        """
        Create a block widget from saved project data.
        
        This is called during project loading (rebuild_from_data).
        
        Args:
            block_id: Unique identifier for this block (from saved data)
            block_type: Type of block ('If', 'While', 'Start', 'End', 'Timer', etc)
            x, y: Position on canvas
            value_1: Primary value (variable name, condition, etc)
            value_2: Secondary value (comparison value, duration, etc)
            combo_value: Combo box selection (operator like '==', '>')
        
        Returns:
            block_widget: QWidget block ready to add to canvas
        """
        
        # Route to appropriate block creator
        if block_type == 'If':
            block_widget = self.create_if_block_loaded(x, y, value_1, value_2, combo_value, block_id)
        elif block_type == 'While':
            block_widget = self.create_while_block_loaded(x, y, value_1, value_2, combo_value, block_id)
        elif block_type == 'Timer':
            block_widget = self.create_timer_block_loaded(x, y, value_1, block_id)
        elif block_type == 'Start':
            block_widget = self.create_start_block_loaded(x, y, block_id)
        elif block_type == 'End':
            block_widget = self.create_end_block_loaded(x, y, block_id)
        elif block_type == 'Switch':
            block_widget = self.create_switch_block_loaded(x, y, value_1, switch_value, block_id)
        else:
            print(f"Warning: Unknown block type '{block_type}' during load. Creating generic block.")
        
        # Position the block
        block_widget.move(x, y)
        
        return block_widget


    # ============================================================================
    # BLOCK-SPECIFIC CREATORS FOR LOADING
    # ============================================================================

    def create_if_block_loaded(self, x, y, value_1, value_2, combo_value, block_id):
        """Create an If block from saved data"""
        # Create the BlockWidget properly
        blockwidget = BlockWidget(self.parent, "If", block_id=block_id)  # blockid will be set in calling code
        
        if hasattr(blockwidget, 'If_input_1') and hasattr(blockwidget, 'If_combobox') and hasattr(blockwidget, 'If_input_2'):
            # If your If block has input fields, populate them
            
            blockwidget.If_input_1.blockSignals(True)
            blockwidget.If_combobox.blockSignals(True)
            blockwidget.If_input_2.blockSignals(True)
            
            for i in range(blockwidget.If_input_1.count()):
                print(f"Checking If_input_1 item: {blockwidget.If_input_1.itemText(i)} against value_1: {value_1}")
                if blockwidget.If_input_1.itemText(i) == value_1:
                    print(f"Setting If_input_1 index to {i}")
                    blockwidget.If_input_1.setCurrentIndex(i)
                    break
            
            for i in range(blockwidget.If_combobox.count()):
                if blockwidget.If_combobox.itemText(i) == combo_value:
                    blockwidget.If_combobox.setCurrentIndex(i)
                    break
            
            blockwidget.If_input_2.setText(value_2)
            
            blockwidget.If_input_1.blockSignals(False)
            blockwidget.If_combobox.blockSignals(False)
            blockwidget.If_input_2.blockSignals(False)
            
        return blockwidget

    def create_while_block_loaded(self, x, y, value_1, value_2, combo_value, block_id):
        """Create a While block from saved data"""
        blockwidget = BlockWidget(self.parent, "While", block_id=block_id)
        
        if hasattr(blockwidget, 'While_input_1') and hasattr(blockwidget, 'While_combobox') and hasattr(blockwidget, 'While_input_2'):
            # If your While block has input fields, populate them
            
            blockwidget.While_input_1.blockSignals(True)
            blockwidget.While_combobox.blockSignals(True)
            blockwidget.While_input_2.blockSignals(True)
            
            for i in range(blockwidget.While_input_1.count()):
                print(f"Checking While_input_1 item: {blockwidget.While_input_1.itemText(i)} against value_1: {value_1}")
                if blockwidget.While_input_1.itemText(i) == value_1:
                    print(f"Setting While_input_1 index to {i}")
                    blockwidget.While_input_1.setCurrentIndex(i)
                    break
            
            for i in range(blockwidget.While_combobox.count()):
                if blockwidget.While_combobox.itemText(i) == combo_value:
                    blockwidget.While_combobox.setCurrentIndex(i)
                    break
            
            blockwidget.While_input_2.setText(value_2)
            
            blockwidget.If_input_1.blockSignals(False)
            blockwidget.If_combobox.blockSignals(False)
            blockwidget.If_input_2.blockSignals(False)
        
        return blockwidget

    def create_timer_block_loaded(self, x, y, value_1, block_id):
        """Create a Timer block from saved data"""
        blockwidget = BlockWidget(self.parent, "Timer", block_id=block_id)
        
        if hasattr(blockwidget, 'value_1'):
            print("setting timer value")
            print(f"Timer value: {value_1}")
            blockwidget.timer_input.setText(value_1)
        
        return blockwidget

    def create_start_block_loaded(self, x, y, block_id):
        """Create a Start block from saved data"""
        blockwidget = BlockWidget(self.parent, "Start", block_id=block_id)
        return blockwidget

    def create_end_block_loaded(self, x, y, block_id):
        """Create an End block from saved data"""
        blockwidget = BlockWidget(self.parent, "End", block_id=block_id)
        return blockwidget

    def create_switch_block_loaded(self, x, y, value_1, switch, block_id):
        """Create a Switch block from saved data"""
        blockwidget = BlockWidget(self.parent, "Switch", block_id=block_id)
        print(f"Switch {switch} with value_1 {value_1}")
        if hasattr(blockwidget, 'Var_input_1') and hasattr(blockwidget, 'Switch'):
            # If your Switch block has input fields, populate them
            
            blockwidget.Var_input_1.blockSignals(True)
            blockwidget.Switch.blockSignals(True)
            
            
            for i in range(blockwidget.Var_input_1.count()):
                print(f"Checking Var_input_1 item: {blockwidget.Var_input_1.itemText(i)} against value_1: {value_1}")
                if blockwidget.Var_input_1.itemText(i) == value_1:
                    print(f"Setting Var_input_1 index to {i}")
                    blockwidget.Var_input_1.setCurrentIndex(i)
                    break
            
            blockwidget.Switch.set_checked(state=switch, emit_signal=False)

                
            blockwidget.Switch.blockSignals(False)
            blockwidget.Var_input_1.blockSignals(False)
            
        return blockwidget
    
#MARK: Block Widget
class BlockWidget(QWidget):
    """Custom widget for visual programming blocks"""
    
    def __init__(self, parent, block_type, block_id):
        super().__init__(parent)
        self.block_type = block_type
        self.block_id = block_id
        self.canvas = parent
        self.events_handler = None
        
        # Generate image
        self.image = self.create_block_image()
        
        # Set size
        self.setFixedSize(self.image.width(), self.image.height())
        
        # Make transparent for non-rectangular shapes
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Add number input for timer blocks
        self.timer_input = None
        if self.block_type == "Timer":
            self.create_timer_input()

        if self.block_type == "If":
            print("If")
            self.create_If_inputs()
        if self.block_type == "While":
            print("While")
            self.create_While_inputs()
        if self.block_type == "Switch":
            self.create_Switch_inputs()
        
    def insert_items(self, combo_box):
        model = combo_box.model()
        item = QStandardItem("--")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        model.appendRow(item)
        if self.block_type == "Switch":
            for id, text in Utils.dev_items.items():
                item = QStandardItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(QColor(255, 240, 200))
                model.appendRow(item)
        else:
            for id, text in Utils.var_items.items():
                item = QStandardItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(QColor(220, 240, 255))
                model.appendRow(item)
            for id, text in Utils.dev_items.items():
                item = QStandardItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(QColor(255, 240, 200))
                model.appendRow(item)
            
    #MARK: IF Inputs      
    def create_If_inputs(self):
        print("creating if input")
        self.If_input_1 = MaxWidthComboBox(self, max_popup_width=300)
        self.If_input_1.setEditable(False)
        self.If_input_1.setFixedHeight(20)
        self.If_input_1.setMinimumWidth(30) 
        model = self.If_input_1.model()
        
        self.insert_items(self.If_input_1)
        
        delegate = NoTruncateDelegate()
        self.If_input_1.setItemDelegate(delegate)
        self.If_input_1.view().setItemDelegate(delegate)
        
        self.If_input_1.view().setMaximumWidth(300)
        self.If_input_1.view().horizontalScrollBar().setStyleSheet("""
            QScrollBar:horizontal {
                height: 0px;
            }
        """)

        # ALSO set the view minimum height to match item size
        self.If_input_1.view().setSpacing(0) 
        self.If_input_1.setCurrentIndex(0)

        input_x = self.width() - 95
        input_y =3* ((self.height() - 20) // 4)
        self.If_input_1.move(input_x, input_y)
        self.If_input_1.setStyleSheet("""
        QComboBox {
            background-color: white;
            border: 1px solid #333;
            border-radius: 3px;
            padding: 2px 2px;
            font-size: 12px;
            color: #333;
        }
        QComboBox::drop-down { 
            width: 0px; 
            border: none; 
        }
        QComboBox::down-arrow { 
            width: 0px; 
            image: none; 
        }
        QComboBox:focus {
            border: 2px solid #4CAF50;
        }
        QComboBox QAbstractItemView {
            background-color: #eeeeee;
            color: #333333;
            border: 1px solid #555555;
            selection-background-color: #1F538D;
            max-width: 300px;
            outline: none;  
        }
        """) 
        self.If_input_1.raise_()
        self.If_input_1.show()

        self.If_input_2 = QLineEdit(self)
        self.If_input_2.setFixedSize(30, 20)
        regex = QRegularExpression(r"^-?\d*$")  # Allow optional minus sign, then digits
        validator = QRegularExpressionValidator(regex, self)
        self.If_input_2.setValidator(validator)
        input_x = self.width() - 40
        input_y =3* ((self.height() - 20) // 4)
        self.If_input_2.move(input_x, input_y)
        self.If_input_2.setStyleSheet("""
        QLineEdit {
            background-color: white;
            border: 1px solid #333;
            border-radius: 3px;
            padding: 2px 2px;
            font-size: 12px;
            color: #333;
        }
        QLineEdit:focus {
            border: 2px solid #4CAF50;
        }
        """)
        self.If_input_2.setPlaceholderText("0")
        self.If_input_2.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        self.If_input_2.raise_()
        self.If_input_2.show()
        
        # Use custom NoArrowComboBox
        self.If_combobox = MaxWidthComboBox(self)
        self.If_combobox.setFixedSize(25, 20)
        self.If_combobox.setEditable(False)
        model = self.If_combobox.model()

        for text in items:
            item = QStandardItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            model.appendRow(item)
            
        #self.If_combobox.view().setMinimumWidth(60)
        
        input_x = self.width() - 65
        input_y =3* ((self.height() - 20) // 4)
        self.If_combobox.move(input_x, input_y)
        
        # CRITICAL: Apply stylesheet that includes arrow removal
        self.If_combobox.setStyleSheet("""
        QComboBox {
            background-color: white;
            border: 1px solid #333;
            border-radius: 3px;
            padding: 2px 2px;
            font-size: 12px;
            color: #333;
        }
        QComboBox::drop-down {
            background_color: white; 
            width: 0px; 
            border: none; 
        }
        QComboBox::down-arrow { 
            width: 0px; 
            image: none; 
        }
        QComboBox:focus {
            border: 2px solid #4CAF50;
        }
        QComboBox QAbstractItemView {
            background-color: #eeeeee;
            color: #333333;
            border: 1px solid #555555;
            selection-background-color: #1F538D;
        }
        """)
        
        self.If_combobox.raise_()
        self.If_combobox.show()
        
        self.If_input_1.currentIndexChanged.connect(self.on_value_1_changed)
        self.If_input_2.textChanged.connect(self.on_value_2_changed)
        self.If_combobox.currentIndexChanged.connect(self.on_combo_changed)
    #MARK: WHILE Inputs      
    def create_While_inputs(self):
        print("creating if input")
        self.While_input_1 = MaxWidthComboBox(self, max_popup_width=300)
        self.While_input_1.setEditable(False)
        self.While_input_1.setFixedHeight(20)
        self.While_input_1.setMinimumWidth(30) 
        model = self.While_input_1.model()
        
        self.insert_items(self.While_input_1)

        delegate = NoTruncateDelegate()
        self.While_input_1.setItemDelegate(delegate)
        self.While_input_1.view().setItemDelegate(delegate)
        
        self.While_input_1.view().setMaximumWidth(300)
        self.While_input_1.view().horizontalScrollBar().setStyleSheet("""
            QScrollBar:horizontal {
                height: 0px;
            }
        """)

        # ALSO set the view minimum height to match item size
        self.While_input_1.view().setSpacing(0) 
        
        self.While_input_1.setCurrentIndex(0)

        input_x = self.width() - 95
        input_y =3* ((self.height() - 20) // 4)
        self.While_input_1.move(input_x, input_y)
        self.While_input_1.setStyleSheet("""
        QComboBox {
            background-color: white;
            border: 1px solid #333;
            border-radius: 3px;
            padding: 2px 2px;
            font-size: 12px;
            color: #333;
        }
        QComboBox::drop-down { 
            width: 0px; 
            border: none; 
        }
        QComboBox::down-arrow { 
            width: 0px; 
            image: none; 
        }
        QComboBox:focus {
            border: 2px solid #4CAF50;
        }
        QComboBox QAbstractItemView {
            background-color: #eeeeee;
            color: #333333;
            border: 1px solid #555555;
            selection-background-color: #1F538D;
            max-width: 300px;
            outline: none;  
        }
        """) 
        self.While_input_1.raise_()
        self.While_input_1.show()

        self.While_input_2 = QLineEdit(self)
        self.While_input_2.setFixedSize(30, 20)
        regex = QRegularExpression(r"^-?\d*$")  # Allow optional minus sign, then digits
        validator = QRegularExpressionValidator(regex, self)
        self.While_input_2.setValidator(validator)
        input_x = self.width() - 40
        input_y =3* ((self.height() - 20) // 4)
        self.While_input_2.move(input_x, input_y)
        self.While_input_2.setStyleSheet("""
        QLineEdit {
            background-color: white;
            border: 1px solid #333;
            border-radius: 3px;
            padding: 2px 2px;
            font-size: 12px;
            color: #333;
        }
        QLineEdit:focus {
            border: 2px solid #4CAF50;
        }
        """)
        self.While_input_2.setPlaceholderText("0")
        self.While_input_2.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        self.While_input_2.raise_()
        self.While_input_2.show()
        
        # Use custom NoArrowComboBox
        self.While_combobox = MaxWidthComboBox(self)
        self.While_combobox.setFixedSize(25, 20)
        self.While_combobox.setEditable(False)
        model = self.While_combobox.model()

        for text in items:
            item = QStandardItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            model.appendRow(item)
        
        input_x = self.width() - 65
        input_y =3* ((self.height() - 20) // 4)
        self.While_combobox.move(input_x, input_y)
        
        # CRITICAL: Apply stylesheet that includes arrow removal
        self.While_combobox.setStyleSheet("""
        QComboBox {
            background-color: white;
            border: 1px solid #333;
            border-radius: 3px;
            padding: 2px 2px;
            font-size: 12px;
            color: #333;
        }
        QComboBox::drop-down {
            background_color: white; 
            width: 0px; 
            border: none; 
        }
        QComboBox::down-arrow { 
            width: 0px; 
            image: none; 
        }
        QComboBox:focus {
            border: 2px solid #4CAF50;
        }
        QComboBox QAbstractItemView {
            background-color: #eeeeee;
            color: #333333;
            border: 1px solid #555555;
            selection-background-color: #1F538D;
        }
        """)
        
        self.While_combobox.raise_()
        self.While_combobox.show()
        
        self.While_input_1.currentIndexChanged.connect(self.on_value_1_changed)
        self.While_input_2.textChanged.connect(self.on_value_2_changed)
        self.While_combobox.currentIndexChanged.connect(self.on_combo_changed)
            
    #MARK: Timer Input
    def create_timer_input(self):
        """Create number input field for timer block"""
        self.timer_input = QLineEdit(self)
        self.timer_input.setFixedSize(50, 20)
        regex = QRegularExpression(r"^\d*$")  # Only digits, no spaces
        validator = QRegularExpressionValidator(regex, self)
        self.timer_input.setValidator(validator)
        # Position the input in the middle-right area of the block
        input_x = self.width() - 65  # 15px from right edge
        input_y = (self.height() - 20) // 2  # Center vertically
        self.timer_input.move(input_x, input_y)
        
        # Style the input
        self.timer_input.setStyleSheet("""
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
        self.timer_input.setPlaceholderText("0")
        
        # Ensure input stays on top
        self.timer_input.raise_()
        self.timer_input.show()
        
        # Store the value when changed
        self.timer_input.textChanged.connect(self.on_value_1_changed)
    #MARK: Switch Input
    def create_Switch_inputs(self):
        self.Switch = CustomSwitch(parent=self, width=40, height=20)
        input_x = (self.Switch_width/2 - self.Switch.width()/2)+3
        input_y = 6*((self.Switch_height - self.Switch.height()) // 6)
        self.Switch.move(int(input_x), int(input_y))
        self.Switch.toggled.connect(self.on_switch_changed)
        
        self.Switch.raise_()
        self.Switch.show()
        
        self.Var_input_1 = MaxWidthComboBox(self, max_popup_width=300)
        self.Var_input_1.setEditable(False)
        self.Var_input_1.setFixedHeight(20)
        self.Var_input_1.setMinimumWidth(30) 
        model = self.Var_input_1.model()
        
        self.insert_items(self.Var_input_1)
        
        delegate = NoTruncateDelegate()
        self.Var_input_1.setItemDelegate(delegate)
        self.Var_input_1.view().setItemDelegate(delegate)
        
        self.Var_input_1.view().setMaximumWidth(300)
        self.Var_input_1.view().horizontalScrollBar().setStyleSheet("""
            QScrollBar:horizontal {
                height: 0px;
            }
        """)

        # ALSO set the view minimum height to match item size
        self.Var_input_1.view().setSpacing(0) 
        
        self.Var_input_1.setCurrentIndex(0)

        input_x = self.Switch_width - 30
        input_y =(self.height() - 20) // 4
        self.Var_input_1.move(input_x, input_y)
        self.Var_input_1.setStyleSheet("""
        QComboBox {
            background-color: white;
            border: 1px solid #333;
            border-radius: 3px;
            padding: 2px 2px;
            font-size: 12px;
            color: #333;
        }
        QComboBox::drop-down { 
            width: 0px; 
            border: none; 
        }
        QComboBox::down-arrow { 
            width: 0px; 
            image: none; 
        }
        QComboBox:focus {
            border: 2px solid #4CAF50;
        }
        QComboBox QAbstractItemView {
            background-color: #eeeeee;
            color: #333333;
            border: 1px solid #555555;
            selection-background-color: #1F538D;
            max-width: 300px;
            outline: none;  
        }
        """) 
        self.Var_input_1.raise_()
        self.Var_input_1.show()
        
        self.Var_input_1.currentIndexChanged.connect(self.on_value_1_changed)
    #MARK: Change Handlers
    def on_switch_changed(self, state):
        """Called automatically when switch toggles"""
        print(f"Switch state changed to: {state}")
        # True = ON, False = OFF
        
        # Store in Utils if needed
        if self.block_id in Utils.top_infos:
            Utils.top_infos[self.block_id]['switch_value'] = state
            print(f"Switch {self.block_id} value: {Utils.top_infos[self.block_id]['switch_value']}")
    
    def on_value_1_changed(self, text):
        """Handle timer value changes"""
        # Store in Utils for later use
        if not text:  # User cleared the field
            return
        
        for block_id, top_info in Utils.top_infos.items():
            if top_info['id'] is self.block_id:
                type = top_info['type']
        
        if type == "If":
            value_1 = self.If_input_1.currentText()
            Utils.top_infos[self.block_id]['value_1'] = value_1
        elif type == "While":
            value_1 = self.While_input_1.currentText()
            Utils.top_infos[self.block_id]['value_1'] = value_1
        elif type == "Switch":
            value_1 = self.Var_input_1.currentText()
            Utils.top_infos[self.block_id]['value_1'] = value_1
        elif type == "Timer":
            try:
                value = len(text)
                
                if value > 4:
                    self.timer_input.blockSignals(True)
                    text = text[:4]
                    self.timer_input.setText(text)
                    self.timer_input.blockSignals(False)
                
                elif value < 0:
                    self.timer_input.blockSignals(True)
                    self.timer_input.setText("0")
                    self.timer_input.blockSignals(False)
                
                # Store the valid value
                if self.block_id in Utils.top_infos:
                    Utils.top_infos[self.block_id]['value_1'] = text
                    print(f"Timer {self.block_id} value: {text}")
                    
            except ValueError:
                # Text is empty or can't convert (shouldn't happen with regex)
                pass        
            
    def on_value_2_changed(self, text):
        """Handle second value changes (if needed)"""
        # Store in Utils for later use
        if not text:  # User cleared the field
            return
        if self.block_type == "Timer":
            try:
                value = len(text)
                
                if value > 4:
                    self.timer_input.blockSignals(True)
                    text = text[:4]
                    self.timer_input.setText(text)
                    self.timer_input.blockSignals(False)
            
                elif value < 0:
                    self.timer_input.blockSignals(True)
                    self.timer_input.setText("0")
                    self.timer_input.blockSignals(False)
                
                # Store the valid value
                if self.block_id in Utils.top_infos:
                    Utils.top_infos[self.block_id]['value_2'] = text
                    print(f"Timer {self.block_id} value: {text}")
            except ValueError:
                        # Text is empty or can't convert (shouldn't happen with regex)
                        pass 
        elif self.block_type == "If":
            try:
                value = len(text)
                
                if value > 4:
                    self.If_input_2.blockSignals(True)
                    text = text[:4]
                    self.If_input_2.setText(text)
                    self.If_input_2.blockSignals(False)

                elif value < 0:
                    self.If_input_2.blockSignals(True)
                    self.If_input_2.setText("0")
                    self.If_input_2.blockSignals(False)
                
                # Store the valid value
                if self.block_id in Utils.top_infos:
                    Utils.top_infos[self.block_id]['value_2'] = text
                    print(f"If {self.block_id} value: {text}")
            except ValueError:
                        # Text is empty or can't convert (shouldn't happen with regex)
                        pass
        elif self.block_type == "While":
            try:
                value = len(text)
                
                if value > 4:
                    self.While_input_2.blockSignals(True)
                    text = text[:4]
                    self.While_input_2.setText(text)
                    self.While_input_2.blockSignals(False)
                
                elif value < 0:
                    self.While_input_2.blockSignals(True)
                    self.While_input_2.setText("0")
                    self.While_input_2.blockSignals(False)
                
                # Store the valid value
                if self.block_id in Utils.top_infos:
                    Utils.top_infos[self.block_id]['value_2'] = text
                    print(f"While {self.block_id} value: {text}")
            except ValueError:
                        # Text is empty or can't convert (shouldn't happen with regex)
                        pass 
        
    def on_combo_changed(self, index):
        """Handle combo box selection changes (if needed)"""
        for block_id, top_info in Utils.top_infos.items():
            if top_info['id'] is self.block_id:
                type = top_info['type']
        
        if type == "If":
            combo_value = self.If_combobox.currentText()
            Utils.top_infos[self.block_id]['combo_value'] = combo_value
        elif type == "While":
            combo_value = self.While_combobox.currentText()
            Utils.top_infos[self.block_id]['combo_value'] = combo_value
        print(f"Block {self.block_id} combo changed to index: {index}")
        print(Utils.top_infos)
    
    def refresh_dropdown(self):
        """Refresh the If block's variable dropdown with updated names"""
        print("REFRESH for block", self.block_id, "type", self.block_type)
        print("VARS:", Utils.var_items)
        print("DEVS:", Utils.dev_items)
        if self.block_type not in ('If', 'While', 'Switch'):
            return
        
        if self.block_type == "If":
            self.If_input_1.blockSignals(True)
            self.If_input_1.clear()
            model = self.If_input_1.model()  # ← Get model reference
            
            
            self.insert_items(self.If_input_1)  # ← Add to model, not addItem()
            
            self.If_input_1.blockSignals(False)
        
        if self.block_type == "While":
            self.While_input_1.blockSignals(True)
            self.While_input_1.clear()
            model = self.While_input_1.model()  # ← Get model reference
            
            # Add variables
            self.insert_items(self.While_input_1)  # ← Use model, not addItem()
            
            self.While_input_1.blockSignals(False)
        
        if self.block_type == "Switch":
            self.Var_input_1.blockSignals(True)
            self.Var_input_1.clear()
            model = self.Var_input_1.model()  # ← Get model reference
            
            # Add variables
            self.insert_items(self.Var_input_1)  # ← Use model, not addItem()
            
            self.Var_input_1.blockSignals(False)
        
        print(f"Refreshed If block {self.block_id} dropdown")
    
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
        elif self.block_type == "While":
            return self.create_while_image()
        elif self.block_type == "Switch":
            return self.create_switch_image()
        else:
            return self.create_start_end_image(self.block_type, "#FFD700")
    #MARK: Start/End Image
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
    #MARK: Timer Image
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
    #MARK: If Image
    def create_if_image(self):
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
    #MARK: While Image
    def create_while_image(self):
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
    #MARK: Switch Image
    def create_switch_image(self):
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
      
    def paintEvent(self, event):
        """Draw the block"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(0, 0, self.image)
    
    def mousePressEvent(self, event):
        """Unified mouse handler - emit signal instead of handling directly"""
        print(f"\n✓ Block {self.block_id} mousePressEvent fired!")
        print(f"  Click position (local): {event.pos()}")
        print(f"  events_handler: {self.events_handler}")
        
        if self.events_handler is None:
            print("  ⚠ ERROR: events_handler is None!")
            return
        
        # Check which circle was clicked
        circle_type = self.events_handler.check_click_on_circle(self, event.pos())
        print(f"  Circle type detected: {circle_type}")
        
        if circle_type:
            print(f"  ✓ Circle detected! Getting info...")
            circle_center = self.events_handler.get_circle_info(self, circle_type)
            print(f"  Circle center: {circle_center}")
            
            if circle_type in ('in', 'in1'):
                print(f"  → Emitting block_input_clicked signal")
                self.events_handler.block_input_clicked.emit(self, circle_center, circle_type)
            elif circle_type in ('out', 'out1', 'out2'):
                print(f"\n🚀 Emitting block_output_clicked")
                print(f"   Circle type: {circle_type}")
                print(f"   self.events_handler: {self.events_handler}")
                self.events_handler.block_output_clicked.emit(self, circle_center, circle_type)
        else:
            print(f"  ✗ Not on a circle - treating as drag")
            super().mousePressEvent(event)
#MARK: Elements_events
class Elements_events(QObject):
    """Centralized event handler for block interactions"""
    
    # Define signals for different events
    block_input_clicked = pyqtSignal(object, tuple, str)  # (block, circle_center, circle_type)
    block_output_clicked = pyqtSignal(object, tuple, str)  # (block, center, circle_type)
    
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.path_manager = canvas.path_manager if hasattr(canvas, 'path_manager') else None
        
        print(f"🔗 Elements_events.__init__(): Connecting signals...")
        print(f"   block_output_clicked signal: {self.block_output_clicked}")
        print(f"   on_output_clicked slot: {self.on_output_clicked}")
        # Connect signals to slots
        self.block_input_clicked.connect(self.on_input_clicked)
        self.block_output_clicked.connect(self.on_output_clicked)
    
        print(f"✓ Signals connected successfully")
        
    def on_input_clicked(self, block, circle_center, circle_type):
        """Handle input circle clicks"""
        if self.path_manager:
            self.path_manager.finalize_connection(block, circle_center, circle_type)
    
    def on_output_clicked(self, block, circle_center, circle_type):
        """Handle output circle clicks"""
        print(f"\n✓✓ on_output_clicked FIRED!")
        print(f"  Block: {block.block_id}, circle_type: {circle_type}")
        print(f"  path_manager: {self.path_manager}")
        
        if self.path_manager:
            print(f"  → Calling path_manager.start_connection()")
            self.path_manager.start_connection(block, circle_center, circle_type)
        else:
            print(f"  ⚠ path_manager is None!")
            pass
    
    def get_circle_info(self, block, circle_type):
        """
        Calculate circle center based on block type and circle role
        
        Args:
            block: BlockWidget instance
            circle_type: 'in1', 'in2', 'out', 'out1', 'out2'
        
        Returns:
            tuple: (screen_x, screen_y) in parent canvas coordinates
        """
        radius = block.height() / 5
        block_screen_pos = (block.x(), block.y())
        
        if circle_type == 'in':
            local_x = radius
            local_y = block.height() / 2
        elif circle_type == 'in1':
            local_x = radius
            local_y = 3*(block.height() / 4)
        elif circle_type == 'out':
            local_x = block.width() - radius
            local_y = block.height() / 2
        elif circle_type == 'out1':  # If block, first output
            local_x = block.width() - radius
            local_y = block.height() / 4
        elif circle_type == 'out2':  # If block, second output
            local_x = block.width() - radius
            local_y = 3 * block.height() / 4
        
        screen_x = block_screen_pos[0] + local_x
        screen_y = block_screen_pos[1] + local_y
        
        return (screen_x, screen_y)
    
    def check_click_on_circle(self, block, click_pos, radius_margin=1):
        """
        Determine which circle (if any) was clicked
        
        Args:
            block: BlockWidget
            click_pos: QPoint of click (in block's local coords)
            radius_margin: tolerance pixels
        
        Returns:
            str: 'in', 'out', 'out1', 'out2', or None
        """
        radius = block.height() / 5
        effective_radius = radius + radius_margin
        
        # Input circle
        if block.block_type in ('If', 'While'):
            # If has ONE input at 3/4 height
            in2_x, in2_y = radius, 3 * (block.height() / 4)
            print(f"  Checking If block inputs at ({in2_x}, {in2_y})")
            dist_in2 = ((click_pos.x() - in2_x)**2 + (click_pos.y() - in2_y)**2)**0.5
            print(f"  Distances to inputs: in2={dist_in2}, effective_radius={effective_radius}")
            if dist_in2 <= effective_radius:
                return 'in1'  # ✅ Matches get_circle_info case
        elif block.block_type == 'Switch':
            # Switch has ONE input at 3/4 height
            in_x, in_y = radius, 3 * (block.height() / 4)
            dist_in = ((click_pos.x() - in_x)**2 + (click_pos.y() - in_y)**2)**0.5
            
            if dist_in <= effective_radius:
                return 'in1'
            
        else:
            # All other blocks: ONE input
            in_x, in_y = radius, block.height() / 2
            dist_in = ((click_pos.x() - in_x)**2 + (click_pos.y() - in_y)**2)**0.5
            
            if dist_in <= effective_radius:
                return 'in'
        # Output circles
        out_x = block.width() - radius
        
        if block.block_type in ('If', 'While'):
            # Two output circles
            out_y1 = block.height() / 4
            out_y2 = 3 * block.height() / 4
            
            dist_out1 = ((click_pos.x() - out_x)**2 + (click_pos.y() - out_y1)**2)**0.5
            dist_out2 = ((click_pos.x() - out_x)**2 + (click_pos.y() - out_y2)**2)**0.5
            
            if dist_out1 <= effective_radius:
                return 'out1'
            if dist_out2 <= effective_radius:
                return 'out2'
        elif block.block_type == 'Switch':
            # Single output circle at 3/4 height
            out_y = 3 * (block.height() / 4)
            dist_out = ((click_pos.x() - out_x)**2 + (click_pos.y() - out_y)**2)**0.5
            
            if dist_out <= effective_radius:
                return 'out2'
        else:
            # Single output circle
            out_y = block.height() / 2
            dist_out = ((click_pos.x() - out_x)**2 + (click_pos.y() - out_y)**2)**0.5
            
            if dist_out <= effective_radius:
                return 'out'
        
        return None


class Element_spawn:
    """Spawns visual elements"""
    
    height = 36
    
    def custom_shape_spawn(self, parent, element_type, event):
        """Spawn a custom shape at the clicked position"""
        # Generate unique ID
        block_id = random.randint(10000, 99999)
        
        Utils.top_infos[block_id] = {
            'widget': None,  # Will set after block created
            'id': block_id,
            'type': element_type,
            'x': 0, 'y': 0,  # Will update after positioning
            'width': 0, 'height': 0,
            'in_connections': [],
            'out_connections': [],
            'value_1': '--',  # Default values
            'value_2': '',
            'combo_value': '=',
            'switch_value': 'True',
        }
        
        # Create block widget
        block = BlockWidget(parent, element_type, block_id)
        
        Utils.top_infos[block_id]['widget'] = block
        Utils.top_infos[block_id]['width'] = block.width()
        Utils.top_infos[block_id]['height'] = block.height()
        
        
        block.events_handler = parent.elements_events
        #print(f"✓ Assigned events_handler to block {block_id}")
        #print(f"  events_handler is: {block.events_handler}")
        #print(f"  parent.elements_events is: {parent.elements_events}")
        # Position at click location
        click_pos = event.pos()
        x, y = parent.snap_to_grid(click_pos.x(), click_pos.y(), block, during_drag=False)
        block.move(x, y)
        Utils.top_infos[block_id]['x'] = x
        Utils.top_infos[block_id]['y'] = y
        
        # Add to canvas
        parent.add_draggable_widget(block)
        
        print(f"Created block: {element_type} at ({x}, {y})")
