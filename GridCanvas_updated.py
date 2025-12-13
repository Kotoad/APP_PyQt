# COMPLETE UPDATED GridCanvas CLASS WITH PAN AND ZOOM
# Replace your existing GridCanvas class in GUI_pyqt.py with this code

class GridCanvas(QWidget):
    """Canvas widget with grid and draggable widgets - WITH PAN AND ZOOM"""

    def __init__(self, parent=None, grid_size=25):
        super().__init__(parent)
        self.grid_size = grid_size
        self.dragged_widget = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.rightClickMenu = None
        self.rightClickPos = None
        self.spawner = spawning_elements(self)
        self.path_manager = PathManager(self)
        self.elements_events = element_events(self)
        self.file_manager = FileManager()

        # ✨ PAN AND ZOOM TRACKING
        self.pan_x = 0              # Horizontal pan offset in pixels
        self.pan_y = 0              # Vertical pan offset in pixels
        self.zoom_level = 1.0       # Zoom scale factor (1.0 = 100%)
        self.min_zoom = 0.1         # Minimum zoom (10%)
        self.max_zoom = 5.0         # Maximum zoom (500%)
        self.zoom_speed = 0.1       # How fast to zoom per scroll increment
        
        # Middle-click pan tracking
        self.is_panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0

        # Setup widget
        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Style
        self.setStyleSheet("""
            GridCanvas {
                background-color: #2B2B2B;
            }
        """)

    def paintEvent(self, event):
        """Draw grid lines and connection paths with pan/zoom applied"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # ✨ APPLY TRANSFORM: Pan and Zoom
        painter.translate(self.pan_x, self.pan_y)
        painter.scale(self.zoom_level, self.zoom_level)

        # Draw grid
        pen = QPen(QColor("#3A3A3A"))
        pen.setWidth(1)
        painter.setPen(pen)

        # Calculate visible grid area (accounting for pan and zoom)
        start_x = -self.pan_x / self.zoom_level
        start_y = -self.pan_y / self.zoom_level
        end_x = start_x + self.width() / self.zoom_level
        end_y = start_y + self.height() / self.zoom_level

        # Vertical lines
        x = (int(start_x / self.grid_size) * self.grid_size)
        while x < end_x:
            painter.drawLine(x, start_y, x, end_y)
            x += self.grid_size

        # Horizontal lines
        y = (int(start_y / self.grid_size) * self.grid_size)
        while y < end_y:
            painter.drawLine(start_x, y, end_x, y)
            y += self.grid_size

        # Draw all connection paths
        self.path_manager.draw_all_paths(painter)

        # Draw preview path while connecting
        if self.path_manager.preview_points:
            self.path_manager.draw_path(
                painter,
                self.path_manager.preview_points,
                QColor(100, 149, 237),
                width=2,
                dashed=True
            )

    def wheelEvent(self, event):
        """Handle mouse wheel for zoom in/out"""
        # Get scroll direction (positive = up, negative = down)
        delta = event.angleDelta().y()

        # Calculate zoom change
        if delta > 0:
            # Scroll up = zoom in
            new_zoom = self.zoom_level + self.zoom_speed
        else:
            # Scroll down = zoom out
            new_zoom = self.zoom_level - self.zoom_speed

        # Clamp zoom to min/max values
        self.zoom_level = max(self.min_zoom, min(new_zoom, self.max_zoom))

        self.update()  # Redraw with new zoom
        event.accept()

    def mousePressEvent(self, event):
        """Handle mouse press - detect middle click for panning"""
        print("✓ GridCanvas.mousePressEvent fired!")
        print(f" Position: {event.pos()}")

        # ✨ NEW: Check for middle-click (pan start)
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = True
            self.pan_start_x = event.pos().x()
            self.pan_start_y = event.pos().y()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)  # Visual feedback
            event.accept()
            return

        # Existing right-click handling
        if event.button() == Qt.MouseButton.RightButton:
            self.rightClickPos = event.pos()
            self.handleRightClick(event)
            event.accept()
            return

        # Call the existing one if you had it, or let it propagate
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move - pan canvas or update path preview"""
        # ✨ NEW: Handle panning with middle mouse button
        if self.is_panning:
            # Calculate movement delta
            delta_x = event.pos().x() - self.pan_start_x
            delta_y = event.pos().y() - self.pan_start_y

            # Update pan offset
            self.pan_x += delta_x
            self.pan_y += delta_y

            # Update start position for next frame
            self.pan_start_x = event.pos().x()
            self.pan_start_y = event.pos().y()

            self.update()  # Redraw canvas
            event.accept()
            return

        # Existing path preview code
        if self.path_manager.start_node:
            self.path_manager.update_preview_path(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release - stop panning"""
        if event.button() == Qt.MouseButton.MiddleButton:
            if self.is_panning:
                self.is_panning = False
                self.setCursor(Qt.CursorShape.ArrowCursor)  # Reset cursor
                event.accept()
                return

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        """Handle keyboard events - added zoom reset"""
        # Optional: Reset zoom and pan with keyboard shortcut
        if event.key() == Qt.Key.Key_Home:
            # Reset to default view
            self.pan_x = 0
            self.pan_y = 0
            self.zoom_level = 1.0
            self.update()
            event.accept()
            return

        # Existing key handling
        if self.spawner and self.spawner.element_placed:
            if event.key() in [Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Enter]:
                self.spawner.stop_placing(self)
                event.accept()
            else:
                event.ignore()
        elif self.path_manager.start_node:
            if event.key() == Qt.Key.Key_Escape:
                self.path_manager.cancel_connection()
                self.update()
                event.accept()
            else:
                event.ignore()
        else:
            super().keyPressEvent(event)

    # ============ SNAP TO GRID ============

    def snap_to_grid(self, x, y, widget=None, during_drag=False):
        """Snap coordinates to nearest grid intersection"""
        if widget and not during_drag:
            height = widget.height()
            grid_height = round(height / self.grid_size) * self.grid_size

            if height > grid_height:
                grid_height += self.grid_size
            elif height < self.grid_size:
                grid_height = self.grid_size

            if height == self.grid_size:
                height_offset = grid_height / 2
            else:
                height_offset = (grid_height - height) / 2
        else:
            height_offset = 0

        snapped_x = int(round(x / self.grid_size) * self.grid_size)
        snapped_y = int(round(y / self.grid_size) * self.grid_size + height_offset)

        return snapped_x, snapped_y

    def add_draggable_widget(self, widget):
        """Make a widget draggable on the canvas"""
        widget.setParent(self)
        widget.show()
        widget.raise_()

        # Store original mouse press handler
        original_press = widget.mousePressEvent
        original_move = widget.mouseMoveEvent
        original_release = widget.mouseReleaseEvent

        def on_press(event):
            if event.button() == Qt.MouseButton.LeftButton:
                # Check if on circle BEFORE setting dragged_widget
                circle_type = self.elements_events.check_click_on_circle(widget, event.pos())
                if not circle_type:  # Only set dragged_widget if NOT on circle
                    self.on_canvas_click(event, widget)
                event.accept()
            original_press(event)

        def on_move(event):
            if event.buttons() & Qt.MouseButton.LeftButton:
                self.on_canvas_drag(event, widget)
            event.accept()
            original_move(event)

        def on_release(event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.on_canvas_release(event, widget)
            original_release(event)

        widget.mousePressEvent = on_press
        widget.mouseMoveEvent = on_move
        widget.mouseReleaseEvent = on_release

    def on_canvas_click(self, event, widget):
        """Handle mouse click on widget"""
        print(f"Pressed {type(self).__name__}")
        for block_id, widget_info in Utils.top_infos.items():
            if widget_info['widget'] is widget:
                self.offset_x = event.pos().x()
                self.offset_y = event.pos().y()
                self.dragged_widget = widget_info
                self.is_dragging = True
                widget.raise_()
                print(f"Click {self.mousePressEvent}")
                break

    def on_canvas_drag(self, event, widget):
        """Handle dragging of widgets"""
        if self.dragged_widget and self.dragged_widget['widget'] is widget:
            global_pos = widget.mapToGlobal(event.pos())
            canvas_pos = self.mapFromGlobal(global_pos)

            new_x = canvas_pos.x() - self.offset_x
            new_y = canvas_pos.y() - self.offset_y

            widget.move(new_x, new_y)
            self.dragged_widget['x'] = new_x
            self.dragged_widget['y'] = new_y

            # Update paths
            self.path_manager.update_paths_for_widget(widget)
            self.update()

    def on_canvas_release(self, event, widget):
        """Handle mouse release - snap to grid"""
        if self.dragged_widget and self.dragged_widget['widget'] is widget:
            snapped_x, snapped_y = self.snap_to_grid(
                self.dragged_widget['x'],
                self.dragged_widget['y'],
                widget,
                during_drag=False
            )

            widget.move(snapped_x, snapped_y)
            self.dragged_widget['x'] = snapped_x
            self.dragged_widget['y'] = snapped_y
            self.dragged_widget = None
            self.is_dragging = False
            self.update()
            self.path_manager.update_paths_for_widget(widget)
            print(f"Release {self.mousePressEvent}")

    # ============ RIGHT CLICK CONTEXT MENU ============

    def handleRightClick(self, event):
        """Determine what was clicked and show appropriate menu"""
        pos = event.pos()

        # 1. Check if clicked on a block
        clickedBlock = self.getBlockAtPosition(pos)
        if clickedBlock:
            self.showBlockContextMenu(clickedBlock, pos)
            return

        # 2. Check if clicked on a path
        clickedPath = self.getPathAtPosition(pos)
        if clickedPath:
            self.showPathContextMenu(clickedPath, pos)
            return

        # 3. Empty canvas area
        self.showCanvasContextMenu(pos)

    def getBlockAtPosition(self, pos):
        """Check if click position is on any block widget"""
        for block_id, block_info in Utils.top_infos.items():
            widget = block_info.get('widget')
            if not widget:
                continue

            block_Rect = widget.geometry()
            if block_Rect.contains(pos):
                return widget

        return None

    def getPathAtPosition(self, pos, tolerance=5):
        """Check if click position is near any path"""
        if not Utils.paths:
            return None

        clickPoint = pos

        # Iterate through all paths
        for path_id, path_Info in Utils.paths.items():
            points = path_Info['waypoints']

            if len(points) < 2:
                continue

            # Check each line segment in the path
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]

                dist = self.distancePointToLineSegment(clickPoint, p1, p2)

                if dist <= tolerance:
                    return path_Info

        return None

    def distancePointToLineSegment(self, point, lineStart, lineEnd):
        """Calculate shortest distance from point to line segment"""
        x0, y0 = point.x(), point.y()
        x1, y1 = lineStart[0], lineStart[1]
        x2, y2 = lineEnd[0], lineEnd[1]

        numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        denominator = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)

        if denominator == 0:
            return math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)

        return numerator / denominator

    def showBlockContextMenu(self, block, pos):
        """Show context menu for blocks"""
        menu = QMenu(self)

        blockid = None
        for bid, info in Utils.top_infos.items():
            if info.get('widget') is block:
                blockid = bid
                break

        edit_Action = QAction("Edit Block", self)
        edit_Action.triggered.connect(lambda: self.editBlock(block, blockid))
        menu.addAction(edit_Action)

        duplicate_Action = QAction("Duplicate", self)
        duplicate_Action.triggered.connect(lambda: self.duplicateBlock(block, blockid))
        menu.addAction(duplicate_Action)

        menu.addSeparator()

        delete_Action = QAction("Delete Block", self)
        delete_Action.triggered.connect(lambda: self.deleteBlock(block, blockid))
        menu.addAction(delete_Action)

        menu.exec(self.mapToGlobal(pos))

    def showPathContextMenu(self, pathInfo, pos):
        """Show context menu for paths/connections"""
        menu = QMenu(self)

        startBlock = pathInfo.get('startBlock')
        endBlock = pathInfo.get('endBlock')

        info_Action = QAction(f"Connection", self)
        info_Action.setEnabled(False)
        menu.addAction(info_Action)

        menu.addSeparator()

        delete_Path_Action = QAction("Delete Connection", self)
        delete_Path_Action.triggered.connect(lambda: self.deletePath(pathInfo))
        menu.addAction(delete_Path_Action)

        menu.exec(self.mapToGlobal(pos))

    def showCanvasContextMenu(self, pos):
        """Show context menu for empty canvas area"""
        menu = QMenu(self)

        addBlockAction = QAction("Add Block", self)
        addBlockAction.triggered.connect(lambda: MainWindow.open_elements_window(self.main_window))
        menu.addAction(addBlockAction)

        menu.addSeparator()

        clearAllAction = QAction("Clear Canvas", self)
        clearAllAction.triggered.connect(self.clearCanvas)
        menu.addAction(clearAllAction)

        menu.exec(self.mapToGlobal(pos))

    # ============ ACTION HANDLERS ============

    def editBlock(self, block, blockid):
        """Edit block properties"""
        print(f"Editing block: {blockid} of type {block.blocktype}")

    def duplicateBlock(self, block, blockid):
        """Create a copy of the block"""
        print(f"Duplicating block: {blockid}")

        if blockid not in Utils.top_infos:
            return

        block_data = Utils.top_infos[blockid]

        blocktype = block_data.get('type')
        x = block_data.get('x', 0) + 50
        y = block_data.get('y', 0) + 50

        value1 = block_data.get('value1', '')
        value2 = block_data.get('value2', '')
        combovalue = block_data.get('combovalue', '')

        if hasattr(self, 'spawner') and self.spawner:
            print(f"Creating duplicate of {blocktype} at ({x}, {y})")

    def deleteBlock(self, block, blockid):
        """Delete a block and its connections"""
        print(f"Deleting block: {blockid}")

        if blockid not in Utils.top_infos:
            return

        if hasattr(self, 'path_manager'):
            self.path_manager.removePathsForBlock(blockid)

        block.setParent(None)
        block.deleteLater()

        del Utils.top_infos[blockid]

        self.update()
        print(f"Block {blockid} deleted")

    def deletePath(self, pathInfo):
        """Delete a connection path"""
        print("Deleting path connection")
        print(f"Path info: {pathInfo}")

        if hasattr(self, 'path_manager'):
            for path_id, pInfo in Utils.paths.items():
                if pInfo == pathInfo:
                    self.path_manager.remove_path(path_id)
                    return

    def clearCanvas(self):
        """Clear all blocks and connections"""
        reply = QMessageBox.question(
            self,
            "Clear Canvas",
            "Are you sure you want to delete all blocks and connections?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            for blockid in list(Utils.top_infos.keys()):
                widget = Utils.top_infos[blockid].get('widget')
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()

                del Utils.top_infos[blockid]

            if hasattr(self, 'path_manager'):
                self.path_manager.clear_all_paths()

            self.update()
            print("Canvas cleared")
