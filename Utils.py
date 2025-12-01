from ctypes import windll, wintypes, byref
top_infos = {}# {top_id: {'widget': top,'id': block_id,'type': type,'x': snapped_x,'y': snapped_y,'width': width,'height': height,'in_connections': [],'out_connections': []}}
paths = {}#{connection_id{'line': line_id, 'waypoints': waypoints, 'from': self.start_node['widget'], 'to': widget}}
variables = {}# {'var_name': {'name': name, 'PIN': PIN}}
vars_same = {}
var_items = {}

config = {
    'grid_size': 25,
}

def get_dpi_for_monitor(window_id):
        DPI_100_PC = 96
        try:
            # Get handle for monitor containing the window
            monitor = windll.user32.MonitorFromWindow(window_id, 2)  # MONITOR_DEFAULTTONEAREST
            dpi_x = wintypes.UINT()
            dpi_y = wintypes.UINT()
            # MDT_EFFECTIVE_DPI = 0
            windll.shcore.GetDpiForMonitor(monitor, 0, byref(dpi_x), byref(dpi_y))
            scaling_factor_x = dpi_x.value / DPI_100_PC
            scaling_factor_y = dpi_y.value / DPI_100_PC
            return (scaling_factor_x, scaling_factor_y)
        except Exception:
            # Defaults if unable to get DPI
            return (1.0, 1.0)