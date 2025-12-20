import logging
logger = logging.getLogger(__name__)

# Configuration: Set to True to force PyQt5 only, False to allow PyQt5/PyQt6 auto-detection
QT5_ONLY = True

if QT5_ONLY:
    # Force PyQt5
    from PyQt5 import QtWidgets, QtGui, QtCore
    from PyQt5.QtCore import Qt, QObject, pyqtSignal
    from PyQt5.QtGui import QIntValidator
    from PyQt5.QtWidgets import QWidget, QMainWindow, QAction  # QAction is in QtWidgets for PyQt5
    Key_Return = QtCore.Qt.Key_Return
    from picamera2.previews.qt import QGlPicamera2
else:
    # Auto-detect PyQt6 first, fallback to PyQt5
    try:
        from PyQt6 import QtWidgets, QtGui, QtCore
        from PyQt6.QtCore import Qt, QObject, pyqtSignal
        from PyQt6.QtGui import QIntValidator, QAction  # QAction is in QtGui for PyQt6
        from PyQt6.QtWidgets import QWidget, QMainWindow
        Key_Return = QtCore.Qt.Key.Key_Return
        from picamera2.previews.qt import QGl6Picamera2 as QGlPicamera2
    except ImportError:
        from PyQt5 import QtWidgets, QtGui, QtCore
        from PyQt5.QtCore import Qt, QObject, pyqtSignal
        from PyQt5.QtGui import QIntValidator
        from PyQt5.QtWidgets import QWidget, QMainWindow, QAction  # QAction is in QtWidgets for PyQt5
        Key_Return = QtCore.Qt.Key_Return
        from picamera2.previews.qt import QGlPicamera2

# Debug: confirm which Qt binding is being used
logger.info(f"Using Qt binding: {QtCore.__name__}")