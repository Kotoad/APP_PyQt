"""
FileManager.py - Complete Save/Load System for Visual Programming Projects

Handles serialization and deserialization of projects with proper separation
of persistent data (JSON-safe) and runtime references (QWidget objects).
"""
from Imports import (json, os, datetime, Path, get_utils, ProjectData)

Utils = get_utils()


class FileManager:
    """Manages project file operations with auto-save capabilities"""
    
    # Directory structure
    PROJECTS_DIR = "projects"
    AUTOSAVE_DIR = "autosave"
    PROJECT_EXTENSION = ".project"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        os.makedirs(cls.PROJECTS_DIR, exist_ok=True)
        os.makedirs(cls.AUTOSAVE_DIR, exist_ok=True)
    
    # ========================================================================
    # SAVE OPERATIONS
    # ========================================================================
    
    @classmethod
    def save_project(cls, project_name: str, is_autosave: bool = False) -> bool:
        """
        Save current project to file
        
        Args:
            project_name: Name of project (without extension)
            is_autosave: If True, save to autosave folder, else projects folder
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cls.ensure_directories()
            
            # Determine save location
            if is_autosave:
                filename = os.path.join(cls.AUTOSAVE_DIR, "autosave" + cls.PROJECT_EXTENSION)
            else:
                filename = os.path.join(cls.PROJECTS_DIR, project_name + cls.PROJECT_EXTENSION)
            
            # Build project data
            project_dict = cls._build_save_data()
            
            # Write to file
            with open(filename, 'w') as f:
                json.dump(project_dict, f, indent=2)
            
            print(f"✓ Project saved: {filename}")
            return True
            
        except Exception as e:
            print(f"✗ Error saving project: {e}")
            return False
    
    @classmethod
    def _build_save_data(cls) -> dict:
        """
        Build complete project data for serialization
        
        Converts all runtime data to pure JSON-safe format
        """
        # Build blocks data (WITHOUT widget references)
        blocks_data = {}
        for block_id, block_info in Utils.top_infos.items():
            blocks_data[block_id] = {
                'type': block_info['type'],
                'x': block_info['x'],
                'y': block_info['y'],
                'width': block_info['width'],
                'height': block_info['height'],
                'value_1': block_info.get('value_1', ''),
                'value_2': block_info.get('value_2', ''),
                'combo_value': block_info.get('combo_value', ''),
                'switch_value': block_info.get('switch_value', ''),
                'in_connections': block_info.get('in_connections', []),
                'out_connections': block_info.get('out_connections', []),
            }
        
        # Build connections data (using block IDs, NOT widget references)
        connections_data = {}
        for conn_id, conn_info in Utils.paths.items():
            connections_data[conn_id] = {
                'from_block': cls._get_block_id_from_widget(conn_info['from']),
                'from_circle': conn_info.get('from_circle', 'out'),
                'to_block': cls._get_block_id_from_widget(conn_info['to']),
                'to_circle': conn_info.get('to_circle', 'in'),
                'waypoints': conn_info.get('waypoints', []),
                'color': 'blue',  # Store as string, not QColor object
            }
        
        # Build variables data (pure data, no widget references)
        variables_data = {}
        for var_id, var_info in Utils.variables.items():
            variables_data[var_id] = {
                'name': var_info.get('name', ''),
                'type': var_info.get('type', 'int'),
                'value': var_info.get('value', ''),
                'pin': var_info.get('PIN', None),
            }
        
        # Build devices data (pure data, no widget references)
        devices_data = {}
        for dev_id, dev_info in Utils.devices.items():
            devices_data[dev_id] = {
                'name': dev_info.get('name', ''),
                'type': dev_info.get('type', 'Output'),
                'pin': dev_info.get('PIN', None),
            }
        
        # Complete project structure
        project_dict = {
            'metadata': {
                'version': '1.0',
                'created': Utils.project_data.metadata.get('created', 
                          datetime.now().isoformat()),
                'modified': datetime.now().isoformat(),
                'rpi_model': Utils.app_settings.rpi_model,
                'rpi_model_index': Utils.app_settings.rpi_model_index,
            },
            'blocks': blocks_data,
            'connections': connections_data,
            'variables': variables_data,
            'devices': devices_data,
        }
        
        return project_dict
    
    @classmethod
    def _get_block_id_from_widget(cls, widget) -> str:
        """Get block ID from widget reference"""
        for block_id, block_info in Utils.top_infos.items():
            if block_info['widget'] is widget:
                return block_id
        return "unknown"
    
    # ========================================================================
    # LOAD OPERATIONS
    # ========================================================================
    
    @classmethod
    def load_project(cls, project_name: str, is_autosave: bool = False) -> bool:
        """
        Load project from file and populate Utils
        
        Args:
            project_name: Name of project (without extension)
            is_autosave: If True, load from autosave folder
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cls.ensure_directories()
            
            # Determine load location
            if is_autosave:
                filename = os.path.join(cls.AUTOSAVE_DIR, "autosave" + cls.PROJECT_EXTENSION)
            else:
                filename = os.path.join(cls.PROJECTS_DIR, project_name + cls.PROJECT_EXTENSION)
            
            # Check if file exists
            if not os.path.exists(filename):
                print(f"✗ Project file not found: {filename}")
                return False
            
            # Load JSON
            with open(filename, 'r') as f:
                project_dict = json.load(f)
            
            # Populate Utils with loaded data (PURE DATA ONLY)
            cls._populate_utils_from_save(project_dict)
            
            print(f"✓ Project loaded: {filename}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON file: {e}")
            return False
        except Exception as e:
            print(f"✗ Error loading project: {e}")
            return False
    
    @classmethod
    def _populate_utils_from_save(cls, project_dict: dict):
        """
        Populate Utils with loaded data
        
        Does NOT create widgets - only populates persistent data.
        Widgets are created by GUI_pyqt.rebuild_from_data()
        """
        
        # Clear existing data
        Utils.project_data = ProjectData()
        
        # Load metadata
        metadata = project_dict.get('metadata', {})
        Utils.project_data.metadata = metadata
        
        # Load RPI settings
        if 'rpi_model' in metadata:
            Utils.app_settings.rpi_model = metadata['rpi_model']
            Utils.app_settings.rpi_model_index = metadata.get('rpi_model_index', 6)
        
        # Load blocks (pure data only)
        Utils.project_data.blocks = project_dict.get('blocks', {})
        
        # Load connections (pure data only)
        Utils.project_data.connections = project_dict.get('connections', {})
        
        # Load variables
        Utils.project_data.variables = project_dict.get('variables', {})
        
        # Load devices
        Utils.project_data.devices = project_dict.get('devices', {})
        
        print(f"✓ Data loaded: {len(Utils.project_data.blocks)} blocks, "
              f"{len(Utils.project_data.connections)} connections, "
              f"{len(Utils.project_data.variables)} variables, "
              f"{len(Utils.project_data.devices)} devices")
    
    # ========================================================================
    # UTILITY OPERATIONS
    # ========================================================================
    
    @classmethod
    def list_projects(cls) -> list:
        """List all saved projects"""
        cls.ensure_directories()
        projects = []
        
        for filename in os.listdir(cls.PROJECTS_DIR):
            if filename.endswith(cls.PROJECT_EXTENSION):
                project_name = filename[:-len(cls.PROJECT_EXTENSION)]
                filepath = os.path.join(cls.PROJECTS_DIR, filename)
                modified = os.path.getmtime(filepath)
                projects.append({
                    'name': project_name,
                    'path': filepath,
                    'modified': datetime.fromtimestamp(modified),
                })
        
        return sorted(projects, key=lambda x: x['modified'], reverse=True)
    
    @classmethod
    def delete_project(cls, project_name: str) -> bool:
        """Delete a saved project"""
        try:
            filepath = os.path.join(cls.PROJECTS_DIR, project_name + cls.PROJECT_EXTENSION)
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"✓ Project deleted: {project_name}")
                return True
            else:
                print(f"✗ Project not found: {project_name}")
                return False
        except Exception as e:
            print(f"✗ Error deleting project: {e}")
            return False
    
    @classmethod
    def project_exists(cls, project_name: str) -> bool:
        """Check if a project file exists"""
        filepath = os.path.join(cls.PROJECTS_DIR, project_name + cls.PROJECT_EXTENSION)
        return os.path.exists(filepath)
    
    # ========================================================================
    # NEW PROJECT
    # ========================================================================
    
    @classmethod
    def new_project(cls):
        """Initialize a new empty project"""
        # Clear all data
        Utils.top_infos.clear()
        Utils.paths.clear()
        Utils.variables.clear()
        Utils.devices.clear()
        Utils.var_items.clear()
        Utils.dev_items.clear()
        Utils.vars_same.clear()
        Utils.devs_same.clear()
        
        # Reset project data
        Utils.project_data = ProjectData()
        Utils.project_data.metadata = {
            'version': '1.0',
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat(),
        }
        
        print("✓ New project created")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage:
    
    # Save current project
    FileManager.save_project("motor_control")
    
    # Load existing project
    if FileManager.load_project("motor_control"):
        print("Project loaded successfully")
    
    # List all projects
    projects = FileManager.list_projects()
    for project in projects:
        print(f"{project['name']} - Modified: {project['modified']}")
    
    # Delete a project
    FileManager.delete_project("old_project")
    
    # Auto-save
    FileManager.save_project("my_project", is_autosave=True)
    """
    pass
