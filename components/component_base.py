from qt import QtWidgets

class ComponentBase(QtWidgets.QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        # Assign all common args
        self.cam = kwargs.get("cam")
        self.preview = kwargs.get("preview")
        self.config_model = kwargs.get("config_model")
        self.controls_model = kwargs.get("controls_model")
        self.zoomsets_model = kwargs.get("zoomsets_model")
        self.path_model = kwargs.get("path_model")
        self.audio_model = kwargs.get("audio_model")
        self.settings_group = kwargs.get("settings_group")

        self.base_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.base_layout)