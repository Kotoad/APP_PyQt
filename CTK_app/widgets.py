import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QPushButton, QLabel, QFrame)
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QMouseEvent, QPalette, QColor


class DraggableChildWidget(QFrame):
    """Child widget that can be added to parent blocks"""
    
    def __init__(self, text="Child Block", color="#3498db", parent=None):
        super().__init__(parent)
        self.text = text
        self.setup_ui(color)
        
    def setup_ui(self, color):
        """Setup the child widget UI"""
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        
        # Set background color
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setAutoFillBackground(True)
        self.setPalette(palette)
        
        # Layout
        layout = QVBoxLayout()
        label = QLabel(self.text)
        label.setStyleSheet("color: white; font-weight: bold; padding: 5px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        self.setLayout(layout)
        self.setMinimumSize(100, 40)


class DraggableParentWidget(QFrame):
    """Parent widget that can contain child widgets and be dragged"""
    
    def __init__(self, text="Parent Block", color="#e74c3c", parent=None):
        super().__init__(parent)
        self.text = text
        self.dragging = False
        self.drag_position = QPoint()
        self.child_widgets = []
        
        self.setup_ui(color)
        
    def setup_ui(self, color):
        """Setup the parent widget UI"""
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(3)
        
        # Set background color
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setAutoFillBackground(True)
        self.setPalette(palette)
        
        # Main layout
        self.main_layout = QVBoxLayout()
        
        # Header with title
        header = QLabel(self.text)
        header.setStyleSheet("color: white; font-weight: bold; font-size: 14px; padding: 8px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(header)
        
        # Container for child widgets
        self.child_container = QWidget()
        self.child_layout = QVBoxLayout()
        self.child_layout.setContentsMargins(10, 5, 10, 5)
        self.child_layout.setSpacing(5)
        self.child_container.setLayout(self.child_layout)
        self.main_layout.addWidget(self.child_container)
        
        self.setLayout(self.main_layout)
        self.setMinimumSize(150, 80)
        self.adjust_size()
        
    def add_child_widget(self, child_widget):
        """Add a child widget to this parent"""
        self.child_widgets.append(child_widget)
        self.child_layout.addWidget(child_widget)
        
        # Adjust parent size to fit all children
        self.adjust_size()
        
    def adjust_size(self):
        """Adjust parent size to fit all child widgets"""
        # Force layout to recalculate
        self.updateGeometry()
        self.adjustSize()
        
        # Calculate required size based on children
        min_width = 150
        min_height = 80
        
        # Add space for each child
        for child in self.child_widgets:
            child_hint = child.sizeHint()
            min_width = max(min_width, child_hint.width() + 40)
            min_height += child_hint.height() + 10
        
        self.setMinimumSize(min_width, min_height)
        self.resize(self.minimumSize())
        
    def mousePressEvent(self, event: QMouseEvent):
        """Start dragging when mouse is pressed"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event: QMouseEvent):
        """Move widget while dragging"""
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            # Calculate new position
            new_pos = event.globalPosition().toPoint() - self.drag_position
            
            # Keep widget within parent bounds
            if self.parent():
                parent_rect = self.parent().rect()
                new_pos.setX(max(0, min(new_pos.x(), parent_rect.width() - self.width())))
                new_pos.setY(max(0, min(new_pos.y(), parent_rect.height() - self.height())))
            
            self.move(new_pos)
            event.accept()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Stop dragging when mouse is released"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()


class MainWindow(QMainWindow):
    """Main window containing the canvas for draggable widgets"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Draggable Widgets - Scratch Style")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget (canvas)
        self.canvas = QWidget()
        self.canvas.setStyleSheet("background-color: #ecf0f1;")
        self.setCentralWidget(self.canvas)
        
        # Create some example blocks
        self.create_example_blocks()
        
        # Control panel
        self.create_control_panel()
        
    def create_example_blocks(self):
        """Create example parent and child blocks"""
        # First parent block with children
        parent1 = DraggableParentWidget("If Block", "#e74c3c", self.canvas)
        parent1.move(50, 50)
        
        child1 = DraggableChildWidget("Condition: x > 10", "#c0392b", parent1)
        parent1.add_child_widget(child1)
        
        child2 = DraggableChildWidget("Action: print('Yes')", "#c0392b", parent1)
        parent1.add_child_widget(child2)
        
        parent1.show()
        
        # Second parent block with different children
        parent2 = DraggableParentWidget("Repeat Block", "#27ae60", self.canvas)
        parent2.move(300, 50)
        
        child3 = DraggableChildWidget("Times: 5", "#229954", parent2)
        parent2.add_child_widget(child3)
        
        child4 = DraggableChildWidget("Move forward", "#229954", parent2)
        parent2.add_child_widget(child4)
        
        child5 = DraggableChildWidget("Turn right", "#229954", parent2)
        parent2.add_child_widget(child5)
        
        parent2.show()
        
        # Third parent block - empty
        parent3 = DraggableParentWidget("Compare Block", "#f39c12", self.canvas)
        parent3.move(550, 50)
        parent3.show()
        
        # Store references
        self.parent_blocks = [parent1, parent2, parent3]
        
    def create_control_panel(self):
        """Create control panel with buttons"""
        control_widget = QWidget(self.canvas)
        control_widget.setGeometry(50, 550, 800, 100)
        control_widget.setStyleSheet("""
            background-color: white; 
            border: 2px solid #95a5a6; 
            border-radius: 8px;
            padding: 10px;
        """)
        
        layout = QHBoxLayout()
        
        # Title
        title = QLabel("Controls:")
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(title)
        
        # Add child to first block button
        btn1 = QPushButton("Add Child to If Block")
        btn1.setStyleSheet("padding: 8px; background-color: #e74c3c; color: white; border: none; border-radius: 4px;")
        btn1.clicked.connect(lambda: self.add_child_to_block(0))
        layout.addWidget(btn1)
        
        # Add child to second block button
        btn2 = QPushButton("Add Child to Repeat Block")
        btn2.setStyleSheet("padding: 8px; background-color: #27ae60; color: white; border: none; border-radius: 4px;")
        btn2.clicked.connect(lambda: self.add_child_to_block(1))
        layout.addWidget(btn2)
        
        # Add child to third block button
        btn3 = QPushButton("Add Child to Compare Block")
        btn3.setStyleSheet("padding: 8px; background-color: #f39c12; color: white; border: none; border-radius: 4px;")
        btn3.clicked.connect(lambda: self.add_child_to_block(2))
        layout.addWidget(btn3)
        
        # Info label
        info = QLabel("Drag the colored blocks around!")
        info.setStyleSheet("font-style: italic; margin-left: 20px;")
        layout.addWidget(info)
        
        layout.addStretch()
        control_widget.setLayout(layout)
        control_widget.show()
        
    def add_child_to_block(self, block_index):
        """Add a new child widget to specified parent block"""
        if block_index < len(self.parent_blocks):
            parent = self.parent_blocks[block_index]
            
            # Create appropriate child based on parent
            if block_index == 0:  # If block
                child = DraggableChildWidget(f"New Condition {len(parent.child_widgets)}", "#c0392b", parent)
            elif block_index == 1:  # Repeat block
                child = DraggableChildWidget(f"New Action {len(parent.child_widgets)}", "#229954", parent)
            else:  # Compare block
                child = DraggableChildWidget(f"New Compare {len(parent.child_widgets)}", "#e67e22", parent)
            
            parent.add_child_widget(child)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()