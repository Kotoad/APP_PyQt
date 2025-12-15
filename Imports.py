"""
Imports.py - Centralized Import Manager

All imports in ONE place to avoid circular dependencies.
Every other file imports from this file.

This is the SINGLE SOURCE OF TRUTH for imports.
"""

# ============================================================================
# STANDARD LIBRARY IMPORTS
# ============================================================================
import sys
import os
import json
import subprocess
import ctypes
import math
import time
from datetime import datetime
from ctypes import windll, wintypes, byref
from pathlib import Path

# ============================================================================
# PYQT6 IMPORTS
# ============================================================================
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QPushButton, QLabel, QFrame, QScrollArea,
    QLineEdit, QComboBox, QDialog, QTabWidget, QFileDialog, QMessageBox,
    QInputDialog, QStyleOptionComboBox, QStyledItemDelegate, QTextEdit,
    QSplitter, QTreeWidget, QTreeWidgetItem, QListWidget, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsPathItem, QGraphicsItem, QGraphicsPixmapItem
)
from PyQt6.QtCore import (
    Qt, QPoint, QRect, QSize, pyqtSignal, QRegularExpression, QTimer, QEvent,
    pyqtProperty, QEasingCurve, QRectF, QPropertyAnimation, QObject, QLine, QCoreApplication,
    QSortFilterProxyModel, QAbstractAnimation, QPointF, QRectF
)
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QBrush, QPalette, QMouseEvent,
    QRegularExpressionValidator, QFont, QPixmap, QImage, QStandardItem,
    QIntValidator, QPainterPath, QIcon, QStandardItemModel, QAction, QPixmap
)
# ============================================================================
# PROJECT-SPECIFIC IMPORTS (Internal)
# ============================================================================

# Data structures and settings (NO GUI DEPENDENCIES - safe to import)
from App_settings import AppSettings
from Project_Data import ProjectData

# Path and connection management
def get_utils():
    """Lazy import Utils - called only when needed to avoid circular import"""
    import Utils
    return Utils

def get_gui_main_window():
    """Lazy import GUI MainWindow - avoid circular deps"""
    from GUI_pyqt import MainWindow
    return MainWindow

def get_code_compiler():
    """Lazy import CodeCompiler - avoid circular import"""
    from code_compiler import CodeCompiler
    return CodeCompiler

def get_spawn_elements():
    """Lazy import spawning_elements and Elements_events - avoid circular import"""
    from spawn_elements_pyqt import spawning_elements, Elements_events, BlockGraphicsItem
    return BlockGraphicsItem, spawning_elements, Elements_events

def get_device_settings_window():
    """Lazy import DeviceSettingsWindow - avoid circular import"""
    from settings_window import DeviceSettingsWindow
    return DeviceSettingsWindow

def get_path_manager():
    """Lazy import PathManager - avoid circular import"""
    from Path_manager_pyqt import PathManager, PathGraphicsItem
    return PathManager, PathGraphicsItem

def get_Elements_Window():
    """Lazy import ElementsWindow - avoid circular import"""
    from Elements_window_pyqt import ElementsWindow
    return ElementsWindow

def get_Help_Window():
    """Lazy import HelpWindow - avoid circular import"""
    from Help_window import HelpWindow
    return HelpWindow()
# ============================================================================
# LAZY IMPORTS (Imported only when needed to avoid circular deps)
# ============================================================================
# These are imported inside functions/methods where needed:
# - FileManager (imported in methods, not at module level)
# - Utils (imported carefully, after AppSettings)

def get_utils():
    """Lazy import Utils to avoid circular dependency"""
    import Utils
    return Utils

def get_file_manager():
    """Lazy import FileManager when needed"""
    from FileManager import FileManager
    return FileManager

# ============================================================================
# EXPORT ALL IMPORTANT ITEMS
# ============================================================================
__all__ = [
    # Standard library
    'sys', 'os', 'json', 'datetime', 'Path',
    'windll', 'wintypes', 'byref',
    
    # PyQt6 widgets
    'QApplication', 'QMainWindow', 'QWidget', 'QVBoxLayout', 'QHBoxLayout',
    'QMenuBar', 'QMenu', 'QPushButton', 'QLabel', 'QFrame', 'QScrollArea',
    'QLineEdit', 'QComboBox', 'QDialog', 'QTabWidget', 'QFileDialog', 
    'QMessageBox', 'QInputDialog', 'QSplitter', 'QTreeWidget', 'QTreeWidgetItem',
    'QTextEdit',
    
    # PyQt6 core
    'Qt', 'QPoint', 'QRect', 'QSize', 'pyqtSignal', 'QRegularExpression', 
    'QTimer', 'QLineF', 'QPropertyAnimation', 'QEasingCurve', 'QRectF',
    'QObject', 'QAbstractAnimation', 'QStandardItem',
    
    # PyQt6 GUI
    'QPainter', 'QPen', 'QColor', 'QBrush', 'QPalette', 'QMouseEvent',
    'QRegularExpressionValidator', 'QFont', 'QIcon', 'QPixmap', 'QImage',
    
    # Project data & settings
    'AppSettings', 'ProjectData',
    
    # Project modules (directly imported - safe)
    'PathManager', 'ElementsWindow', 'FileManager',
    
    # Lazy loaders (call these functions to import)
    'get_utils', 'get_gui_main_window', 'get_code_compiler',
    'get_spawn_elements', 'get_device_settings_window',
    'get_spawning_elements', 'get_elements_events',
]
