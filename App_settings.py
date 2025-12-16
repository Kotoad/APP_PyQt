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
        
        self.rpi_host = "raspberrypi.local"
        self.rpi_user = "kryst"
        self.rpi_password = "9Vv5WmDn"
        self.rpi_model_name = ""
        self.rpi_os = ""
        self.auto_detected = False
    
    def to_dict(self):
        return {
            'rpi_model': self.rpi_model,
            'rpi_model_index': self.rpi_model_index,
            'rpi_host': self.rpi_host,
            'rpi_user': self.rpi_user,
            'rpi_password': self.rpi_password,
            'use_ssh_key': self.use_ssh_key,
            'ssh_key_path': self.ssh_key_path
        }
    
    @classmethod
    def from_dict(cls, data):
        s = cls()
        s.rpi_model = data.get('rpi_model', 'RPI 4 model B')
        s.rpi_model_index = data.get('rpi_model_index', 6)
        s.rpi_host = data.get('rpi_host', 'raspberrypi.local')
        s.rpi_user = data.get('rpi_user', 'pi')
        s.rpi_password = data.get('rpi_password', '')
        s.use_ssh_key = data.get('use_ssh_key', True)
        s.ssh_key_path = data.get('ssh_key_path', '~/.ssh/id_rsa')
        return s