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