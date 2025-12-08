from qt import QtWidgets
class ResolutionsEditor(QtWidgets.QDialog):
    def __init__(self, resolution_model):
        super().__init__()
        # Use QTableWidget to show/edit resolutions
        # On save, call resolution_model.set_resolutions(...)