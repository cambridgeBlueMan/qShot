import sys
from qt import QtWidgets as qtw, QtGui, QtCore, Qt

class ResCombo(qtw.QComboBox):

    def __init__(self, parent=None, config_model=None, resolutions_model=None):
        super().__init__(parent)
        self.config_model = config_model
        self.resolutions_model = resolutions_model
        self.generateComboItems(mode=None)
        self.currentIndexChanged.connect(self.set_size_in_config)
        if self.resolutions_model:
            self.resolutions_model.resolutionsChanged.connect(lambda: self.generateComboItems(mode=None))

    def generateComboItems(self, mode):
        self.clear()
        if not self.resolutions_model:
            return
        resolutions = self.resolutions_model.get_resolutions()
        for item in resolutions:
            if mode is not None:
                if item[1][0] < mode['size'][0] and item[1][1] <= mode['size'][1]:
                    self.addItem(f"{item[0]}, {item[1]}", userData=item[1])
            else:
                self.addItem(f"{item[0]}, {item[1]}", userData=item[1])
        self.set_largest_resolution()  # <-- Ensure largest is selected

    def applySettings(self, tup):
        ix = self.findData(tup)
        self.setCurrentIndex(ix)
        return True

    def set_size_in_config(self, index):
        size = self.itemData(index)
        if size and self.config_model:
            self.config_model.set_nested('main', 'size', size)

    def set_largest_resolution(self):
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

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    from resolutions_model import ResolutionsModel
    resolutions_model = ResolutionsModel()
    combo = ResCombo(config_model=None, resolutions_model=resolutions_model)
    w = qtw.QWidget()
    layout = qtw.QVBoxLayout(w)
    layout.addWidget(combo)
    w.show()
    sys.exit(app.exec())
