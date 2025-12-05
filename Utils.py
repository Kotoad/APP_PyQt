from ctypes import windll, wintypes, byref

# ============================================================================
# GLOBAL DICTIONARIES - Data Storage for the Visual Programming System
# ============================================================================

# TOP-LEVEL BLOCKS DATA STRUCTURE
# Purpose: Stores metadata for every visual block placed on the canvas
# Key: block_id (unique identifier for each block)
# Value: Dictionary containing block properties and connections
# 
# Structure:
# {
#     'block_id_1': {
#         'widget': QWidget,              # Reference to the PyQt widget (for rendering)
#         'id': 'block_id_1',             # Block identifier (redundant but useful for lookups)
#         'type': 'If' | 'While' | 'Timer' | 'Start' | 'End',  # Block type
#         'x': int,                       # X position on canvas (snapped to grid)
#         'y': int,                       # Y position on canvas (snapped to grid)
#         'width': int,                   # Block width in pixels
#         'height': int,                  # Block height in pixels
#         'in_connections': [],           # List of connection_ids pointing TO this block
#         'out_connections': [],          # List of connection_ids originating FROM this block
#         'value_1': str,                  # Primary input value (variable name, condition, etc)
#         'value_2': str,                  # Secondary input value (comparison value, timer duration)
#         'combo_value': str              # Combo box selection (comparison operator like '==', '>')
#     },
#     'block_id_2': { ... },
#     ...
# }
# 
# Example Usage:
#   Utils.top_infos['block_123'] = {
#       'widget': block_widget,
#       'id': 'block_123',
#       'type': 'If',
#       'x': 100, 'y': 200,
#       'width': 100, 'height': 36,
#       'in_connections': ['conn_1'],
#       'out_connections': ['conn_2', 'conn_3'],
#       'value_1': 'temperature',
#       'value_2': '50',
#       'combo_value': '>'
#   }
top_infos = {}

# CONNECTION PATHS DATA STRUCTURE
# Purpose: Stores visual connection lines between blocks
# Key: connection_id (unique identifier for each connection/path)
# Value: Dictionary containing line properties and waypoints
#
# Structure:
# {
#     'connection_id_1': {
#         'line': line_id,                # Reference to the drawn line (PyQt object)
#         'waypoints': [(x1, y1), (x2, y2), ...],  # Points the connection path goes through
#         'from': block_widget,           # Reference to source block widget
#         'to': block_widget              # Reference to target block widget
#         'from_circle': 'out' | 'out1' | 'out2',  # Which output circle on source block
#         'to_circle': 'in' | 'in1'       # Which input circle on target block
#         'color': QColor(...)             # Color of the connection line
#
#     },
#     'connection_id_2': { ... },
#     ...
# }
#
# Why Waypoints? Connections don't go straight - they bend to avoid overlapping blocks
# and create a visual flow (like Scratch/Blockly connections)
#
# Example Usage:
#   Utils.paths['conn_1'] = {
#       'line': line_obj,
#       'waypoints': [(150, 36), (150, 100), (100, 100)],  # Path from point to point
#       'from': block_widget_1,
#       'to': block_widget_2
#       'from_circle': 'out',
#       'to_circle': 'in',
#       'color': QColor(31, 83, 141)  # Blue color
#   }
paths = {}

# VARIABLES DATA STRUCTURE
# Purpose: Stores all user-defined variables in the program
# Key: variable_id (unique identifier for each variable)
# Value: Dictionary containing variable metadata
#
# Structure:
# {
#     'var_id_1': {
#         'name': '',          # User-friendly variable name (shown in UI)
#         'type': 'int' | 'float' | 'bool' | 'string',  # Variable data type
#         'value': initial_value,        # Current value of the variable
#         'PIN': 5                        # GPIO PIN number (for Raspberry Pi)
#         'name_imput': QComboBox      # Reference to the name input widget
#         'type_input': QComboBox     # Reference to the type selection widget
#         'value_input': QLineEdit    # Reference to the value input widget
#     },
#     ...
# }
#
# Why Both ID and Name? The ID is unique and never changes. The name is what users see.
# This allows renaming variables without breaking block connections.
#
# Example Usage:
#   Utils.variables['var_1'] = {
#       'name': 'sensor_value',
#       'type': 'int',
#       'value': 0,
#       'PIN': 5
#       'name_input': name_combo_box,
#       'type_input': type_combo_box,
#       'value_input': value_line_edit,
#   }
#   # Later, get the variable's PIN
#   pin = Utils.variables['var_1']['PIN']  # Returns 5
variables = {}

# DEVICES DATA STRUCTURE
# Purpose: Stores all user-defined devices in the program
# Key: device_id (unique identifier for each device)
# Value: Dictionary containing device metadata
# {
#     'device_id_1': {
#         'name': '',          # User-friendly device name (shown in UI)
#         'type': 'Output' | 'Input' | 'PWM',  # Device type
#         'PIN': 5,            # GPIO PIN number (for Raspberry Pi)
#     },
#     ...
# }
devices = {}

# VARIABLES WITH SAME NAME TRACKING
# Purpose: Handles cases where multiple variables might have the same name
# This is a lookup optimization to quickly check if a name is already used
# Key: variable_name (string)
# Value: list of variable_ids with that name
#
# Structure:
# {
#     'temperature': ['var_id_1', 'var_id_4'],  # Multiple vars can have same name
#     'motor_speed': ['var_id_2'],
#     ...
# }
#
# Why Track Duplicates? Allows you to quickly find all variables with a given name
# without iterating through the entire variables dict
#
# Example Usage:
#   # Find all variables named 'temperature'
#   temp_vars = Utils.vars_same.get('temperature', [])
vars_same = {}

