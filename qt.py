try:
    from PyQt6 import QtWidgets, QtGui, QtCore
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIntValidator
except ImportError:
    from PyQt5 import QtWidgets, QtGui, QtCore
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QIntValidator

# In qt.py
try:
    from PyQt6 import QtCore
    Key_Return = QtCore.Qt.Key.Key_Return
except ImportError:
    from PyQt5 import QtCore
    Key_Return = QtCore.Qt.Key_Return