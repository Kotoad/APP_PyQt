class ProjectData:
    """Holds all serializable project information"""
    
    def __init__(self):
        self.main_canvas = {
            'blocks': {},
            'paths': {}
        }        # Pure block data (no QWidget refs)
        self.functions = {}          # Pure function data
        self.canvases = {}          # All canvas data
        self.variables = {}     # Pure variable data
        self.devices = {}       # Pure device data
        self.settings = {}      # App settings (RPI model, etc)
        self.metadata = {}     # Additional metadata (version, crafred, modified)

    def to_dict(self):
        """Convert to serializable dict"""
        return {
            'main_canvas': self.main_canvas,
            'functions': self.functions,
            'canvases': self.canvases,
            'variables': self.variables,
            'devices': self.devices,
            'settings': self.settings,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Reconstruct from dict"""
        project = cls()
        project.main_canvas = data.get('main_canvas', {})
        project.functions = data.get('functions', {})
        project.variables = data.get('variables', {})
        project.canvases = data.get('canvases', {})
        project.devices = data.get('devices', {})
        project.settings = data.get('settings', {})
        project.metadata = data.get('metadata', {})
        return project