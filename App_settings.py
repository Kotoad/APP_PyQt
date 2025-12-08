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