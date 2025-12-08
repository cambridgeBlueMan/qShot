from qt import QtCore
class ResolutionsModel(QtCore.QObject):
    resolutionsChanged = QtCore.pyqtSignal()

    def __init__(self, resolutions=None):
        super().__init__()
        self.resolutions = resolutions or [
            ('CGA', (320, 200)), ('QVGA', (320, 240)), # ...etc
        ]

    def set_resolutions(self, new_list):
        self.resolutions = new_list
        self.resolutionsChanged.emit()

    def get_resolutions(self):
        return self.resolutions