# DEVICES WITH SAME NAME TRACKING
# Purpose: Handles cases where multiple devices might have the same name
# This is a lookup optimization to quickly check if a name is already used
# Key: device_name (string)
# Value: list of device_ids with that name
# Structure:
# { 
#     'led_light': ['dev_id_1', 'dev_id_3'],  # Multiple devices can have same name
#     'motor': ['dev_id_2'],
#     ...
# }

devs_same = {}

# VARIABLE UI ITEMS MAPPING
# Purpose: Maps variable IDs to their visual representation in combo boxes/dropdowns
# Used to populate "If" and "While" block variable selectors
# Key: variable_id (unique identifier) OR special key '--'
# Value: Display name (what user sees in the dropdown)
#
# Structure:
# {
#     'var_id_1': 'temperature',          # Maps ID to display name
#     'var_id_2': 'motor_speed',
#     '--': '-- select variable --',      # Special placeholder entry
#     ...
# }
#
# Why Separate from variables{}? This is UI-specific. When you populate a dropdown,
# you want quick lookup of what text to display for each variable ID.
#
# Example Usage:
#   # Populate combo box with variable names
#   for var_id, var_name in Utils.var_items.items():
#       if var_id != '--':  # Skip placeholder
#           combo_box.addItem(var_name, var_id)  # Text: var_name, Data: var_id
var_items = {}

# DEVICE UI ITEMS MAPPING
# Purpose: Maps device IDs to their visual representation in combo boxes/dropdowns
# Used to populate device selection dropdowns
# Key: device_id (unique identifier) OR special key '--'
# Value: Display name (what user sees in the dropdown)
# Structure:
# {
#     'dev_id_1': 'led_light',          # Maps ID to display name
#     'dev_id_2': 'motor',
#     '--': '-- select device --',      # Special placeholder entry
#     ...
# }

dev_items = {}

# CONFIGURATION DATA STRUCTURE
# Purpose: Stores application-wide settings and constants
# These are used for snapping to grid, scaling, etc.
#
# Structure:
# {
#     'grid_size': 25,                    # Snap-to-grid pixel size (blocks align to 25px grid)
#     'other_setting': value,             # Add more config as needed
# }
#
# Why a Config Dict? Centralizes all configurable values. If you need to change grid size,
# you update ONE place instead of searching through code for magic numbers.
#
# Example Usage:
#   # Snap a position to grid
#   snapped_x = (x // Utils.config['grid_size']) * Utils.config['grid_size']
config = {
    'grid_size': 25,                        # Snap-to-grid pixel size (blocks align to 25px grid)
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_dpi_for_monitor(window_id):
    """
    Get DPI scaling factors for the monitor containing the window.
    
    Why Use This?
    - Different monitors have different DPI (dots per inch)
    - Modern high-resolution displays need scaling to render UI elements at correct size
    - Example: A 27" 1440p monitor has ~110 DPI, needs 1.15x scaling for readability
    - Example: A 15" laptop with 4K has ~294 DPI, needs ~3x scaling
    
    Args:
        window_id: Native window handle (HWND on Windows)
    
    Returns:
        Tuple[float, float]: (scaling_factor_x, scaling_factor_y)
        - (1.0, 1.0) = 96 DPI (standard, no scaling)
        - (1.5, 1.5) = 144 DPI (150% scale - high-res display)
        - (2.0, 2.0) = 192 DPI (200% scale - very high-res display)
    
    Edge Cases (What To Watch For):
        - If DPI query fails, returns (1.0, 1.0) as safe default
        - Works on Windows; other platforms need different implementation
        - Window spanning multiple monitors: uses nearest monitor's DPI
    
    Example Usage:
        scale_x, scale_y = get_dpi_for_monitor(hwnd)
        scaled_font_size = 12 * scale_x
        scaled_block_width = 100 * scale_x
    """
    DPI_100_PC = 96  # Windows standard DPI (100% scale) - baseline reference
    
    try:
        # Get handle for monitor containing the window
        # MONITOR_DEFAULTTONEAREST (2) = use nearest monitor if window spans multiple displays
        monitor = windll.user32.MonitorFromWindow(window_id, 2)
        
        # Create variables to hold DPI values (Windows API requirement)
        dpi_x = wintypes.UINT()
        dpi_y = wintypes.UINT()
        
        # Query the monitor's DPI
        # MDT_EFFECTIVE_DPI = 0 (what the user actually sees, accounting for overrides)
        windll.shcore.GetDpiForMonitor(monitor, 0, byref(dpi_x), byref(dpi_y))
        
        # Calculate scaling: 144 DPI display = 144/96 = 1.5x scale
        scaling_factor_x = dpi_x.value / DPI_100_PC
        scaling_factor_y = dpi_y.value / DPI_100_PC
        
        return (scaling_factor_x, scaling_factor_y)
    
    except Exception:
        # Defaults if unable to get DPI
        # Reasons this might fail:
        #   - Running on non-Windows platform
        #   - Windows API unavailable
        #   - Window handle invalid
        # Safe fallback: assume no scaling needed (96 DPI standard)
        return (1.0, 1.0)