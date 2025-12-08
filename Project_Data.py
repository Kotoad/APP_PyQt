class ProjectData:
    """Holds all serializable project information"""
    
    def __init__(self):
        self.blocks = {}        # Pure block data (no QWidget refs)
        self.connections = {}   # Pure connection data
        self.variables = {}     # Pure variable data
        self.devices = {}       # Pure device data
        self.settings = {}      # App settings (RPI model, etc)
        self.metadata = {}     # Additional metadata (version, crafred, modified)

    def to_dict(self):
        """Convert to serializable dict"""
        return {
            'blocks': self.blocks,
            'connections': self.connections,
            'variables': self.variables,
            'devices': self.devices,
            'settings': self.settings,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Reconstruct from dict"""
        project = cls()
        project.blocks = data.get('blocks', {})
        project.connections = data.get('connections', {})
        project.variables = data.get('variables', {})
        project.devices = data.get('devices', {})
        project.settings = data.get('settings', {})
        project.metadata = data.get('metadata', {})
        return project