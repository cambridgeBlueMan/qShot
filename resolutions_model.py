from qt import QtCore

class ResolutionsModel(QtCore.QObject):
    resolutionsChanged = QtCore.pyqtSignal()

    def __init__(self, resolutions=None):
        super().__init__()
        self.resolutions = resolutions or [
            ('CGA', (320, 200)), ('VGA', (640, 480)), ('HD 720', (1280, 720)), ('HD 1080', (1920, 1080)),
        ]

    def set_resolutions(self, new_list):
        self.resolutions = new_list
        self.resolutionsChanged.emit()

    def get_resolutions(self):
        return self.resolutions