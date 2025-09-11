from PyQt6.QtCore import QObject, pyqtSignal

class AppSignals(QObject):
    mode_changed = pyqtSignal(object)  # Pass mode info (dict, index, etc.)

app_signals = AppSignals()