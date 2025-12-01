from PyQt6.QtCore import Qt, QPoint, QLine
from PyQt6.QtGui import QPainter, QPen, QColor
import Utils


class PathManager:
    """Manages path connections between blocks"""
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.grid_size = Utils.config['grid_size']
        self.active_path = None
        self.start_node = None
        self.temp_line = None
        self.preview_points = []
        
    def start_connection(self, widget, circle_center, circle_type):
        """Start a connection from a widget's output circle"""
        print(f"\n✓✓✓ start_connection FIRED!")
        print(f"  widget: {widget}, circle_type: {circle_type}")
        print(f"  circle_center: {circle_center}")
        
        for block_id, top_info in Utils.top_infos.items():
            if top_info["widget"] == widget:
                widget_id = block_id
                print(f"  ✓ Found block {widget_id}")
                print("  Setting start_node...")
                self.start_node = {
                    'widget': widget,
                    'id': widget_id,
                    'pos': circle_center,
                    'circle_type': circle_type
                }
                print(f"  start_node is now: {self.start_node}")
                self.canvas.setMouseTracking(True)
                widget.raise_()
                break
        
        if not self.start_node:
            print(f"  ⚠ WARNING: start_node is still None after loop!")
    
    def cancel_connection(self):
        """Cancel the current connection"""
        print("Cancelling connection...")
        self.temp_line = None
        self.preview_points = []
        self.start_node = None
        self.canvas.update()
        print(f"✓ Cleanup complete. start_node={self.start_node}, preview_points={self.preview_points}")
    
    def update_preview_path(self, mouse_pos):
        """Update temporary path preview as mouse moves"""
        if not self.start_node:
            return
        
        mouse_x = mouse_pos.x()
        mouse_y = mouse_pos.y()
        
        # Calculate path
        waypoints = self.calculate_grid_path(
            self.start_node['pos'][0],
            self.start_node['pos'][1],
            mouse_x,
            mouse_y
        )
        
        self.preview_points = waypoints
        self.canvas.update()
    
    def finalize_connection(self, widget, circle_center, circle_type):
        """Finalize connection to a widget's input circle"""
        print("Finalizing connection...")
        if not self.start_node:
            return
        for block_id, top_info in Utils.top_infos.items():
            if top_info["widget"] == widget and circle_type not in ('in1'):
                widget_id = block_id
                print(f"  ✓ Found block {widget_id} for finalization")
                print("Invalid connection: Cannot connect to this circle type.")
                self.cancel_connection()
                return
    
        print(self.start_node)
        print(circle_center, circle_type)
        # Calculate final path
        waypoints = self.calculate_grid_path(
            self.start_node['pos'][0],
            self.start_node['pos'][1],
            circle_center[0],
            circle_center[1]
        )
        
        # Create permanent connection
        for block_id, top_info in Utils.top_infos.items():
            if top_info["widget"] == widget:
                widget_id = block_id
                connection_id = f"{self.start_node['id']}_{widget_id}"
                
                Utils.paths[connection_id] = {
                    'line': None,  # Will be drawn by canvas
                    'waypoints': waypoints,
                    'from': self.start_node['widget'],
                    'to': widget,
                    'from_circle': self.start_node['circle_type'],
                    'to_circle': circle_type,
                    'color': QColor(31, 83, 141)  # Blue color
                }
                
                Utils.top_infos[self.start_node['id']]['out_connections'].append(connection_id)
                Utils.top_infos[widget_id]['in_connections'].append(connection_id)
                
                print(f"Connection created: {connection_id}")
                print(f"Path info {Utils.paths[connection_id]}")
                break
        
        # Cleanup
        self.preview_points = []
        self.start_node = None
        self.canvas.update()
    
    def calculate_grid_path(self, x1, y1, x2, y2):
        """Generate orthogonal path following grid"""
        # Snap to grid
        #x1 = round(x1 / self.grid_size) * self.grid_size
        #y1 = round(y1 / self.grid_size) * self.grid_size
        #x2 = round(x2 / self.grid_size) * self.grid_size
        #y2 = int(y2 // self.grid_size) * self.grid_size
        
        # Create L-shaped path
        waypoints = [(x1, y1)]
        
        dx = x2 - x1
        dy = y2 - y1
        
        if abs(dx) > abs(dy):
            # Horizontal first
            mid_x = x1 + dx // 2
            waypoints.append((mid_x, y1))
            waypoints.append((mid_x, y2))
        else:
            # Vertical first
            mid_y = y1 + dy // 2
            waypoints.append((x1, mid_y))
            waypoints.append((x2, mid_y))
        
        waypoints.append((x2, y2))
        return waypoints
  
    def draw_path(self, painter, waypoints, color=None, width=2, dashed=False):
        """Draw path on canvas"""
        if not waypoints or len(waypoints) < 2:
            return
        
        pen = QPen(color if color else QColor(31, 83, 141))
        pen.setWidth(width)
        
        if dashed:
            pen.setStyle(Qt.PenStyle.DashLine)
        else:
            pen.setStyle(Qt.PenStyle.SolidLine)
        
        painter.setPen(pen)
        
        for i in range(len(waypoints) - 1):
            x1, y1 = waypoints[i]
            x2, y2 = waypoints[i + 1]
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
    
    def draw_all_paths(self, painter):
        """Draw all permanent paths"""
        for conn_id, path_data in Utils.paths.items():
            self.draw_path(
                painter,
                path_data['waypoints'],
                path_data.get('color', QColor(31, 83, 141)),
                width=2
            )
        
        # Draw preview path if active
        if self.preview_points:
            self.draw_path(
                painter,
                self.preview_points,
                QColor(100, 149, 237),  # Lighter blue for preview
                width=2,
                dashed=True
            )
    
    def get_circle_position(self, widget, circle_type):
        """Get the center position of the specified circle on the widget"""
        canvas_widget_pos = self.canvas.mapFromGlobal(widget.mapToGlobal(QPoint(0, 0)))
        widget_x = canvas_widget_pos.x()
        widget_y = canvas_widget_pos.y()
        widget_width = widget.width()
        widget_height = widget.height()
        print(f"widget.x()={widget.x()}, widget.y()={widget.y()}")
        print(f"canvas.x()={self.canvas.x()}, canvas.y()={self.canvas.y()}")
        
        if circle_type == 'in':
            # Left side, center
            print("Getting 'in' circle position")
            return (widget_x + 10, widget_y + widget_height // 2)
        elif circle_type == 'in1':
            print("Getting 'in1' circle position")
            circle_y = widget_y + 3 * (widget_height - 2 * (widget_height // 6)) // 4 + (widget_height // 6) + 3
            return (widget_x + 10, circle_y)
        elif circle_type == 'out':
            print("Getting 'out' circle position")
            # Right side, center (for Start, End, Timer)
            return (widget_x + widget_width - 10, widget_y + widget_height // 2)
        elif circle_type == 'out1':
            print("Getting 'out1' circle position")
            # Upper right circle (for If block)
            circle_y = widget_y + (widget_height - 2 * (widget_height // 6)) // 4 + (widget_height // 6) - 3
            return (widget_x + widget_width - 10, circle_y)
        elif circle_type == 'out2':
            print("Getting 'out2' circle position")
            # Lower right circle (for If block)
            circle_y = widget_y + 3 * (widget_height - 2 * (widget_height // 6)) // 4 + (widget_height // 6) + 3
            return (widget_x + widget_width - 10, circle_y)
        else:
            print("Getting default circle position")
            # Default fallback
            return (widget_x + widget_width - 10, widget_y + widget_height // 2)
    
    def update_paths_for_widget(self, widget):
        """Recalculate paths when element moves"""
        print(f"Updating paths for moved widget: {widget}")
        print(f"Current paths: {Utils.paths}")
        for conn_id, path_data in Utils.paths.items():
            if path_data['from'] == widget or path_data['to'] == widget:
                # Get new positions using specific circle types
                from_pos = self.get_circle_position(
                    path_data['from'],
                    path_data['from_circle']
                )
                print(f"from_pos: {from_pos}")
                to_pos = self.get_circle_position(
                    path_data['to'],
                    path_data['to_circle']
                )
                print(f"to_pos: {to_pos}")
                # Recalculate path
                new_waypoints = self.calculate_grid_path(
                    from_pos[0], from_pos[1],
                    to_pos[0], to_pos[1]
                )
                
                path_data['waypoints'] = new_waypoints
        
        self.canvas.update()
