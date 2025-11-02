from abc import ABC, abstractmethod

from qt import QtWidgets, QtGui, QtCore, Qt
class BaseControlWidget(QtWidgets.QWidget):
    """
    Abstract base class for all control widgets in the bottom dock.
    Ensures consistent kwargs handling and provides a place for shared logic.
    """
    def __init__(self, **kwargs):
        super().__init__()
        self.cam = kwargs.get("cam")
        self.config_model = kwargs.get("config_model")
        self.controls_model = kwargs.get("controls_model")
        self.preview = kwargs.get("preview")
        self.zoomsets_model = kwargs.get("zoomsets_model")
        self.settings_group = kwargs.get("settings_group", None)
        self.init_ui()

    @abstractmethod
    def init_ui(self):
        """
        Subclasses must implement this to set up their UI.
        """
        pass

    def cleanup(self):
        """
        Optional: Subclasses can override this for cleanup logic.
        """
        pass
