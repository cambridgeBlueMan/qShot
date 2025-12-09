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
        print("generateComboItems called")
        self.clear()
        if not self.resolutions_model:
            print("No resolutions_model provided!")
            return
        resolutions = self.resolutions_model.get_resolutions()
        print(f"Resolutions fetched from model: {resolutions}")
        for item in resolutions:
            print(f"Adding item: {item}")
            if mode is not None:
                print(f"Mode provided: {mode}")
                if item[1][0] < mode['size'][0] and item[1][1] <= mode['size'][1]:
                    self.addItem(f"{item[0]}, {item[1]}", userData=item[1])
                    print(f"Item added with mode filter: {item}")
            else:
                self.addItem(f"{item[0]}, {item[1]}", userData=item[1])
                print(f"Item added without mode filter: {item}")
        print('Combo count:', self.count(), 'Current text:', self.currentText())

    def applySettings(self, tup):
        ix = self.findData(tup)
        self.setCurrentIndex(ix)
        return True

    def set_size_in_config(self, index):
        size = self.itemData(index)
        if size and self.config_model:
            self.config_model.set_nested('main', 'size', size)
            print(f"Set config['main']['size'] to {size}")

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
        print(f"Defaulting to largest resolution: {self.itemText(largest_ix)}, {self.itemData(largest_ix)}")

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
