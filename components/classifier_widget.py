import logging
import os
from datetime import datetime
from qt import QtWidgets, QtGui, QtCore, Qt
from ai_file_manager_base import AIFileManager
from app_signals import app_signals
# from config_model import config_model

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)

IMG_EXT = ".jpg"

class CameraManager(QtWidgets.QWidget):
    """
    CameraManager widget that receives camera and csi information and provides capture controls.
    Handles single and interval image capture, as well as UI feedback for sequence capture.
    """

    def __init__(self, file_manager=None, parent=None, **kwargs):
        """
        Initialize the CameraManager widget.

        Args:
            cam: Camera object.
            csi: Camera serial interface index.
            modes: List of camera modes.
            file_manager: FileManagerWidget instance.
            preview: Preview widget with signal_done.
            parent: Parent QWidget.
        """
        super().__init__(parent)
        self.file_manager = file_manager
        self.cam = kwargs.get("cam")
        self.modes = self.cam.sensor_modes
        self.preview = kwargs.get("preview")
        self.config_model = kwargs.get("config_model")
        self.controls_model = kwargs.get("controls_model")
        self.settings_group = kwargs.get("settings_group")
        
        self.sequence_running = False
        self.sequence_flash_on = False
        self.sequence_timer = QtCore.QTimer(self)
        self.sequence_timer.timeout.connect(self._flash_sequence_btn)
        self.signal_function = self.preview.signal_done if self.preview and hasattr(self.preview, "signal_done") else None

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

        # Sequence interval row
        interval_layout = QtWidgets.QHBoxLayout()
        interval_label = QtWidgets.QLabel("Sequence Interval")
        self.sequence_interval_spin = QtWidgets.QDoubleSpinBox()
        self.sequence_interval_spin.setDecimals(1)
        self.sequence_interval_spin.setSingleStep(0.1)
        self.sequence_interval_spin.setMinimum(0.1)
        self.sequence_interval_spin.setMaximum(10.0)
        self.sequence_interval_spin.setValue(0.5)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.sequence_interval_spin)
        main_layout.addLayout(interval_layout)

        # Capture button row
        capture_layout = QtWidgets.QHBoxLayout()
        self.capture_btn = QtWidgets.QPushButton("Capture Image")
        self.capture_btn.setToolTip("Capture Image")
        self.capture_btn.clicked.connect(self.capture_image)
        self.capture_btn.setEnabled(False)
        capture_layout.addWidget(self.capture_btn)
        main_layout.addLayout(capture_layout)

        # Sequence capture button row
        sequence_layout = QtWidgets.QHBoxLayout()
        self.sequence_btn = QtWidgets.QPushButton("Capture Image Sequence")
        self.sequence_btn.setToolTip("Start or stop capturing an image sequence")
        self.sequence_btn.clicked.connect(self.toggle_sequence_capture)
        self.sequence_btn.setEnabled(False)
        sequence_layout.addWidget(self.sequence_btn)
        main_layout.addLayout(sequence_layout)

        # X/Y position row
        pos_layout = QtWidgets.QHBoxLayout()
        xpos_label = QtWidgets.QLabel("X pos")
        self.xpos_spin = QtWidgets.QSpinBox()
        self.xpos_spin.setRange(0, 816)
        self.xpos_spin.setValue(0)
        ypos_label = QtWidgets.QLabel("Y pos")
        self.ypos_spin = QtWidgets.QSpinBox()
        self.ypos_spin.setRange(0, 608)
        self.ypos_spin.setValue(0)
        set_btn = QtWidgets.QPushButton("Set")
        set_btn.setToolTip("Set ScalerCrop to current X/Y values")
        set_btn.clicked.connect(self._update_scaler_crop)
        pos_layout.addWidget(xpos_label)
        pos_layout.addWidget(self.xpos_spin)
        pos_layout.addWidget(ypos_label)
        pos_layout.addWidget(self.ypos_spin)
        pos_layout.addWidget(set_btn)
        main_layout.addLayout(pos_layout)

        self.setLayout(main_layout)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        logging.info("CameraManager widget initialized with camera and csi.")

        # Listen for global mode changes
        app_signals.mode_changed.connect(self._set_mode_from_signal)

    def _capture_done(self, job):
        logging.info("Image capture completed.")
        result = self.cam.wait(job)
        self.capture_btn.setDisabled(False)
        if self.file_manager and hasattr(self.file_manager, "update_image_count"):
            self.file_manager.update_image_count()

    def capture_image(self):
        logging.info("Capture button pressed.")
        self.capture_btn.setDisabled(True)
        if self.preview and hasattr(self.preview, "done_signal"):
            self.preview.done_signal.connect(self._capture_done)
        if self.file_manager and hasattr(self.file_manager, "get_new_file_path"):
            file_name = self.file_manager.get_new_file_path()
            logging.info(f"Generated file path from FileManagerWidget: {file_name}")
            self.cam.capture_file(file_name, signal_function=self.signal_function)
        else:
            logging.info("FileManagerWidget not available or does not have get_new_file_path().")

    def toggle_sequence_capture(self):
        logging.info("Sequence capture button pressed.")
        self.sequence_running = not self.sequence_running
        if self.sequence_running:
            self.sequence_timer.start(500)
            self.start_interval_capture()
            logging.info("Started sequence capture.")
        else:
            self.sequence_timer.stop()
            self.sequence_btn.setStyleSheet("")
            self.stop_interval_capture()
            logging.info("Stopped sequence capture.")

    def _flash_sequence_btn(self):
        if self.sequence_flash_on:
            self.sequence_btn.setStyleSheet("")
        else:
            self.sequence_btn.setStyleSheet("background-color: red; color: white;")
        self.sequence_flash_on = not self.sequence_flash_on

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

    def start_interval_capture(self):
        interval = self.sequence_interval_spin.value()
        if interval <= 0:
            logging.warning("Interval must be greater than 0.")
            return
        if hasattr(self, 'interval_capture_timer') and self.interval_capture_timer.isActive():
            self.interval_capture_timer.stop()
        self.interval_capture_timer = QtCore.QTimer(self)
        self.interval_capture_timer.timeout.connect(self.capture_image)
        self.interval_capture_timer.start(int(interval * 1000))
        logging.info(f"Started interval capture every {interval} seconds.")

    def stop_interval_capture(self):
        if hasattr(self, 'interval_capture_timer') and self.interval_capture_timer.isActive():
            self.interval_capture_timer.stop()
            logging.info("Stopped interval capture.")

    def _update_scaler_crop(self):
        x = self.xpos_spin.value()
        y = self.ypos_spin.value()
        width = 640
        height = 480
        try:
            self.cam.set_controls({"ScalerCrop": (x, y, width, height)})
            logging.info(f"ScalerCrop set to: x={x}, y={y}, width={width}, height={height}")
        except Exception as e:
            logging.error(f"Failed to set ScalerCrop: {e}")

    def validate_and_update_buttons(self):
        logging.info("validate_and_update_buttons() called")
        dataset_valid = self.is_dataset_path_valid()
        labels_valid = self.is_labels_file_valid()
        buttons_enabled = dataset_valid and labels_valid
        logging.info(f"Setting capture_btn.setEnabled({buttons_enabled})")
        logging.info(f"Setting sequence_btn.setEnabled({buttons_enabled})")
        self.capture_btn.setEnabled(buttons_enabled)
        self.sequence_btn.setEnabled(buttons_enabled)
        logging.info(f"capture_btn.isEnabled() = {self.capture_btn.isEnabled()}")
        logging.info(f"sequence_btn.isEnabled() = {self.sequence_btn.isEnabled()}")
        if not buttons_enabled:
            logging.info(f"Capture buttons disabled - Dataset valid: {dataset_valid}, Labels valid: {labels_valid}")
            self.capture_btn.setStyleSheet("color: #333333; background-color: #888888; border: 1px solid #666666;")
            self.sequence_btn.setStyleSheet("color: #333333; background-color: #888888; border: 1px solid #666666;")
        else:
            logging.info("Capture buttons enabled - Both dataset and labels are valid")
            self.capture_btn.setStyleSheet("")
            self.sequence_btn.setStyleSheet("")

    def is_dataset_path_valid(self):
        if not self.file_manager or not hasattr(self.file_manager, "dataset_path_input"):
            return False
        dataset_path = self.file_manager.dataset_path_input.text()
        return os.path.isdir(dataset_path)

    def is_labels_file_valid(self):
        if not self.file_manager or not hasattr(self.file_manager, "class_labels_input"):
            return False
        labels_path = self.file_manager.class_labels_input.text()
        if not os.path.isfile(labels_path):
            return False
        try:
            with open(labels_path, "r") as f:
                labels = [line.strip() for line in f if line.strip()]
            if not labels:
                logging.warning("Labels file is empty")
                return False
            logging.info(f"Labels file is valid with {len(labels)} classes")
            return True
        except Exception as e:
            logging.error(f"Error reading labels file: {e}")
            return False

    def _on_mode_changed(self, index):
        mode = self.cam.sensor_modes[index]
        self.config_model.set_nested('sensor', 'output_size', mode['size'])
        self.config_model.set_nested('sensor', 'bit_depth', mode['bit_depth'])
        logging.info(f"Camera mode changed: {mode}")
        print(self.config_model.to_dict())

    def _set_mode_from_signal(self, mode):
        idx = self.camera_mode_combo.findData(mode)
        if idx != -1 and idx != self.camera_mode_combo.currentIndex():
            self.camera_mode_combo.setCurrentIndex(idx)
            logging.info(f"CameraManager updated dropdown to mode: {mode}")

