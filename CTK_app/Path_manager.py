import Utils

class PathManager:
    def __init__(self, canvas):
        self.canvas = canvas
        self.grid_size = Utils.config['grid_size']
        self.active_path = None
        self.start_node = None
        self.temp_line = None
        self.is_obstacle = lambda n, obstacles: True  # Placeholder for obstacle checking
        
    def start_connection(self, widget, circle_center, circle_type):
        """Called when user clicks 'in' circle"""
        for block_id, top_info in Utils.top_infos.items():
            if top_info["widget"] == widget:
                widget_id = block_id
                
        print("Starting connection...")
        self.start_node = {
            'widget': widget,
            'id': widget_id,
            'pos': circle_center,
            'circle_type': circle_type
        }
        
        # Bind mouse motion to canvas
        widget.lift()
        self.canvas.bind('<Motion>', self.update_preview_path)
        
        # Bind Escape to canvas instead of widget
        self.canvas.bind('<Escape>', lambda e: self.cancel_connection(widget))
        
        # Give canvas focus so it can receive keyboard events
        self.canvas.focus_set()

    def cancel_connection(self, widget):
        """Cancel the current connection process"""
        print("Cancelling connection...")
        if self.temp_line:
            self.canvas.delete(self.temp_line)
            self.temp_line = None
        
        self.canvas.unbind('<Motion>')
        self.canvas.unbind('<Escape>')  # Unbind from canvas
        self.start_node = None
    
    def update_preview_path(self, event):
        """Update temporary path as mouse moves"""
        if not self.start_node:
            return
            
        # Get mouse position in canvas coordinates
        mouse_x = self.canvas.canvasx(event.x)
        mouse_y = self.canvas.canvasy(event.y)
        print(f"Mouse moved to: ({mouse_x}, {mouse_y})")
        print(f"Start node position: {self.start_node['pos']}")
        # Calculate path
        waypoints = self.calculate_grid_path(
            self.start_node['pos'][0], 
            self.start_node['pos'][1],
            mouse_x, 
            mouse_y
        )
        
        
        # Delete old preview
        if self.temp_line:
            self.canvas.delete(self.temp_line)
        
        # Draw new preview path
        self.temp_line = self.draw_path(waypoints, color='blue', dash=(5, 3))
        
    def finalize_connection(self, widget, circle_center, circle_type):
        print("Finalizing connection...")
        """Called when user clicks 'out' circle"""
        if not self.start_node:
            return
        
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
        line_id = self.draw_path(waypoints, color='blue', width=2)
        
        Utils.paths[connection_id] = {
            'line': line_id,
            'waypoints': waypoints,
            'from': self.start_node['widget'],
            'to': widget,
            'from_circle': self.start_node['circle_type'],
            'to_circle': circle_type
        }
        
        Utils.top_infos[self.start_node['id']]['out_connections'].append(connection_id)
        Utils.top_infos[widget_id]['in_connections'].append(connection_id)
        print(Utils.paths)
        print(Utils.top_infos)
        # Cleanup
        if self.temp_line:
            self.canvas.delete(self.temp_line)
            self.temp_line = None
        self.canvas.unbind('<Motion>')
        self.start_node = None
        
    def calculate_grid_path(self, x1, y1, x2, y2):
        """Generate orthogonal path following grid"""
        # Snap to grid
        x1 = round(x1 / self.grid_size) * self.grid_size
        y1 = round(y1 / self.grid_size) * self.grid_size
        x2 = round(x2 / self.grid_size) * self.grid_size
        y2 = round(y2 / self.grid_size) * self.grid_size
        
        # Create L-shaped path with optional middle segment
        waypoints = [(x1, y1)]
        
        # Calculate middle point based on direction
        dx = x2 - x1
        dy = y2 - y1
        
        if abs(dx) > abs(dy):
            # Primarily horizontal - go horizontal first
            mid_x = x1 + dx // 2
            waypoints.append((mid_x, y1))
            waypoints.append((mid_x, y2))
        else:
            # Primarily vertical - go vertical first
            mid_y = y1 + dy // 2
            waypoints.append((x1, mid_y))
            waypoints.append((x2, mid_y))
        
        waypoints.append((x2, y2))
        
        return waypoints
    
    def draw_path(self, waypoints, color='blue', width=2, dash=None):
        """Draw path on canvas from waypoints"""
        coords = []
        for x, y in waypoints:
            coords.extend([x, y])
        
        return self.canvas.create_line(
            *coords, 
            fill=color, 
            width=width,
            dash=dash,
            smooth=False,  # Keep right angles
            tags='connection_path'
        )
    
    def get_circle_position(self, widget, circletype):
        '''Get the center position of the specified circle on the widget'''
        widget_x = widget.winfo_x()
        widget_y = widget.winfo_y()
        widget_width = widget.winfo_width()
        widget_height = widget.winfo_height()
        
        canvas_x = widget_x - self.canvas.winfo_rootx()
        canvas_y = widget_y - self.canvas.winfo_rooty()
        
        if circletype == 'in':
            # Left side, center
            return (canvas_x + 10, canvas_y + widget_height // 2)
        elif circletype == 'out':
            # Right side, center (for Start, End, Timer)
            return (canvas_x + widget_width - 10, canvas_y + widget_height // 2)
        elif circletype == 'out1':
            # Upper right circle (for If block)
            circle_y = canvas_y + (widget_height - 2 * (widget_height // 6)) // 4 + (widget_height // 6)
            return (canvas_x + widget_width - 10, circle_y)
        elif circletype == 'out2':
            # Lower right circle (for If block)
            circle_y = canvas_y + 3 * (widget_height - 2 * (widget_height // 6)) // 4 + (widget_height // 6)
            return (canvas_x + widget_width - 10, circle_y)
        else:
            # Default fallback
            return (canvas_x + widget_width - 10, canvas_y + widget_height // 2)
    
    def update_paths_for_widget(self, widget):
        """Recalculate paths when element moves"""
        for conn_id, path_data in Utils.paths.items():
            if path_data['from'] == widget or path_data['to'] == widget:
                # Get new positions using SPECIFIC circle types
                from_pos = self.get_circle_position(
                    path_data['from'], 
                    path_data['from_circle']  # ← Use stored circle type
                )
                to_pos = self.get_circle_position(
                    path_data['to'], 
                    path_data['to_circle']  # ← Use stored circle type
                )
                
                # Recalculate path
                new_waypoints = self.calculate_grid_path(
                    from_pos[0], from_pos[1], 
                    to_pos[0], to_pos[1]
                )
                
                # Update drawing
                self.canvas.delete(path_data['line'])
                path_data['line'] = self.draw_path(new_waypoints, color='blue', width=2)
                path_data['waypoints'] = new_waypoints
