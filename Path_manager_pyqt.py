from Imports import (Qt, QPoint, QLine, QPainter, QPen, QColor, QGraphicsPathItem,
                     QPointF, QPainterPath)
from Imports import get_utils, get_State_Manager

Utils = get_utils()
Statemanager = get_State_Manager()

class PathGraphicsItem(QGraphicsPathItem):
    """Graphics item representing a connection path between blocks"""
    
    def __init__(self, from_block, to_block, path_id, parent_canvas, to_circle_type, from_circle_type):
        super().__init__()
        if from_block == None:
            return
        self.from_block = from_block
        self.to_block = to_block
        self.path_id = path_id
        self.canvas = parent_canvas
        self.to_circle_type = to_circle_type
        self.from_circle_type = from_circle_type
        #print(f"✓ PathGraphicsItem.__init__: {path_id} from {from_block.block_id} to {to_block.block_id}")
        #print(f"   from_circle_type: {from_circle_type}, to_circle_type: {to_circle_type}")
        
        # Style the path
        pen = QPen(QColor(31, 83, 141))
        pen.setWidth(2)
        self.setPen(pen)
        
        self.update_path()
    
    def update_path(self):
        """Recalculate path between blocks"""
        
        # Get block positions and sizes
        from_rect = self.from_block.boundingRect()
        to_rect = self.to_block.boundingRect()
        if self.to_circle_type == 'in':
            to_pos = self.to_block.pos() + QPointF(0, to_rect.height() / 2)
        elif self.to_circle_type == 'in1':
            to_pos = self.to_block.pos() + QPointF(0, 3*(to_rect.height() / 4))
        elif self.to_circle_type == None:
            to_pos = self.to_block.pos() + QPointF(0, to_rect.height() / 2)
            
        if self.from_circle_type == 'out':
            from_pos = self.from_block.pos() + QPointF(from_rect.width(), from_rect.height() / 2)
        elif self.from_circle_type == None:
            from_pos = self.from_block.pos() + QPointF(from_rect.width(), from_rect.height() / 2)
        elif self.from_circle_type == 'out1':
            from_pos = self.from_block.pos() + QPointF(from_rect.width(), from_rect.height() / 4)
        elif self.from_circle_type == 'out2':
            from_pos = self.from_block.pos() + QPointF(from_rect.width(), 3*(from_rect.height() / 4))
        #print(f"   from_pos: {from_pos}, to_pos: {to_pos}")
        # Create orthogonal path
        path = QPainterPath()
        path.moveTo(from_pos)
        
        mid_x = (from_pos.x() + to_pos.x()) / 2
        path.lineTo(mid_x, from_pos.y())
        path.lineTo(mid_x, to_pos.y())
        path.lineTo(to_pos)
        
        self.setPath(path)

    def update_preview_path(self, waypoints):
        """Update path using provided waypoints"""
        path = QPainterPath()
        if not waypoints:
            return
        
        start_point = QPointF(waypoints[0][0], waypoints[0][1])
        path.moveTo(start_point)
        
        for point in waypoints[1:]:
            path.lineTo(QPointF(point[0], point[1]))
        
        self.setPath(path)
    
