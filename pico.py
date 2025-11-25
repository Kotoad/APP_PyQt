from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath
import sys


class DraggableBlock(QWidget):
    """Base class for draggable blocks"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dragging = False
        self.offset = QPoint()
        self.bound_child = None
        self.parent_block = None
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # If this block is bound to a parent, drag the parent instead
            if self.parent_block:
                self.parent_block.dragging = True
                self.parent_block.offset = event.pos()
            else:
                self.dragging = True
                self.offset = event.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = self.mapToParent(event.pos() - self.offset)

            # Boundary checking
            parent_rect = self.parentWidget().rect()
            new_pos.setX(max(0, min(new_pos.x(), parent_rect.width() - self.width())))
            new_pos.setY(max(0, min(new_pos.y(), parent_rect.height() - self.height())))

            self.move(new_pos)

            # Update bound child position
            if self.bound_child:
                self.update_bound_child_position()

            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

            # Check if we're dropping a comp block on an if block
            if isinstance(self, ComparisonBlock) and not self.parent_block:
                if_block = self.find_if_block_under_mouse(event.globalPosition().toPoint())

                if if_block and not if_block.bound_child:
                    # Bind blocks together
                    if_block.bind_child(self)

            event.accept()

    def find_if_block_under_mouse(self, global_pos):
        """Find an If block under the mouse cursor"""
        # Get the widget under cursor
        widget = QApplication.widgetAt(global_pos)

        # Check if it's an If block or a child of an If block
        while widget:
            if isinstance(widget, IfBlock):
                return widget
            widget = widget.parentWidget()
            if widget == self.parentWidget():
                break

        return None


class IfBlock(DraggableBlock):
    """Diamond-shaped If block with a slot for comparison blocks"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(140, 140)
        self.drop_highlight = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create diamond shape
        path = QPainterPath()
        center_x = self.width() / 2
        center_y = self.height() / 2
        size = 60
        
        path.moveTo(center_x, center_y - size)  # Top
        path.lineTo(center_x + size, center_y)  # Right
        path.lineTo(center_x, center_y + size)  # Bottom
        path.lineTo(center_x - size, center_y)  # Left
        path.closeSubpath()
        
        # Fill diamond
        painter.fillPath(path, QBrush(QColor(135, 206, 235)))  # Sky blue
        
        # Draw border
        painter.setPen(QPen(Qt.GlobalColor.black, 3))
        painter.drawPath(path)
        
        # Draw slot if no child bound
        if not self.bound_child:
            slot_rect = QRect(int(center_x - 50), int(center_y - 25), 100, 50)  # ← FIX
            
            if self.drop_highlight:
                painter.setBrush(QBrush(QColor(76, 175, 80, 80)))
                painter.setPen(QPen(QColor(76, 175, 80), 2, Qt.PenStyle.DashLine))
            else:
                painter.setBrush(QBrush(QColor(255, 255, 255, 128)))
                painter.setPen(QPen(QColor(0, 0, 0, 80), 2, Qt.PenStyle.DashLine))
            
            painter.drawRoundedRect(slot_rect, 8, 8)
            
            # Draw text
            painter.setPen(QPen(QColor(102, 102, 102)))
            painter.drawText(slot_rect, Qt.AlignmentFlag.AlignCenter, "Drop here")
        
        # Draw "If" text
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.setFont(painter.font())
        font = painter.font()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        text_rect = QRect(int(center_x - 30), 10, 60, 30)  # ← FIX
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "If")
        
        # Draw connection dots
        # Input dot (top)
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawEllipse(QPoint(int(center_x), 8), 8, 8)  # ← FIX
        
        # True output (right-top)
        painter.setBrush(QBrush(QColor(76, 175, 80)))
        painter.drawEllipse(QPoint(self.width() - 8, 40), 8, 8)
        
        # False output (right-bottom)
        painter.setBrush(QBrush(QColor(244, 67, 54)))
        painter.drawEllipse(QPoint(self.width() - 8, self.height() - 40), 8, 8)


    def bind_child(self, child_block):
        """Bind a comparison block to this If block"""
        self.bound_child = child_block
        child_block.parent_block = self
        child_block.raise_()
        self.update_bound_child_position()
        self.update()

    def update_bound_child_position(self):
        """Update the position of the bound child to center it"""
        if self.bound_child:
            center_x = self.x() + (self.width() / 2) - (self.bound_child.width() / 2)
            center_y = self.y() + (self.height() / 2) - (self.bound_child.height() / 2)
            self.bound_child.move(int(center_x), int(center_y))

    def dragEnterEvent(self, event):
        if not self.bound_child:
            self.drop_highlight = True
            self.update()
        event.accept()

    def dragLeaveEvent(self, event):
        self.drop_highlight = False
        self.update()
        event.accept()


class ComparisonBlock(DraggableBlock):
    """Rectangular comparison block"""

    def __init__(self, parent=None, text="A > B"):
        super().__init__(parent)
        self.setFixedSize(90, 40)
        self.text = text

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw rounded rectangle
        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.setBrush(QBrush(QColor(255, 179, 71)))  # Orange
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawRoundedRect(rect, 6, 6)

        # Draw text
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text)


class Canvas(QWidget):
    """Main canvas for spawning and managing blocks"""

    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: white; border: 2px solid #ccc;")
        self.blocks = []

        # Spawn initial blocks
        self.spawn_if_block(100, 100)
        self.spawn_comparison_block(300, 200, "A > B")

    def spawn_if_block(self, x, y):
        """Spawn a new If block"""
        if_block = IfBlock(self)
        if_block.move(x, y)
        if_block.show()
        self.blocks.append(if_block)
        return if_block

    def spawn_comparison_block(self, x, y, text="A > B"):
        """Spawn a new Comparison block"""
        comp_block = ComparisonBlock(self, text)
        comp_block.move(x, y)
        comp_block.show()
        self.blocks.append(comp_block)
        return comp_block


# Example usage
if __name__ == "__main__":
    app = QApplication(sys.argv)

    canvas = Canvas()
    canvas.setWindowTitle("Block Binding System")
    canvas.show()

    sys.exit(app.exec())