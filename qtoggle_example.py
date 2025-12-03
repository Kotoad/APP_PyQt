# QToggle Example - PyQt6 Custom Toggle Switch Widget
# This example implements a fully customizable toggle switch from scratch

import sys
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QEasingCurve
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import QPropertyAnimation, QRect, pyqtProperty, QRectF



class QToggle(QWidget):
    """
    Advanced customizable toggle switch widget for PyQt6.
    Inherits from QWidget and provides smooth animations and full customization.
    """
    
    # Signal emitted when toggle state changes
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None, 
                 width=60, height=30,
                 bg_color="#cccccc", 
                 circle_color="#ffffff",
                 active_color="#4CAF50",
                 disabled_color="#999999",
                 animation_duration=200):
        super().__init__(parent)
        
        # State
        self._is_checked = False
        self._circle_position = 0
        
        # Sizing
        self.width = width
        self.height = height
        self.circle_diameter = height - 4
        self.margin = 2
        
        # Colors
        self.bg_color = bg_color
        self.circle_color = circle_color
        self.active_color = active_color
        self.disabled_color = disabled_color
        
        @pyqtProperty(float)
        def circle_position(self):
            return self._circle_position
        
        @circle_position.setter
        def circle_position(self, pos):
            self._circle_position = pos
            self.update()
        
        # Animation
        self.animation = QPropertyAnimation(self, b"circle_position")
        self.animation.setDuration(animation_duration)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # Set widget properties
        self.setFixedSize(self.width, self.height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def mousePressEvent(self, event):
        """Handle mouse click to toggle state"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle()
    
    def toggle(self):
        """Toggle the switch state with animation"""
        self._is_checked = not self._is_checked
        self._animate_toggle()
        self.toggled.emit(self._is_checked)
    
    def _animate_toggle(self):
        """Animate the circle movement"""
        if self._is_checked:
            end_pos = self.width - self.circle_diameter - self.margin
        else:
            end_pos = self.margin
        
        self.animation.setStartValue(self._circle_position)
        self.animation.setEndValue(end_pos)
        self.animation.start()
    
    def set_circle_position(self, pos):
        """Property setter for animation (used by QPropertyAnimation)"""
        self._circle_position = pos
        self.update()
    
    def get_circle_position(self):
        """Property getter for animation"""
        return self._circle_position
    
    # Create Qt property for animation
    circle_position = pyqtProperty(float, get_circle_position, set_circle_position)
    
    def is_checked(self):
        """Return current toggle state"""
        return self._is_checked
    
    def set_checked(self, state):
        """Set toggle state programmatically"""
        if self._is_checked != state:
            self._is_checked = state
            self._animate_toggle()
            self.toggled.emit(self._is_checked)
    
    def paintEvent(self, event):
        """Draw the toggle switch"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        bg_rect = QRect(0, 0, self.width, self.height)
        bg_color = QColor(self.active_color if self._is_checked else self.bg_color)
        painter.fillRect(bg_rect, bg_color)
        
        # Draw border
        painter.setPen(QColor("#000000"))
        painter.drawRoundedRect(bg_rect, self.height // 2, self.height // 2)
        
        # Draw circle (handle)
        circle_rect = QRect(
            int(self._circle_position),
            self.margin,
            self.circle_diameter,
            self.circle_diameter
        )
        painter.setBrush(QColor(self.circle_color))
        painter.drawEllipse(circle_rect)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QToggle Examples - PyQt6")
        self.setGeometry(100, 100, 600, 400)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Add title
        title = QLabel("QToggle Widget Examples")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Example 1: Default toggle
        example1_layout = QHBoxLayout()
        example1_label = QLabel("Default Toggle:")
        toggle1 = QToggle()
        toggle1.toggled.connect(lambda state: print(f"Toggle 1: {'ON' if state else 'OFF'}"))
        example1_layout.addWidget(example1_label)
        example1_layout.addWidget(toggle1)
        example1_layout.addStretch()
        main_layout.addLayout(example1_layout)
        
        # Example 2: Custom colors (Purple)
        example2_layout = QHBoxLayout()
        example2_label = QLabel("Purple Theme:")
        toggle2 = QToggle(
            bg_color="#e0e0e0",
            circle_color="#ffffff",
            active_color="#9c27b0",
            animation_duration=300
        )
        toggle2.toggled.connect(lambda state: print(f"Toggle 2: {'ON' if state else 'OFF'}"))
        example2_layout.addWidget(example2_label)
        example2_layout.addWidget(toggle2)
        example2_layout.addStretch()
        main_layout.addLayout(example2_layout)
        
        # Example 3: Custom colors (Blue)
        example3_layout = QHBoxLayout()
        example3_label = QLabel("Blue Theme:")
        toggle3 = QToggle(
            width=70,
            height=35,
            bg_color="#f0f0f0",
            circle_color="#ffffff",
            active_color="#2196f3",
            animation_duration=250
        )
        toggle3.toggled.connect(lambda state: print(f"Toggle 3: {'ON' if state else 'OFF'}"))
        example3_layout.addWidget(example3_label)
        example3_layout.addWidget(toggle3)
        example3_layout.addStretch()
        main_layout.addLayout(example3_layout)
        
        # Example 4: Start checked
        example4_layout = QHBoxLayout()
        example4_label = QLabel("Pre-checked Toggle:")
        toggle4 = QToggle(
            bg_color="#e0e0e0",
            circle_color="#ffffff",
            active_color="#ff9800"
        )
        toggle4.set_checked(True)  # Start in checked state
        toggle4.toggled.connect(lambda state: print(f"Toggle 4: {'ON' if state else 'OFF'}"))
        example4_layout.addWidget(example4_label)
        example4_layout.addWidget(toggle4)
        example4_layout.addStretch()
        main_layout.addLayout(example4_layout)
        
        # Example 5: Show state label
        example5_layout = QHBoxLayout()
        example5_label = QLabel("Status Display:")
        toggle5 = QToggle(
            bg_color="#e0e0e0",
            active_color="#4CAF50"
        )
        self.status_label = QLabel("Status: OFF")
        toggle5.toggled.connect(self.update_status)
        example5_layout.addWidget(example5_label)
        example5_layout.addWidget(toggle5)
        example5_layout.addWidget(self.status_label)
        example5_layout.addStretch()
        main_layout.addLayout(example5_layout)
        
        main_layout.addStretch()
    
    def update_status(self, state):
        """Update status label based on toggle state"""
        self.status_label.setText(f"Status: {'ON ✓' if state else 'OFF ✗'}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
