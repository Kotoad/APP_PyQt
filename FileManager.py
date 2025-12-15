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
    COMPARE_DIR = "compare"
    PROJECT_EXTENSION = ".project"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        os.makedirs(cls.PROJECTS_DIR, exist_ok=True)
        os.makedirs(cls.AUTOSAVE_DIR, exist_ok=True)
        os.makedirs(cls.COMPARE_DIR, exist_ok=True)
    
    # ========================================================================
    # SAVE OPERATIONS
    # ========================================================================
    
    @classmethod
    def save_project(cls, project_name: str, is_autosave: bool = False, is_compare=False) -> bool:
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
                filename = os.path.join(cls.AUTOSAVE_DIR, project_name + cls.PROJECT_EXTENSION)
            elif is_compare:
                filename = os.path.join(cls.COMPARE_DIR, project_name + "_TEMP" + cls.PROJECT_EXTENSION)
            else:
                filename = os.path.join(cls.PROJECTS_DIR, project_name + cls.PROJECT_EXTENSION)
            
            # Build project data
            project_dict = cls._build_save_data(project_name)
            
            # Write to file
            with open(filename, 'w') as f:
                json.dump(project_dict, f, indent=2)
            
            print(f"✓ Project saved: {filename}")
            return True
            
        except Exception as e:
            print(f"✗ Error saving project: {e}")
            return False
    
    @classmethod
    def _build_save_data(cls, project_name: str) -> dict:
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
                'value_1_name': block_info.get('value_1_name', ''),
                'value_2_name': block_info.get('value_2_name', ''),
                'operator': block_info.get('operator', ''),
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
                'type': var_info.get('type', ''),
                'value': var_info.get('value', ''),
            }
        
        # Build devices data (pure data, no widget references)
        devices_data = {}
        for dev_id, dev_info in Utils.devices.items():
            devices_data[dev_id] = {
                'name': dev_info.get('name', ''),
                'type': dev_info.get('type', 'Output'),
                'pin': dev_info.get('PIN', None),
            }
        metadata = {
            'version': '1.0',
            'name': project_name,
            'created': Utils.project_data.metadata.get('created', 
                      datetime.now().isoformat()),
            'modified': datetime.now().isoformat(),
        }
        
        settings = {
            'rpi_model': Utils.app_settings.rpi_model,
            'rpi_model_index': Utils.app_settings.rpi_model_index,
        }
        
        # Complete project structure
        project_dict = {
            'metadata': metadata,
            'settings': settings,
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
        Utils.project_data.metadata = project_dict.get('metadata', {})
        
        # Load RPI settings
        Utils.project_data.settings = project_dict.get('settings', {})
        
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
              f"{len(Utils.project_data.devices)} devices, "
              f"Settings: {len(Utils.project_data.settings)}"
              f"Metadata: {len(Utils.project_data.metadata)}"
              )
    
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
            'name': 'Untitled',
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat(),
        }
        
        print("✓ New project created")

    @classmethod
    def compare_projects(cls, project_name: str) -> dict:
        """
        Compare current project with saved compare file.
        Returns a dict with detailed change information.
        
        Returns:
            {
                'has_changes': bool,
                'blocks_changed': bool,
                'connections_changed': bool,
                'variables_changed': bool,
                'devices_changed': bool,
                'settings_changed': bool,
                'details': {
                    'blocks': {...},
                    'connections': {...},
                    'variables': {...},
                    'devices': {...},
                    'settings': {...}
                }
            }
        """
        try:
            # Load the compare file
            compare_path = os.path.join(cls.COMPARE_DIR, project_name + "_TEMP" + cls.PROJECT_EXTENSION)
            current_path = os.path.join(cls.PROJECTS_DIR, project_name + cls.PROJECT_EXTENSION)
            if not os.path.exists(compare_path):
                print(f"⚠ Compare file not found: {compare_path}")
                print("  Treating all current data as changes")
                return {
                    'has_changes': True,
                    'blocks_changed': len(Utils.top_infos) > 0,
                    'connections_changed': len(Utils.paths) > 0,
                    'variables_changed': len(Utils.variables) > 0,
                    'devices_changed': len(Utils.devices) > 0,
                    'settings_changed': False,
                    'details': {}
                }
            
            # Load compare file
            with open(compare_path, 'r') as f:
                compare_data = json.load(f)
            
            # Build current project data
            with open(current_path, 'r') as f:
                current_data = json.load(f)
            
            # Compare each section
            result = {
                'has_changes': False,
                'blocks_changed': False,
                'connections_changed': False,
                'variables_changed': False,
                'devices_changed': False,
                'settings_changed': False,
                'details': {
                    'blocks': [],
                    'connections': [],
                    'variables': [],
                    'devices': [],
                    'settings': []
                }
            }
            
            # Compare blocks
            blocks_changed = cls._compare_blocks(
                current_data.get('blocks', {}),
                compare_data.get('blocks', {})
            )
            if blocks_changed:
                print("Blocks changes detected.")
                result['blocks_changed'] = True
                result['details']['blocks'] = blocks_changed
            
            # Compare connections
            connections_changed = cls._compare_connections(
                current_data.get('connections', {}),
                compare_data.get('connections', {})
            )
            if connections_changed:
                print("Connections changes detected.")
                result['connections_changed'] = True
                result['details']['connections'] = connections_changed
            
            # Compare variables
            variables_changed = cls._compare_variables(
                current_data.get('variables', {}),
                compare_data.get('variables', {})
            )
            if variables_changed:
                print("Variables changes detected.")
                result['variables_changed'] = True
                result['details']['variables'] = variables_changed
            
            # Compare devices
            devices_changed = cls._compare_devices(
                current_data.get('devices', {}),
                compare_data.get('devices', {})
            )
            if devices_changed:
                print("Devices changes detected.")
                result['devices_changed'] = True
                result['details']['devices'] = devices_changed
            
            # Compare settings
            settings_changed = cls._compare_settings(
                current_data.get('settings', {}),
                compare_data.get('settings', {})
            )
            if settings_changed:
                print("Settings changes detected.")
                result['settings_changed'] = True
                result['details']['settings'] = settings_changed
            
            # Overall has_changes
            result['has_changes'] = (
                result['blocks_changed'] or 
                result['connections_changed'] or 
                result['variables_changed'] or 
                result['devices_changed'] or 
                result['settings_changed']
            )
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"✗ Error reading compare file: {e}")
            return {'has_changes': True, 'error': str(e)}
        except Exception as e:
            print(f"✗ Error comparing projects: {e}")
            return {'has_changes': True, 'error': str(e)}

    @classmethod
    def _compare_blocks(cls, current: dict, saved: dict) -> list:
        """Compare block data - returns list of changes"""
        changes = []
        print("Comparing blocks...")
        # Check for new blocks
        for block_id in current:
            print(f"Checking block: {block_id}")
            if block_id not in saved:
                print(f"New block detected: {block_id}")
                changes.append(f"✓ New block: {block_id}")
        
        # Check for deleted blocks
        for block_id in saved:
            print(f"Checking saved block: {block_id}")
            if block_id not in current:
                print(f"Deleted block detected: {block_id}")
                changes.append(f"✗ Deleted block: {block_id}")
        
        # Check for modified blocks
        for block_id in current:
            print(f"Checking for modifications in block: {block_id}")
            if block_id in saved:
                print(f"Comparing current {current[block_id]} and saved {saved[block_id]} for block: {block_id}")
                if current[block_id] != saved[block_id]:
                    print(f"Modifications detected in block: {block_id}")
                    changes.append(f"⊕ Modified block: {block_id}")
                    # Detail the changes
                    for key in current[block_id]:
                        if current[block_id].get(key) != saved[block_id].get(key):
                            changes.append(f"    {key}: {saved[block_id].get(key)} → {current[block_id].get(key)}")
        
        return changes

    @classmethod
    def _compare_connections(cls, current: dict, saved: dict) -> list:
        """Compare connection data - returns list of changes"""
        changes = []
        print("Comparing connections...")
        # Check for new connections
        for conn_id in current:
            print(f"Checking connection: {conn_id}")
            if conn_id not in saved:
                print(f"New connection detected: {conn_id}")
                changes.append(f"✓ New connection: {conn_id}")
        
        # Check for deleted connections
        for conn_id in saved:
            print(f"Checking saved connection: {conn_id}")
            if conn_id not in current:
                print(f"Deleted connection detected: {conn_id}")
                changes.append(f"✗ Deleted connection: {conn_id}")
        
        # Check for modified connections
        for conn_id in current:
            print(f"Checking for modifications in connection: {conn_id}")
            if conn_id in saved:
                print(f"Comparing current and saved data for connection: {conn_id}")
                if current[conn_id] != saved[conn_id]:
                    print(f"Modifications detected in connection: {conn_id}")
                    changes.append(f"⊕ Modified connection: {conn_id}")
        
        return changes

    @classmethod
    def _compare_variables(cls, current: dict, saved: dict) -> list:
        """Compare variables data - returns list of changes"""
        changes = []
        
        # Check for new variables
        for var_id in current:
            print(f"Checking variable: {var_id}")
            if var_id not in saved:
                var_name = current[var_id].get('name', 'Unknown')
                print(f"New variable detected: {var_name}")
                changes.append(f"✓ New variable: {var_name}")
        
        # Check for deleted variables
        for var_id in saved:
            print(f"Checking saved variable: {var_id}")
            if var_id not in current:
                var_name = saved[var_id].get('name', 'Unknown')
                print(f"Deleted variable detected: {var_name}")
                changes.append(f"✗ Deleted variable: {var_name}")
        
        # Check for modified variables
        for var_id in current:
            print(f"Checking for modifications in variable: {var_id}")
            if var_id in saved:
                print(f"Comparing current and saved data for variable: {var_id}")
                if current[var_id] != saved[var_id]:
                    print(f"Modifications detected in variable: {var_id}")
                    var_name = current[var_id].get('name', var_id)
                    changes.append(f"⊕ Modified variable: {var_name}")
                    for key in ['value', 'type']:
                        if current[var_id].get(key) != saved[var_id].get(key):
                            changes.append(f"    {key}: {saved[var_id].get(key)} → {current[var_id].get(key)}")
        
        return changes

    @classmethod
    def _compare_devices(cls, current: dict, saved: dict) -> list:
        """Compare devices data - returns list of changes"""
        changes = []
        print("Comparing devices...")
        # Check for new devices
        for dev_id in current:
            print(f"Checking device: {dev_id}")
            if dev_id not in saved:
                print(f"New device detected: {dev_id}")
                dev_name = current[dev_id].get('name', 'Unknown')
                changes.append(f"✓ New device: {dev_name}")
        
        # Check for deleted devices
        for dev_id in saved:
            print(f"Checking saved device: {dev_id}")
            if dev_id not in current:
                print(f"Deleted device detected: {dev_id}")
                dev_name = saved[dev_id].get('name', 'Unknown')
                changes.append(f"✗ Deleted device: {dev_name}")
        
        # Check for modified devices
        for dev_id in current:
            print(f"Checking for modifications in device: {dev_id}")
            if dev_id in saved:
                print(f"Comparing current and saved data for device: {dev_id}")
                if current[dev_id] != saved[dev_id]:
                    print(f"Modifications detected in device: {dev_id}")
                    dev_name = current[dev_id].get('name', dev_id)
                    changes.append(f"⊕ Modified device: {dev_name}")
                    for key in ['pin', 'type']:
                        if current[dev_id].get(key) != saved[dev_id].get(key):
                            changes.append(f"    {key}: {saved[dev_id].get(key)} → {current[dev_id].get(key)}")
        
        return changes

    @classmethod
    def _compare_settings(cls, current: dict, saved: dict) -> list:
        """Compare settings data - returns list of changes"""
        changes = []
        print("Comparing settings...")
        for key in current:
            print(f"Checking setting: {key}")
            if key not in saved:
                print(f"New setting detected: {key}")
                changes.append(f"✓ New setting: {key}")
            elif current[key] != saved[key]:
                print(f"Modification detected in setting: {key}")
                changes.append(f"⊕ {key}: {saved[key]} → {current[key]}")
        
        for key in saved:
            print(f"Checking saved setting: {key}")
            if key not in current:
                print(f"Removed setting detected: {key}")
                changes.append(f"✗ Removed setting: {key}")
        
        return changes

    

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
