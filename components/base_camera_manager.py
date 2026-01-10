from qt import QtWidgets, QtCore, Qt
import logging

class BaseCameraManager(QtWidgets.QWidget):
    """
    Base class for camera management widgets.
    Handles common camera controls, mode selection, and preview logic.
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
        # Camera Mode row
        camera_mode_layout = QtWidgets.QHBoxLayout()
        camera_mode_label = QtWidgets.QLabel("Camera Mode")
        camera_mode_layout.addWidget(camera_mode_label)
        self.camera_mode_combo = QtWidgets.QComboBox()
        self._add_sensor_mode_dropdown(camera_mode_layout, self.modes, combo=self.camera_mode_combo)
        self.camera_mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        camera_mode_layout.addWidget(self.camera_mode_combo)
        main_layout.addLayout(camera_mode_layout)
        self.setLayout(main_layout)

    def _add_sensor_mode_dropdown(self, layout, modes, combo=None):
        if combo is None:
            combo = QtWidgets.QComboBox()
        if modes:
            for idx, mode in enumerate(modes):
                desc = f"{idx}: {mode.get('size', '')} {mode.get('format', '')}"
                combo.addItem(desc, userData=mode)
            logging.info(f"Sensor mode dropdown populated with {len(modes)} modes.")
        else:
            combo.addItem("No sensor modes found")
            logging.warning("No sensor modes found for dropdown.")
        combo.setToolTip("Select sensor mode")
        layout.addWidget(combo)

    def _on_mode_changed(self, index):
        if not self.cam or not self.config_model:
            return
        mode = self.cam.sensor_modes[index]
        self.config_model.set_nested('sensor', 'output_size', mode['size'])
        self.config_model.set_nested('sensor', 'bit_depth', mode['bit_depth'])
        logging.info(f"Camera mode changed: {mode}")
        if hasattr(self.config_model, 'to_dict'):
            print(self.config_model.to_dict())
