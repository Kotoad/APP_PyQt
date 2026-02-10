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
import threading
import paramiko
import subprocess
import ctypes
import math
import time
import warnings
from datetime import datetime
from ctypes import windll, wintypes, byref
from pathlib import Path

# ============================================================================
# PYQT6 IMPORTS
# ============================================================================
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QProgressBar,
    QMenuBar, QMenu, QPushButton, QLabel, QFrame, QScrollArea,QSizePolicy,  
    QLineEdit, QComboBox, QDialog, QTabWidget, QFileDialog, QMessageBox, QScroller,
    QInputDialog, QStyleOptionComboBox, QStyledItemDelegate, QTextEdit, QProgressDialog,
    QSplitter, QTreeWidget, QTreeWidgetItem, QListWidget, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsPathItem, QGraphicsItem, QGraphicsPixmapItem, QGraphicsObject,
    QListWidgetItem, QStackedWidget, QGraphicsObject, QGraphicsEllipseItem, QSplashScreen
)
from PyQt6.QtCore import (
    Qt, QPoint, QRect, QSize, pyqtSignal, QRegularExpression, QTimer, QEvent,
    pyqtProperty, QEasingCurve, QRectF, QPropertyAnimation, QObject, QLine, QCoreApplication,
    QSortFilterProxyModel, QAbstractAnimation, QPointF, QRectF, QThread,
)
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QBrush, QPalette, QMouseEvent, QKeySequence, QShortcut, QEventPoint,
    QRegularExpressionValidator, QFont, QPixmap, QImage, QStandardItem, QMovie, QTouchEvent,
    QIntValidator, QPainterPath, QIcon, QStandardItemModel, QAction, QPixmap, QInputDevice, QCursor
)
from PyQt6.QtTest import QTest
# ============================================================================
# PROJECT-SPECIFIC IMPORTS (Internal)
# ============================================================================

# Data structures and settings (NO GUI DEPENDENCIES - safe to import)
from App_settings import AppSettings
from Project_Data import ProjectData

def get_gui():
    """Lazy import GUI MainWindow - avoid circular deps"""
    from GUI_pyqt import MainWindow, GridCanvas
    return MainWindow, GridCanvas

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
    return HelpWindow

def get_State_Machine():
    """Lazy import AppStateMachine - avoid circular import"""
    from state_machine import AppStateMachine, CanvasStateMachine
    return AppStateMachine, CanvasStateMachine

def get_State_Manager():
    """Lazy import StateManager - avoid circular import"""
    from state_manager import StateManager
    return StateManager

def get_CodeViewer_Window():
    """Lazy import CodeViewerWindow - avoid circular import"""
    from Code_view_window import CodeViewerWindow
    return CodeViewerWindow

def get_Translation_Manager():
    """Lazy import TranslationManager - avoid circular import"""
    from Translation_manager import TranslationManager
    return TranslationManager

def get_Data_Control():
    """Lazy import DataControl - avoid circular import"""
    from Data_control import DataControl
    return DataControl

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

