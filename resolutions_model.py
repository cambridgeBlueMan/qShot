from qt import QtCore

class ResolutionsModel(QtCore.QObject):
    resolutionsChanged = QtCore.pyqtSignal()

    DEFAULT_RESOLUTIONS = [
            ('CGA', (320, 200)), ('QVGA', (320, 240)),
            ('VGA', (640, 480)), ('PAL', (768, 576)),
            ('480p', (720, 480)), ('576p', (720, 576)),
            ('WVGA', (800, 480)), ('SVGA', (800, 600)),
            ('FWVGA', (854, 480)), ('WSVGA', (1024, 600)),
            ('XGA', (1024, 768)), ('HD 720', (1280, 720)),
            ('WXGA_1', (1280, 768)), ('WXGA_2', (1280, 800)),
            ('SXGA', (1280, 1024)), ('SXGA+', (1400, 1050)),
            ('UXGA', (1600, 1200)), ('WSXGA+', (1680, 1050)),
            ('HD 1080', (1920, 1080)), ('WUXGA', (1920, 1200)),
            ('2K', (2048, 1080)), ('Small Square', (100, 100)),
            ('Medium Square', (200, 200)), ('Large Square', (400, 400)),
            ('half size', (960, 540)),
            ('4K UHD', (3840, 2160)), 
        ]
    def __init__(self, resolutions=None):
        super().__init__()
        self.settings = QtCore.QSettings("ai_capture", "Resolutions")
        self.resolutions = self.load_resolutions_from_settings()
        if not self.resolutions:
            self.resolutions = resolutions or self.DEFAULT_RESOLUTIONS

    def set_resolutions(self, new_list):
        self.resolutions = new_list
        self.save_resolutions_to_settings()
        self.resolutionsChanged.emit()

    def get_resolutions(self):
        return self.resolutions

    def save_resolutions_to_settings(self):
        self.settings.setValue("resolutions", self.resolutions)

    def load_resolutions_from_settings(self):
        vals = self.settings.value("resolutions", None)
        # QSettings may return a QVariant or list of lists
        if vals:
            try:
                # Convert to list of tuples
                return [(str(name), (int(size[0]), int(size[1]))) for name, size in vals]
            except Exception:
                pass
        return []