from qt import QtWidgets, QtCore, Qt
import logging

class BaseCameraManager(QtWidgets.QWidget):
    """
    Base class for camera management widgets.
    Handles common camera controls and preview logic (mode selector removed).
    """
    def __init__(self, cam=None, preview=None, config_model=None, controls_model=None, settings_group=None, parent=None):
        super().__init__(parent)
        self.cam = cam
        self.preview = preview
        self.config_model = config_model
        self.controls_model = controls_model
        self.settings_group = settings_group
        self.modes = self.cam.sensor_modes if self.cam else []
        self._init_ui()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        logging.info(f"{self.__class__.__name__} initialized with camera and preview.")

    def _init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setSpacing(4)
        # Camera mode selector removed
        self.setLayout(main_layout)
