from qt import QtWidgets, QtGui, QtCore, Qt

class ComponentBase(QtWidgets.QWidget):
    """
    Abstract base class for all component widgets.
    Handles common argument parsing, layout setup, and provides a place for shared utilities.
    """

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        # Store commonly used arguments
        self.cam = kwargs.get("cam")
        self.config_model = kwargs.get("config_model")
        self.controls_model = kwargs.get("controls_model")
        self.zoomsets_model = kwargs.get("zoomsets_model")
        self.path_model = kwargs.get("path_model")
        self.audio_model = kwargs.get("audio_model")
        self.settings_group = kwargs.get("settings_group")
        # Add more shared attributes as needed

        # Provide a base layout for child widgets to use or extend
        self.base_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.base_layout)

    # Optionally, add shared utility methods here
    # def some_shared_method(self):
    #     pass