class Classifier(AIFileManager):
    """
    Widget for the right dock: 1 column, 2 rows.
    Row 1: FileManager controls (with set/class dropdowns)
    Row 2: CameraManager widget
    """

    def __init__(self, parent=None, **kwargs):
        """
        Initialize the Classifier widget.

        Args (passed via kwargs):
            cam: Camera object.
            config_model: Configuration model object.
            controls_model: Controls model object.
            settings_group: Optional settings group name.
            csi, modes, preview, parent: Other optional arguments.
        """
        logging.info(f"Loading Classifier component with settings_group={kwargs.get('settings_group')}")
        super().__init__(kwargs.get("parent", None), settings_group=kwargs.get("settings_group"))

        self.cam = kwargs.get("cam")
        self.config_model = kwargs.get("config_model")
        self.controls_model = kwargs.get("controls_model")
        self.settings_group = kwargs.get("settings_group")

        spacer_above = QtWidgets.QWidget()
        spacer_above.setFixedHeight(12)
        self.base_layout.addWidget(spacer_above)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        palette = self.palette()
        bg_color = palette.color(QtGui.QPalette.ColorRole.Dark).name()
        separator.setStyleSheet(f"background-color: {bg_color}; height: 2px; border: none;")
        self.base_layout.addWidget(separator)

        spacer_below = QtWidgets.QWidget()
        spacer_below.setFixedHeight(12)
        self.base_layout.addWidget(spacer_below)

        group_layout = QtWidgets.QVBoxLayout()
        group_layout.setSpacing(10)
        group_layout.setContentsMargins(0, 0, 0, 0)

        group_box = QtWidgets.QGroupBox("Dataset Controls")
        group_box_layout = QtWidgets.QGridLayout()
        group_box_layout.setSpacing(10)
        group_box_layout.setContentsMargins(8, 8, 8, 8)

        set_label = QtWidgets.QLabel("Current Set:")
        self.current_set_dropdown = QtWidgets.QComboBox()
        group_box_layout.addWidget(set_label, 0, 0)
        group_box_layout.addWidget(self.current_set_dropdown, 0, 1)

        class_label = QtWidgets.QLabel("Current Class:")
        self.current_class_dropdown = QtWidgets.QComboBox() 
        group_box_layout.addWidget(class_label, 1, 0)
        group_box_layout.addWidget(self.current_class_dropdown, 1, 1)

        image_count_label = QtWidgets.QLabel("Image count for current set and class:")
        self.image_count_label = QtWidgets.QLabel("0")
        self.image_count_label.setMinimumWidth(40)
        self.image_count_label.setStyleSheet("color: yellow;")
        group_box_layout.addWidget(image_count_label, 2, 0)
        group_box_layout.addWidget(self.image_count_label, 2, 1)

        group_box.setLayout(group_box_layout)
        self.base_layout.addWidget(group_box)

        logging.info("Instantiating CameraManager for Classifier component")
        self.camera_manager = CameraManager(file_manager=self, **kwargs)
        self.base_layout.addWidget(self.camera_manager)

        self.setLayout(self.base_layout)
        logging.info("Classifier widget initialized.")

        self.init_action()
        self.camera_manager.validate_and_update_buttons()
        self.current_set_dropdown.currentIndexChanged.connect(self.update_image_count)
        self.current_class_dropdown.currentIndexChanged.connect(self.update_image_count)
        app_signals.mode_changed.connect(self.on_global_mode_changed)

    def get_new_file_path(self):
        dataset_path = self.dataset_path_input.text()
        set_value = self.current_set_dropdown.currentText() if self.current_set_dropdown.count() else "unknown_set"
        class_value = self.current_class_dropdown.currentText() if self.current_class_dropdown.count() else "unknown_class"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = os.path.join(
            dataset_path,
            set_value,
            class_value,
            f"{class_value}_{timestamp}{IMG_EXT}"
        )
        logging.info(f"Generated file path: {file_path}")
        return file_path

    def init_action(self):
        dataset_path = self.dataset_path_input.text()
        self.current_set_dropdown.clear()
        self.current_class_dropdown.clear()
        class_labels = self.load_class_labels()
        for set_name in ["train", "test", "val"]:
            set_dir = os.path.join(dataset_path, set_name)
            if not os.path.isdir(set_dir):
                try:
                    os.makedirs(set_dir, exist_ok=True)
                    logging.info(f"Created missing set directory: {set_dir}")
                except Exception as e:
                    logging.error(f"Failed to create set directory {set_dir}: {e}")
                    continue
            for class_label in class_labels:
                class_dir = os.path.join(set_dir, class_label)
                if not os.path.isdir(class_dir):
                    try:
                        os.makedirs(class_dir, exist_ok=True)
                        logging.info(f"Created class directory: {class_dir}")
                    except Exception as e:
                        logging.error(f"Failed to create class directory {class_dir}: {e}")

        if not os.path.isdir(dataset_path):
            logging.warning(f"Dataset path does not exist: {dataset_path}")
            return

        sets = [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]
        self.current_set_dropdown.addItems(sets)
        self.current_set_dropdown.currentIndexChanged.connect(self._update_class_dropdown)
        self._update_class_dropdown()
        self.update_image_count()
        self.camera_manager.validate_and_update_buttons()

    def _update_class_dropdown(self):
        self.current_class_dropdown.clear()
        class_labels = self.load_class_labels()
        self.current_class_dropdown.addItems(class_labels)
        self.camera_manager.validate_and_update_buttons()
        self.update_image_count()

    def load_class_labels(self):
        labels_path = self.class_labels_input.text() if hasattr(self, "class_labels_input") else ""
        if os.path.isfile(labels_path):
            with open(labels_path, "r") as f:
                labels = [line.strip() for line in f if line.strip()]
            return labels
        return []

    def check_paths_and_update_fields(self):
        dataset_path = self.dataset_path_input.text()
        labels_path = self.labels_path_input.text() if hasattr(self, "labels_path_input") else ""
        if not os.path.isdir(dataset_path):
            logging.info(f"Dataset path does not exist: {dataset_path}. Clearing field.")
            self.dataset_path_input.setText("")
        if not os.path.isfile(labels_path):
            logging.info(f"Labels path does not exist: {labels_path}. Clearing field.")
            if hasattr(self, "class_labels_input"):
                self.class_labels_input.setText("")

    def update_image_count(self):
        dataset_path = self.dataset_path_input.text()
        set_value = self.current_set_dropdown.currentText()
        class_value = self.current_class_dropdown.currentText()
        count = 0
        if dataset_path and set_value and class_value:
            folder = os.path.join(dataset_path, set_value, class_value)
            if os.path.isdir(folder):
                count = len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])
        self.image_count_label.setText(str(count))

    def on_global_mode_changed(self, mode):
        logging.info(f"Classifier received global mode change: {mode}")