class PathManager:
    """Manages all path connections between blocks"""
    
    def __init__(self, canvas):
        self.canvas = canvas
        self.start_node = None  # (widget, id, pos, circle_type)
        self.preview_points = []
        self.preview_item = None
        self.state_manager = Statemanager.get_instance()
    
    def start_connection(self, block, circle_center, circle_type):
        """Start a new connection from a block's output circle"""
        #print(f"✓ PathManager.start_connection: {block.block_id} ({circle_type})")
        

        if self.canvas.reference == 'canvas':
            #print(" → Starting from main canvas")
            for block_id, block_info in Utils.main_canvas['blocks'].items():
                if block_info.get('widget') == block:
                    if block_info.get('type') == 'End':
                        print("⚠ Cannot start connection from End block")
                        self.cancel_connection()
                        return
                    for conn_id, conn_type in block_info['out_connections'].items():
                        if conn_type == circle_type:
                            print("⚠ Output already connected on this circle")
                            self.cancel_connection()
                            return
                    self.start_node = {
                        'widget': block,
                        'id': block_id,
                        'pos': circle_center,
                        'circle_type': circle_type
                    }
                    #print(f" → Connection started from {block_id}")
                    break
        elif self.canvas.reference == 'function':
            #print(" → Starting from function canvas")
            for f_id, f_info in Utils.functions.items():
                if self.canvas == f_info.get('canvas'):
                    #print(f"   In function: {f_id}")
                    for block_id, block_info in f_info['blocks'].items():
                        if block_info.get('widget') == block:
                            if block_info.get('type') == 'End':
                                print("⚠ Cannot start connection from End block")
                                self.cancel_connection()
                                return
                            for conn_id, conn_type in block_info['out_connections'].items():
                                if conn_type == circle_type:
                                    print("⚠ Output already connected on this circle")
                                    self.cancel_connection()
                                    return
                            self.start_node = {
                                'widget': block,
                                'id': block_id,
                                'pos': circle_center,
                                'circle_type': circle_type
                            }
                            #print(f" → Connection started from {block_id} in function {f_id}")
                            break
    
    def cancel_connection(self):
        """Cancel the current connection"""
        print("✓ PathManager.cancel_connection")
        
        # Remove preview item
        if self.preview_item is not None:
            self.canvas.scene.removeItem(self.preview_item)
            self.preview_item = None
        
        self.start_node = None
        self.preview_points = []
        self.canvas.scene.update()
        self.state_manager.canvas_state.on_idle()
    
    def finalize_connection(self, block, circle_center, circle_type):
        """Finalize connection to a block's input circle"""
        if not self.start_node:
            print("⚠ No connection started")
            self.cancel_connection()
            return
        
        if self.canvas.reference == 'canvas':
            for block_id, block_info in Utils.main_canvas['blocks'].items():
                if block_info.get('widget') == block:
                    print(f"✓ PathManager.finalize_connection: {block.block_id} ({circle_type})")
                    print(f"input connections: {block_info['in_connections']}, len: {len(block_info['in_connections'].keys())}")
                    for conn_id, conn_type in block_info['in_connections'].items():
                        if conn_type == circle_type:
                            print("⚠ Input already connected")
                            #self.cancel_connection()
                            return
                        print(self.start_node['widget'], block)
                    if self.start_node['widget'] == block:
                        print("⚠ Cannot connect block to itself")
                        #self.cancel_connection()
                        return
                    
        elif self.canvas.reference == 'function':
            for f_id, f_info in Utils.functions.items():
                if self.canvas == f_info.get('canvas'):
                    for block_id, block_info in f_info['blocks'].items():
                        if block_info.get('widget') == block:
                            print(f"✓ PathManager.finalize_connection: {block.block_id} ({circle_type})")
                            print(f"input connections: {block_info['in_connections']}, len: {len(block_info['in_connections'].keys())}")
                            for conn_id, conn_type in block_info['in_connections'].items():
                                if conn_type == circle_type:
                                    print("⚠ Input already connected")
                                    #self.cancel_connection()
                                    return
                            if self.start_node['widget'] == block:
                                print("⚠ Cannot connect block to itself")
                                #self.cancel_connection()
                                return
        #print(f"✓ PathManager.finalize_connection: {block.block_id} ({circle_type})")
        
        # Find target block in Utils
        if self.canvas.reference == 'canvas':
            #print(" → Finalizing to main canvas")
            for block_id, block_info in Utils.main_canvas['blocks'].items():
                if block_info.get('widget') == block:
                    from_block = self.start_node['widget']
                    to_block = block
                    connection_id = f"{self.start_node['id']}-{block_id}"
                    self.canvas.scene.removeItem(self.preview_item)
                    self.preview_item = None
                    # Create path graphics item
                    path_item = PathGraphicsItem(from_block, to_block, connection_id, self.canvas, circle_type, self.start_node['circle_type'])
                    self.canvas.scene.addItem(path_item)
                    
                    # Store in Utils and scene_paths
                    Utils.main_canvas['paths'][connection_id] = {
                        'from': self.start_node['id'],
                        'from_circle_type': self.start_node['circle_type'],
                        'to': block_id,
                        'to_circle_type': circle_type,
                        'waypoints': self.preview_points,
                        'canvas': self.canvas,
                        'color': QColor(31, 83, 141),
                        'item': path_item
                    }
                    Utils.scene_paths[connection_id] = path_item
                    
                    # Update block connection info
                    Utils.main_canvas['blocks'][self.start_node['id']]['out_connections'].setdefault(connection_id, self.start_node['circle_type'])
                    Utils.main_canvas['blocks'][block_id]['in_connections'].setdefault(connection_id, circle_type)
                    
                    #print(f"  → Connection created: {connection_id}")
                    break
        elif self.canvas.reference == 'function':
            #print(" → Finalizing to function canvas")
            for f_id, f_info in Utils.functions.items():
                if self.canvas == f_info.get('canvas'):
                    #print(f"   In function: {f_id}")
                    for block_id, block_info in f_info['blocks'].items():
                        if block_info.get('widget') == block:
                            from_block = self.start_node['widget']
                            to_block = block
                            connection_id = f"{self.start_node['id']}-{block_id}"
                            self.canvas.scene.removeItem(self.preview_item)
                            self.preview_item = None
                            # Create path graphics item
                            path_item = PathGraphicsItem(from_block, to_block, connection_id, self.canvas, circle_type, self.start_node['circle_type'])
                            self.canvas.scene.addItem(path_item)
                            
                            # Store in Utils and scene_paths
                            Utils.functions[f_id]['paths'][connection_id] = {
                                'from': self.start_node['id'],
                                'from_circle_type': self.start_node['circle_type'],
                                'to': block_id,
                                'to_circle_type': circle_type,
                                'waypoints': self.preview_points,
                                'canvas': self.canvas,
                                'color': QColor(31, 83, 141),
                                'item': path_item
                            }
                            Utils.scene_paths[connection_id] = path_item
                            
                            # Update block connection info
                            Utils.functions[f_id]['blocks'][self.start_node['id']]['out_connections'].setdefault(connection_id, self.start_node['circle_type'])
                            Utils.functions[f_id]['blocks'][block_id]['in_connections'].setdefault(connection_id, circle_type)
                            
                            #print(f"  → Connection created: {connection_id}")
                            break
        # Reset
        self.state_manager.canvas_state.on_idle()
        self.preview_points = []
        self.start_node = None
    
    def update_preview_path(self, mouse_pos):
        """Update preview path as mouse moves"""
        if not self.start_node:
            return

        # Calculate waypoints
        self.preview_points = self.calculate_grid_path(
            self.start_node['pos'].x(),
            self.start_node['pos'].y(),
            mouse_pos.x(),
            mouse_pos.y()
        )

        # Create/update preview item if needed
        if self.preview_item is None:
            # CREATE an instance with a dummy path first
            self.preview_item = PathGraphicsItem(
                self.start_node['widget'], 
                self.start_node['widget'],  # temp to_block
                "preview",
                self.canvas,
                None, 
                None
            )
            self.canvas.scene.addItem(self.preview_item)

        # Now update the preview path on the instance
        self.preview_item.update_preview_path(self.preview_points)
        self.canvas.scene.update()

    
    def calculate_grid_path(self, x1, y1, x2, y2):
        """Calculate orthogonal path points snapped to grid"""
        waypoints = [(x1, y1)]
        dx = x2 - x1
        dy = y2 - y1
        
        if abs(dx) >= abs(dy):
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
        
        for path_id, path_item in Utils.scene_paths.items():
            if path_item.from_block == widget or path_item.to_block == widget:
                path_item.update_path()
    
    def remove_paths_for_block(self, block_id):
        """Remove all paths connected to a block"""
        #print(f"✓ PathManager.remove_paths_for_block: {block_id}")
        
        paths_to_remove = []
        
        # Find all connected paths
        for path_id, path_item in list(Utils.scene_paths.items()):
            if path_item.from_block.block_id == block_id or path_item.to_block.block_id == block_id:
                self.canvas.scene.removeItem(path_item)
                paths_to_remove.append(path_id)
        
        # Remove from dictionaries
        for path_id in paths_to_remove:
            if path_id in Utils.paths:
                del Utils.paths[path_id]
            if path_id in Utils.scene_paths:
                del Utils.scene_paths[path_id]
    
    def remove_path(self, path_id):
        """Remove a specific path"""
        if path_id in Utils.scene_paths:
            path_item = Utils.scene_paths[path_id]
            self.canvas.scene.removeItem(path_item)
            del Utils.scene_paths[path_id]
        
        if path_id in Utils.paths:
            del Utils.paths[path_id]
    
    def clear_all_paths(self):
        """Clear all paths"""
        for path_id in list(Utils.scene_paths.keys()):
            self.remove_path(path_id)
        Utils.paths.clear()