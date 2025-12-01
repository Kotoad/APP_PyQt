from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QComboBox, QApplication, QStyleOptionComboBox
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal, QObject
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QImage, QMouseEvent, QStandardItem
from PIL import Image, ImageDraw, ImageFont
import random
import Utils
from PyQt6.QtWidgets import QStyledItemDelegate

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

        #print(f"Before: {self.parent.mousePressEvent}")
        self.old_mousePressEvent = parent.mousePressEvent
        parent.mousePressEvent = self.on_mouse_press
        #print(f"After: {self.parent.mousePressEvent}")
        parent.setFocus()
        #print(f"Canvas enabled: {parent.isEnabled()}")
        #print(f"Canvas transparent for mouse: {parent.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)}")
        #print(f"Canvas focus: {parent.hasFocus()}")
        parent.raise_()
        #print("Canvas raised to top")
        
        
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
    #MARK: IF Inputs      
    def create_If_inputs(self):
        print("creating if input")
        self.If_input_1 = MaxWidthComboBox(self, max_popup_width=300)
        self.If_input_1.setEditable(False)
        self.If_input_1.setFixedHeight(20)
        self.If_input_1.setMinimumWidth(30) 
        model = self.If_input_1.model()
        
        Utils.var_items.setdefault("default_item", "--")
        for var_id, vars in Utils.variables.items():
            Utils.var_items.setdefault(var_id, vars['name'])
        print(Utils.var_items)
        
        for var_id, var_name in Utils.var_items.items():
            item = QStandardItem(var_name)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            model.appendRow(item)
            
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
        self.If_input_2.setText("1")
        self.If_input_2.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        self.If_input_2.raise_()
        self.If_input_2.show()
        
        # Use custom NoArrowComboBox
        self.If_combobox = MaxWidthComboBox(self)
        self.If_combobox.setFixedSize(25, 20)
        self.If_combobox.setEditable(False)
        model = self.If_combobox.model()
        items = ["=", "<=", ">=", "<", ">"]

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
        
        Utils.var_items.setdefault("default_item", "--")
        for var_id, vars in Utils.variables.items():
            Utils.var_items.setdefault(var_id, vars['name'])
        print(Utils.var_items)
        
        for var_id, var_name in Utils.var_items.items():
            item = QStandardItem(var_name)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            model.appendRow(item)
            
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
        self.While_input_2.setText("1")
        self.While_input_2.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        self.While_input_2.raise_()
        self.While_input_2.show()
        
        # Use custom NoArrowComboBox
        self.While_combobox = MaxWidthComboBox(self)
        self.While_combobox.setFixedSize(25, 20)
        self.While_combobox.setEditable(False)
        model = self.While_combobox.model()
        items = ["=", "<=", ">=", "<", ">"]

        for text in items:
            item = QStandardItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            model.appendRow(item)
            
        #self.If_combobox.view().setMinimumWidth(60)
        
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
        
    def refresh_if_dropdown(self):
        """Refresh the If block's variable dropdown with updated names"""
        if self.block_type not in ('If', 'While'):
            return
        
        # Block signals so we don't trigger change events
        if self.block_type == 'If':
            self.If_input_1.blockSignals(True)
            self.If_input_1.clear()
        if self.block_type == 'While':
            self.While_input_1.blockSignals(True)
            self.While_input_1.clear()
        
        # Add new items from updated Utils.items_If
        for var_id, var_name in Utils.var_items.items():
            if self.block_type == 'If':
                self.If_input_1.addItem(var_name)
            if self.block_type == 'While':
                self.While_input_1.addItem(var_name)
        
        # Unblock signals
        if self.block_type == 'If':
            self.If_input_1.blockSignals(False)
        if self.block_type == 'While':
            self.While_input_1.blockSignals(False)
        
        print(f"Refreshed If block {self.block_id} dropdown")    
    #MARK: Timer Input
    def create_timer_input(self):
        """Create number input field for timer block"""
        self.timer_input = QLineEdit(self)
        self.timer_input.setFixedSize(50, 20)
        
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
        self.timer_input.setText("1")
        
        # Ensure input stays on top
        self.timer_input.raise_()
        self.timer_input.show()
        
        # Store the value when changed
        self.timer_input.textChanged.connect(self.on_value_1_changed)
    
    def on_value_1_changed(self, text):
        """Handle timer value changes"""
        # Store in Utils for later use
        if self.block_id in Utils.top_infos:
            Utils.top_infos[self.block_id]['value_1'] = text
        print(f"Timer {self.block_id} value changed to: {text}")
        print(Utils.top_infos)
    def on_value_2_changed(self, text):
        """Handle second value changes (if needed)"""
        # Store in Utils for later use
        if self.block_id in Utils.top_infos:
            Utils.top_infos[self.block_id]['value_2'] = text
        print(f"Block {self.block_id} value 2 changed to: {text}")
        print(Utils.top_infos)
    def on_combo_changed(self, index):
        """Handle combo box selection changes (if needed)"""
        if self.block_id in Utils.top_infos:
            Utils.top_infos[self.block_id]['combo_index'] = index
        print(f"Block {self.block_id} combo changed to index: {index}")
        print(Utils.top_infos)
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
      
    def paintEvent(self, event):
        """Draw the block"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(0, 0, self.image)
    
    def mousePressEvent(self, event):
        """Unified mouse handler - emit signal instead of handling directly"""
        #print(f"\n✓ Block {self.block_id} mousePressEvent fired!")
        #print(f"  Click position (local): {event.pos()}")
        #print(f"  events_handler: {self.events_handler}")
        
        if self.events_handler is None:
            #print("  ⚠ ERROR: events_handler is None!")
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
                print(f"  → Emitting block_output_clicked signal")
                self.events_handler.block_output_clicked.emit(self, circle_center, circle_type)
        else:
            print(f"  ✗ Not on a circle - treating as drag")
            super().mousePressEvent(event)

class Elements_events(QObject):
    """Centralized event handler for block interactions"""
    
    # Define signals for different events
    block_input_clicked = pyqtSignal(object, tuple, str)  # (block, circle_center, circle_type)
    block_output_clicked = pyqtSignal(object, tuple, str)  # (block, center, circle_type)
    
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.path_manager = canvas.path_manager if hasattr(canvas, 'path_manager') else None
        
        # Connect signals to slots
        self.block_input_clicked.connect(self.on_input_clicked)
        self.block_output_clicked.connect(self.on_output_clicked)
    
    def on_input_clicked(self, block, circle_center, circle_type):
        """Handle input circle clicks"""
        if self.path_manager:
            self.path_manager.finalize_connection(block, circle_center, circle_type)
    
    def on_output_clicked(self, block, circle_center, circle_type):
        """Handle output circle clicks"""
        #print(f"\n✓✓ on_output_clicked FIRED!")
        #print(f"  Block: {block.block_id}, circle_type: {circle_type}")
        #print(f"  path_manager: {self.path_manager}")
        
        if self.path_manager:
            #print(f"  → Calling path_manager.start_connection()")
            self.path_manager.start_connection(block, circle_center, circle_type)
        else:
            #print(f"  ⚠ path_manager is None!")
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
            # If has TWO inputs
            in2_x, in2_y = radius, 3 * (block.height() / 4)
            print(f"  Checking If block inputs at ({in2_x}, {in2_y})")
            dist_in2 = ((click_pos.x() - in2_x)**2 + (click_pos.y() - in2_y)**2)**0.5
            print(f"  Distances to inputs: in2={dist_in2}, effective_radius={effective_radius}")
            if dist_in2 <= effective_radius:
                return 'in1'  # ✅ Matches get_circle_info case
        
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
        
        # Create block widget
        block = BlockWidget(parent, element_type, block_id)
        
        block.events_handler = parent.elements_events
        #print(f"✓ Assigned events_handler to block {block_id}")
        #print(f"  events_handler is: {block.events_handler}")
        #print(f"  parent.elements_events is: {parent.elements_events}")
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
