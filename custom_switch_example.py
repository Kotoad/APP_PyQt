# Why SwitchControl Can't Change Circle Size - The Truth
# Complete comparison with working solution

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtGui import QFont, QPainterPath
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush

# ====== LESSON: Why SwitchControl Doesn't Work ======
"""
PROBLEM WITH SwitchControl (from PyQt6_SwitchControl package):
===============================================================

1. Source code is CLOSED (you can't modify it)
2. Circle diameter is HARDCODED inside the package
3. No public method to change circle size
4. No circle_diameter parameter in __init__
5. Stylesheets don't affect circle - only padding/margins

RESULT: Circle size is FIXED and UNCHANGEABLE

SOLUTION: Use your CustomSwitch instead!
Your CustomSwitch has:
- ✅ circle_diameter = height - 8 (you control it!)
- ✅ Easy to resize just by changing height parameter
- ✅ Full source code access
- ✅ Complete customization
"""


# ====== YOUR CustomSwitch - FULLY CUSTOMIZABLE ======

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
    
    def is_checked(self):
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
        if event.button() == Qt.MouseButton.LeftButton and self._is_enabled:
            self.toggle()
    
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return):
            if not event.isAutoRepeat() and self._is_enabled:
                self.toggle()
        else:
            super().keyPressEvent(event)
    
    def wheelEvent(self, event):
        if self._is_enabled:
            if event.angleDelta().y() > 0:
                self.set_checked(True)
            else:
                self.set_checked(False)
    
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


# ====== COMPARISON DEMO ======

class ComparisonWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CustomSwitch - Circle Size Control")
        self.setGeometry(100, 100, 800, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        title = QLabel("YOUR CustomSwitch - Full Circle Control")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Explanation
        explanation = QLabel(
            "SwitchControl (package) = Circle size FIXED\n"
            "CustomSwitch (yours) = Circle size CONTROLLABLE\n\n"
            "The circle diameter = height - 8\n"
            "So: Just change the HEIGHT to change circle size!"
        )
        explanation_font = QFont()
        explanation_font.setPointSize(11)
        explanation.setFont(explanation_font)
        explanation.setStyleSheet("color: #666666; padding: 20px; background: #f5f5f5; border-radius: 5px;")
        layout.addWidget(explanation)
        
        layout.addSpacing(20)
        
        # Example 1: Small circle (small height)
        h_layout1 = QHBoxLayout()
        label1 = QLabel("Small Circle\n(height=20):")
        label1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label1.setMinimumWidth(120)
        h_layout1.addWidget(label1)
        switch1 = CustomSwitch(width=60, height=20)  # Small circle
        h_layout1.addWidget(switch1)
        h_layout1.addStretch()
        layout.addLayout(h_layout1)
        
        # Example 2: Medium circle (medium height)
        h_layout2 = QHBoxLayout()
        label2 = QLabel("Medium Circle\n(height=40):")
        label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label2.setMinimumWidth(120)
        h_layout2.addWidget(label2)
        switch2 = CustomSwitch(width=80, height=40)  # Medium circle (default)
        h_layout2.addWidget(switch2)
        h_layout2.addStretch()
        layout.addLayout(h_layout2)
        
        # Example 3: Large circle (large height)
        h_layout3 = QHBoxLayout()
        label3 = QLabel("Large Circle\n(height=60):")
        label3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label3.setMinimumWidth(120)
        h_layout3.addWidget(label3)
        switch3 = CustomSwitch(width=120, height=60)  # Large circle
        h_layout3.addWidget(switch3)
        h_layout3.addStretch()
        layout.addLayout(h_layout3)
        
        # Example 4: Extra large circle (extra large height)
        h_layout4 = QHBoxLayout()
        label4 = QLabel("Extra Large Circle\n(height=80):")
        label4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label4.setMinimumWidth(120)
        h_layout4.addWidget(label4)
        switch4 = CustomSwitch(width=160, height=80)  # Extra large circle
        h_layout4.addWidget(switch4)
        h_layout4.addStretch()
        layout.addLayout(h_layout4)
        
        layout.addSpacing(20)
        
        # Key info box
        key_info = QLabel(
            "KEY INSIGHT:\n"
            "circle_diameter = height - 8\n\n"
            "height=20 → circle=12px\n"
            "height=40 → circle=32px\n"
            "height=60 → circle=52px\n"
            "height=80 → circle=72px"
        )
        key_info_font = QFont()
        key_info_font.setPointSize(10)
        key_info_font.setFamily("Courier")
        key_info.setFont(key_info_font)
        key_info.setStyleSheet("background: #000000; padding: 15px; border-radius: 5px; border: 1px solid #4CAF50;")
        layout.addWidget(key_info)
        
        layout.addStretch()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ComparisonWindow()
    window.show()
    sys.exit(app.exec())