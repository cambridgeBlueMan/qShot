from qt import QtCore, QtWidgets, QtGui, Qt

class ZoomsetsModel(QtCore.QObject):
    """
    Example model for managing zoom sets.
    """
    zoomsetsChanged = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoomsets = []

    def add_zoomset(self, zoomset):
        self._zoomsets.append(zoomset)
        self.zoomsetsChanged.emit()

    def remove_zoomset(self, zoomset):
        if zoomset in self._zoomsets:
            self._zoomsets.remove(zoomset)
            self.zoomsetsChanged.emit()

    def get_zoomsets(self):
        return self._zoomsets

    def set_zoomsets(self, zoomsets):
        self._zoomsets = zoomsets
        self.zoomsetsChanged.emit()