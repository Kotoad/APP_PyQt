"""
Path_manager_pyqt.py - UPDATED FOR QGraphicsView
Simplified path management with graphics items
"""

from Imports import Qt, QPoint, QLine, QPainter, QPen, QColor
from Imports import getutils

Utils = getutils()


class PathManager:
    """Manages path connections between blocks in graphics view"""
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.start_node = None
        self.preview_points = []
        self.grid_size = Utils.config.get('grid_size', 25)
        self.scene_paths = {}  # path_id -> PathGraphicsItem
    
    def start_connection(self, widget, circle_center, circle_type):
        """Start a new connection from a widget's output circle"""
        print(f"Starting connection from {widget.block_id}")
        
        # Find block in canvas
        for block_id, top_info in Utils.top_infos.items():
            if top_info['widget'] == widget:
                self.start_node = {
                    'widget': widget,
                    'id': block_id,
                    'pos': circle_center,
                    'circle_type': circle_type
                }
                print(f"Connection started from block {block_id}")
                break
    
    def cancel_connection(self):
        """Cancel the current connection"""
        print("Cancelling connection...")
        self.start_node = None
        self.preview_points = []
        self.canvas.scene.update()
    
    def finalize_connection(self, widget, circle_center, circle_type):
        """Finalize connection to a widget's input circle"""
        if not self.start_node:
            return
        
        print(f"Finalizing connection to {widget.block_id}")
        
        # Find target block
        for block_id, top_info in Utils.top_infos.items():
            if top_info['widget'] == widget:
                connection_id = f"{self.start_node['id']}-{block_id}"
                
                # Create path graphics item
                from_block = self.start_node['widget']
                to_block = widget
                
                # Import graphics item class
                from GUI_pyqt_updated import PathGraphicsItem
                
                path_item = PathGraphicsItem(from_block, to_block, connection_id, self.canvas)
                self.canvas.scene.addItem(path_item)
                
                # Store in Utils and scene_paths
                Utils.paths[connection_id] = {
                    'from': self.start_node['id'],
                    'to': block_id,
                    'waypoints': self.preview_points,
                    'color': QColor(31, 83, 141),
                    'item': path_item
                }
                
                self.scene_paths[connection_id] = path_item
                
                # Store connection references in blocks
                Utils.top_infos[self.start_node['id']]['out_connections'] = \
                    Utils.top_infos[self.start_node['id']].get('out_connections', [])
                Utils.top_infos[self.start_node['id']]['out_connections'].append(connection_id)
                
                Utils.top_infos[block_id]['in_connections'] = \
                    Utils.top_infos[block_id].get('in_connections', [])
                Utils.top_infos[block_id]['in_connections'].append(connection_id)
                
                print(f"Connection created: {connection_id}")
                
                # Reset
                self.preview_points = []
                self.start_node = None
                break
    
    def update_preview_path(self, mouse_pos):
        """Update preview path as mouse moves"""
        if not self.start_node:
            return
        
        # Simple preview - just store points
        self.preview_points = self.calculate_grid_path(
            self.start_node['pos'][0],
            self.start_node['pos'][1],
            mouse_pos.x(),
            mouse_pos.y()
        )
        
        self.canvas.scene.update()
    
    def calculate_grid_path(self, x1, y1, x2, y2):
        """Calculate orthogonal path points"""
        # Snap to grid
        x1 = round(x1 / self.grid_size) * self.grid_size
        y1 = round(y1 / self.grid_size) * self.grid_size
        x2 = round(x2 / self.grid_size) * self.grid_size
        y2 = round(y2 / self.grid_size) * self.grid_size
        
        waypoints = [(x1, y1)]
        
        dx = x2 - x1
        dy = y2 - y1
        
        if abs(dx) > abs(dy):
            # Horizontal first
            mid_x = x1 + dx / 2
            waypoints.append((mid_x, y1))
            waypoints.append((mid_x, y2))
        else:
            # Vertical first
            mid_y = y1 + dy / 2
            waypoints.append((x1, mid_y))
            waypoints.append((x2, mid_y))
        
        waypoints.append((x2, y2))
        return waypoints
    
    def update_paths_for_widget(self, widget):
        """Update all paths connected to a widget"""
        block_id = widget.block_id
        
        # Find all connected paths
        for path_id, path_item in self.scene_paths.items():
            if path_item.from_block == widget or path_item.to_block == widget:
                path_item.update_path()  # Graphics item updates itself
    
    def remove_paths_for_block(self, block_id):
        """Remove all paths connected to a block"""
        print(f"Removing paths for block {block_id}")
        
        paths_to_remove = []
        
        for path_id, path_item in list(self.scene_paths.items()):
            if (path_item.from_block.block_id == block_id or 
                path_item.to_block.block_id == block_id):
                self.canvas.scene.removeItem(path_item)
                paths_to_remove.append(path_id)
        
        # Clean up Utils.paths
        for path_id in paths_to_remove:
            if path_id in Utils.paths:
                del Utils.paths[path_id]
            if path_id in self.scene_paths:
                del self.scene_paths[path_id]
    
    def remove_path(self, path_id):
        """Remove a specific path"""
        if path_id in self.scene_paths:
            path_item = self.scene_paths[path_id]
            self.canvas.scene.removeItem(path_item)
            del self.scene_paths[path_id]
        
        if path_id in Utils.paths:
            del Utils.paths[path_id]
    
    def clear_all_paths(self):
        """Clear all paths"""
        for path_id in list(self.scene_paths.keys()):
            self.remove_path(path_id)
        
        Utils.paths.clear()
