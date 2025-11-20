try:
    from PyQt6 import QtWidgets, QtGui, QtCore
    from PyQt6.QtCore import Qt, QObject, pyqtSignal
    from PyQt6.QtGui import QIntValidator
except ImportError:
    from PyQt5 import QtWidgets, QtGui, QtCore
    from PyQt5.QtCore import Qt, QObject, pyqtSignal
    from PyQt5.QtGui import QIntValidator

try:
    from PyQt6 import QtCore
    Key_Return = QtCore.Qt.Key.Key_Return
except ImportError:
    from PyQt5 import QtCore
    Key_Return = QtCore.Qt.Key_Return

try:
    from PyQt6 import QtCore, QtGui, QtWidgets
    from picamera2.previews.qt import QGl6Picamera2 as QGlPicamera2
except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets
    from picamera2.previews.qt import QGlPicamera2