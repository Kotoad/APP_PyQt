"""
AppSettings.py - Application Settings

Separate from GUI_pyqt to avoid circular imports:
FileManager → Utils → AppSettings (no GUI dependency!)
"""
from Imports import os, json


class AppSettings:
    """Application-wide settings (RPI model, preferences, etc)"""
    
    def __init__(self):
        self.rpi_model = "RPI 4 model B"  # Default
        self.rpi_model_index = 6           # Index in combo box
    
    def to_dict(self):
        return {
            'rpi_model': self.rpi_model,
            'rpi_model_index': self.rpi_model_index,
        }
    
    @classmethod
    def from_dict(cls, data):
        s = cls()
        s.rpi_model = data.get('rpi_model', 'RPI 4 model B')
        s.rpi_model_index = data.get('rpi_model_index', 6)
        return s
    
    def save_to_file(self, filename='app_settings.json'):
        """Save settings to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            print(f"✓ Settings saved to {filename}")
        except Exception as e:
            print(f"✗ Error saving settings: {e}")
    
    @classmethod
    def load_from_file(cls, filename='app_settings.json'):
        """Load settings from JSON file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    data = json.load(f)
                return cls.from_dict(data)
            else:
                return cls()  # Return default if file doesn't exist
        except Exception as e:
            print(f"✗ Error loading settings: {e}")
            return cls()  # Return default on error