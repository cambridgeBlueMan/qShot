from qt import QtCore

class AppSignals(QtCore.QObject):
    mode_changed = QtCore.pyqtSignal(object)  # Existing signal
    isRecordingChanged = QtCore.pyqtSignal(bool)
    isPlayingChanged = QtCore.pyqtSignal(bool)

app_signals = AppSignals()