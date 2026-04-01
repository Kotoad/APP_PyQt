import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QGridLayout, QPushButton, QLabel, QFrame, QScrollArea,
                             QLineEdit)
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

class ColorSwatch(QFrame):
    """A custom widget to display a color sample and its role name."""
    def __init__(self, role_name, role, parent=None):
        super().__init__(parent)
        self.role_name = role_name
        self.role = role
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setLineWidth(1)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(2) # Tighter spacing for the text fields
        
        # Color Box
        self.color_box = QFrame()
        self.color_box.setFixedHeight(50)
        self.color_box.setAutoFillBackground(True)
        
        # Role Name
        self.name_label = QLabel(self.role_name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("""
            QLabel {
                color: palette(text); font-weight: bold; font-size: 12px; margin-top: 4px;
            }
        """)
        
        # HEX Code (Using read-only QLineEdit for easy copying)
        self.hex_input = QLineEdit()
        self.hex_input.setReadOnly(True)
        self.hex_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hex_input.setStyleSheet("""
            QLineEdit {
                background: transparent; 
                border: none; 
                font-size: 11px; 
                color: palette(text);
                selection-background-color: palette(highlight);
            }
        """)
        
        # RGB Code (Using read-only QLineEdit for easy copying)
        self.rgb_input = QLineEdit()
        self.rgb_input.setReadOnly(True)
        self.rgb_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rgb_input.setStyleSheet("""
            QLineEdit {
                background: transparent; 
                border: none; 
                font-size: 11px; 
                color: palette(text);
                selection-background-color: palette(highlight);
            }
        """)
        
        layout.addWidget(self.color_box)
        layout.addWidget(self.name_label)
        layout.addWidget(self.hex_input)
        layout.addWidget(self.rgb_input)
        
    def update_color(self, palette):
        color = palette.color(self.role)
        
        # Update the visual box
        box_palette = self.color_box.palette()
        box_palette.setColor(QPalette.ColorRole.Window, color)
        self.color_box.setPalette(box_palette)
        
        # Update the copyable text fields
        self.name_label.setStyleSheet("""
            QLabel {
                color: palette(text); font-weight: bold; font-size: 12px; margin-top: 4px;
            }
        """)

        self.hex_input.setText(color.name().upper())
        self.hex_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                font-size: 11px;
                color: palette(text);
                selection-background-color: palette(highlight);
            }
        """)
        self.rgb_input.setText(f"rgb({color.red()}, {color.green()}, {color.blue()})")
        self.rgb_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                font-size: 11px;
                color: palette(text);
                selection-background-color: palette(highlight);
            }
        """)

        # Set cursor to beginning so it doesn't scroll if text is slightly long
        self.hex_input.setCursorPosition(0)
        self.rgb_input.setCursorPosition(0)

class ThemeTesterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OmniBoard Full Palette Tester")
        self.resize(900, 750)
        self.current_theme = 'dark' 
        
        # EXACTLY 22 ROLES: All distinct QPalette.ColorRole enums in PyQt6
        self.roles = [
            ("Window", QPalette.ColorRole.Window),
            ("WindowText", QPalette.ColorRole.WindowText),
            ("Base", QPalette.ColorRole.Base),
            ("AlternateBase", QPalette.ColorRole.AlternateBase),
            ("ToolTipBase", QPalette.ColorRole.ToolTipBase),
            ("ToolTipText", QPalette.ColorRole.ToolTipText),
            ("Text", QPalette.ColorRole.Text),
            ("PlaceholderText", QPalette.ColorRole.PlaceholderText),
            ("Button", QPalette.ColorRole.Button),
            ("ButtonText", QPalette.ColorRole.ButtonText),
            ("BrightText", QPalette.ColorRole.BrightText),
            ("Highlight", QPalette.ColorRole.Highlight),
            ("HighlightedText", QPalette.ColorRole.HighlightedText),
            ("Link", QPalette.ColorRole.Link),
            ("LinkVisited", QPalette.ColorRole.LinkVisited),
            ("Light", QPalette.ColorRole.Light),
            ("Midlight", QPalette.ColorRole.Midlight),
            ("Mid", QPalette.ColorRole.Mid),
            ("Dark", QPalette.ColorRole.Dark),
            ("Shadow", QPalette.ColorRole.Shadow),
            ("Accent", QPalette.ColorRole.Accent),
            ("NoRole", QPalette.ColorRole.NoRole),
        ]
        
        self.swatches = []
        self.setup_ui()
        self.apply_theme() 

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        header_layout = QVBoxLayout()
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        
        self.toggle_btn = QPushButton("Toggle Light / Dark Mode")
        self.toggle_btn.setFixedSize(200, 40)
        self.toggle_btn.clicked.connect(self.toggle_theme)
        
        header_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.toggle_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(header_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_content = QWidget()
        self.grid_layout = QGridLayout(scroll_content)
        self.grid_layout.setSpacing(10)
        
        row, col = 0, 0
        max_cols = 5  
        for name, role in self.roles:
            swatch = ColorSwatch(name, role)
            self.swatches.append(swatch)
            self.grid_layout.addWidget(swatch, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def toggle_theme(self):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme()

    def apply_theme(self):
        palette = QPalette()

        if self.current_theme == 'dark':
            self.title_label.setText("Current Theme: Slate Dark")
            # Primary Backgrounds & Texts
            palette.setColor(QPalette.ColorRole.Window, QColor(15, 23, 42))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(226, 232, 240))
            palette.setColor(QPalette.ColorRole.Base, QColor(30, 41, 59))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(51, 65, 85))
            palette.setColor(QPalette.ColorRole.Text, QColor(226, 232, 240))
            palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(148, 163, 184)) 
            
            # Tooltips
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(15, 23, 42))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(226, 232, 240))
            
            # Buttons
            palette.setColor(QPalette.ColorRole.Button, QColor(30, 41, 59))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(226, 232, 240))
            
            # Highlights & Links
            palette.setColor(QPalette.ColorRole.Highlight, QColor(59, 130, 246))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Link, QColor(59, 130, 246))
            palette.setColor(QPalette.ColorRole.LinkVisited, QColor(139, 92, 246)) 
            palette.setColor(QPalette.ColorRole.Accent, QColor(59, 130, 246))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 160, 0)) 
            
            # 3D Bevels & Shadows (Light to Dark)
            palette.setColor(QPalette.ColorRole.Light, QColor(51, 65, 85))
            palette.setColor(QPalette.ColorRole.Midlight, QColor(30, 41, 59))
            palette.setColor(QPalette.ColorRole.Mid, QColor(15, 23, 42))
            palette.setColor(QPalette.ColorRole.Dark, QColor(2, 6, 23))
            palette.setColor(QPalette.ColorRole.Shadow, QColor(0, 0, 0))
            
            palette.setColor(QPalette.ColorRole.NoRole, QColor(51, 65, 85))

        elif self.current_theme == 'light':
            self.title_label.setText("Current Theme: Warm Light")
            # Primary Backgrounds & Texts
            palette.setColor(QPalette.ColorRole.Window, QColor(253, 245, 230))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.Base, QColor(224, 218, 202))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(225, 225, 225))
            palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(120, 120, 120)) 
            
            # Tooltips (Dark contrast for readability)
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(30, 30, 30))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
            
            # Buttons
            palette.setColor(QPalette.ColorRole.Button, QColor(253, 245, 230))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
            
            # Highlights & Links
            palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Link, QColor(0, 120, 215))
            palette.setColor(QPalette.ColorRole.LinkVisited, QColor(128, 0, 128)) 
            palette.setColor(QPalette.ColorRole.Accent, QColor(0, 120, 215))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(220, 38, 38)) 
            
            # 3D Bevels & Shadows (Light to Dark)
            palette.setColor(QPalette.ColorRole.Light, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Midlight, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.Mid, QColor(200, 200, 200))
            palette.setColor(QPalette.ColorRole.Dark, QColor(160, 160, 160))
            palette.setColor(QPalette.ColorRole.Shadow, QColor(100, 100, 100))
            
            palette.setColor(QPalette.ColorRole.NoRole, QColor(169, 169, 169))


        QApplication.instance().setPalette(palette)
        
        self.title_label.setStyleSheet("""
            QLabel {
                color: palette(text);
            }
        """)

        for swatch in self.swatches:
            swatch.update_color(palette)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion') 
    
    window = ThemeTesterApp()
    window.show()
    
    sys.exit(app.exec())