import sys
from qt import QtWidgets as qtw, QtGui, QtCore, Qt

class ResCombo(qtw.QComboBox):

    def __init__(self, parent=None, config_model=None, resolutions_model=None):
        super().__init__(parent)
        self.config_model = config_model
        self.resolutions_model = resolutions_model
        self.resolutions = (
            self.resolutions_model.get_resolutions()
            if self.resolutions_model else [
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
                ('4K UHD', (3840, 2160)), ('8K UHD', (7680, 4320))  
            ]
        )
        self.generateComboItems(mode=None)
        self.currentIndexChanged.connect(self.set_size_in_config)
        # self.show()

    def generateComboItems(self, mode):
        self.clear()
        for item in self.resolutions:
            if mode is not None:
                if item[1][0] < mode['size'][0] and item[1][1] <= mode['size'][1]:
                    self.addItem(f"{item[0]}, {item[1]}", userData=item[1])
            else:
                self.addItem(f"{item[0]}, {item[1]}", userData=item[1])
        print('current text', self.count(), self.currentText())
        # self.setCurrentIndex(0)

    def applySettings(self, tup):
        ix = self.findData(tup)
        self.setCurrentIndex(ix)
        return True

    def set_size_in_config(self, index):
        """
        Slot to set the 'main', 'size' value in the config dictionary when the combo selection changes.
        """
        size = self.itemData(index)
        if size and self.config_model:
            self.config_model.set_nested('main', 'size', size)
            print(f"Set config['main']['size'] to {size}")

    def set_largest_resolution(self):
        """Set the combo box to the largest available resolution currently in the combo."""
        if self.count() == 0:
            return
        largest_ix = 0
        largest_area = 0
        for i in range(self.count()):
            size = self.itemData(i)
            if size:
                area = size[0] * size[1]
                if area > largest_area:
                    largest_area = area
                    largest_ix = i
        self.setCurrentIndex(largest_ix)
        print(f"Defaulting to largest resolution: {self.itemText(largest_ix)}, {self.itemData(largest_ix)}")
if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    w = qtw.QWidget()
    layout = qtw.QVBoxLayout(w)
    # For standalone test, pass None for config_model
    combo = ResCombo(config_model=None)
    layout.addWidget(combo)
    w.show()
    sys.exit(app.exec())
