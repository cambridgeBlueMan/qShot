
from qt import QtWidgets, QtGui, QtCore, Qt
class AppSignals(QtCore.QObject):
    mode_changed = QtCore.pyqtSignal(object)  # Pass mode info (dict, index, etc.)

app_signals = AppSignals()