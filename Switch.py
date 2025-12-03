import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6_SwitchControl import SwitchControl


# ====== APPROACH 1: Using Stylesheets ======
def create_styled_switch(circle_size="medium"):
    """
    Create SwitchControl with custom styling via stylesheet
    
    circle_size options: "small", "medium", "large", "xlarge"
    """
    switch = SwitchControl()
    
    # Stylesheet approach - affects padding/margins
    stylesheets = {
        "small": """
            SwitchControl {
                padding: 2px;
                margin: 2px;
            }
        """,
        "medium": """
            SwitchControl {
                padding: 4px;
                margin: 4px;
            }
        """,
        "large": """
            SwitchControl {
                padding: 6px;
                margin: 6px;
            }
        """,
        "xlarge": """
            SwitchControl {
                padding: 8px;
                margin: 8px;
            }
        """
    }
    
    if circle_size in stylesheets:
        switch.setStyleSheet(stylesheets[circle_size])
    
    return switch


# ====== APPROACH 2: Scale using setMinimumSize/setMaximumSize ======
def create_scaled_switch(scale_factor=1.0):
    """
    Scale the entire switch widget (including circle)
    
    scale_factor: 1.0 = normal, 0.5 = half size, 2.0 = double size
    """
    switch = SwitchControl()
    
    # Default SwitchControl is roughly 60x30
    base_width = 60
    base_height = 30
    
    new_width = int(base_width * scale_factor)
    new_height = int(base_height * scale_factor)
    
    switch.setFixedSize(new_width, new_height)
    return switch


# ====== APPROACH 3: Custom SwitchControl Subclass ======
# (Better control over circle proportions)

class CustomSwitchControl(SwitchControl):
    """
    Extended SwitchControl with adjustable circle size
    """
    def __init__(self, parent=None, circle_ratio=0.8):
        """
        Initialize with custom circle ratio
        
        circle_ratio: 0.0-1.0, how much of height should be circle
                      0.8 = 80% of height (default)
                      0.6 = 60% of height (smaller circle)
                      1.0 = 100% of height (large circle)
        """
        super().__init__(parent)
        self.circle_ratio = circle_ratio
        # Note: SwitchControl doesn't expose circle_diameter directly,
        # so visual effect is limited without full reimplementation
    
    def set_circle_ratio(self, ratio):
        """Adjust circle size ratio"""
        self.circle_ratio = max(0.3, min(1.0, ratio))  # Clamp between 0.3-1.0
        self.update()


# ====== DEMO WINDOW ======

class SwitchControlSizeDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SwitchControl - Circle Size Examples")
        self.setGeometry(100, 100, 700, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("SwitchControl Circle Size Options")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # ===== SECTION 1: Size Scaling =====
        section1_title = QLabel("Section 1: Size Scaling (Scales Entire Widget)")
        section1_title_font = QFont()
        section1_title_font.setPointSize(12)
        section1_title_font.setBold(True)
        section1_title.setFont(section1_title_font)
        layout.addWidget(section1_title)
        
        # 0.5x (Small)
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(QLabel("0.5x Scale (Small):"))
        h_layout1.addWidget(create_scaled_switch(0.5))
        h_layout1.addStretch()
        layout.addLayout(h_layout1)
        
        # 1.0x (Normal)
        h_layout2 = QHBoxLayout()
        h_layout2.addWidget(QLabel("1.0x Scale (Normal):"))
        h_layout2.addWidget(create_scaled_switch(1.0))
        h_layout2.addStretch()
        layout.addLayout(h_layout2)
        
        # 1.5x (Large)
        h_layout3 = QHBoxLayout()
        h_layout3.addWidget(QLabel("1.5x Scale (Large):"))
        h_layout3.addWidget(create_scaled_switch(1.5))
        h_layout3.addStretch()
        layout.addLayout(h_layout3)
        
        # 2.0x (Extra Large)
        h_layout4 = QHBoxLayout()
        h_layout4.addWidget(QLabel("2.0x Scale (Extra Large):"))
        h_layout4.addWidget(create_scaled_switch(2.0))
        h_layout4.addStretch()
        layout.addLayout(h_layout4)
        
        # 3.0x (Huge)
        h_layout5 = QHBoxLayout()
        h_layout5.addWidget(QLabel("3.0x Scale (Huge):"))
        h_layout5.addWidget(create_scaled_switch(3.0))
        h_layout5.addStretch()
        layout.addLayout(h_layout5)
        
        layout.addSpacing(20)
        
        # ===== SECTION 2: Stylesheet Styling =====
        section2_title = QLabel("Section 2: Stylesheet Approach")
        section2_title.setFont(section1_title_font)
        layout.addWidget(section2_title)
        
        h_layout6 = QHBoxLayout()
        h_layout6.addWidget(QLabel("Styled Small:"))
        h_layout6.addWidget(create_styled_switch("small"))
        h_layout6.addStretch()
        layout.addLayout(h_layout6)
        
        h_layout7 = QHBoxLayout()
        h_layout7.addWidget(QLabel("Styled Medium:"))
        h_layout7.addWidget(create_styled_switch("medium"))
        h_layout7.addStretch()
        layout.addLayout(h_layout7)
        
        h_layout8 = QHBoxLayout()
        h_layout8.addWidget(QLabel("Styled Large:"))
        h_layout8.addWidget(create_styled_switch("large"))
        h_layout8.addStretch()
        layout.addLayout(h_layout8)
        
        h_layout9 = QHBoxLayout()
        h_layout9.addWidget(QLabel("Styled XLarge:"))
        h_layout9.addWidget(create_styled_switch("xlarge"))
        h_layout9.addStretch()
        layout.addLayout(h_layout9)
        
        layout.addSpacing(20)
        
        # ===== SECTION 3: Custom Subclass =====
        section3_title = QLabel("Section 3: Custom Subclass (Limited Effect)")
        section3_title.setFont(section1_title_font)
        layout.addWidget(section3_title)
        
        h_layout10 = QHBoxLayout()
        h_layout10.addWidget(QLabel("Custom Subclass:"))
        custom_switch = CustomSwitchControl(circle_ratio=0.1)
        h_layout10.addWidget(custom_switch)
        h_layout10.addStretch()
        layout.addLayout(h_layout10)
        
        layout.addStretch()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SwitchControlSizeDemo()
    window.show()
    sys.exit(app.exec())