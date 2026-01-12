import logging
import os
from datetime import datetime
from qt import QtWidgets, QtGui, QtCore, Qt
from app_signals import app_signals
from components.base_camera_manager import BaseCameraManager

from ai_file_manager_base import AIFileManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)


IMG_EXT = ".jpg"
IMAGENET_DEFAULT = 244

class CameraManager(BaseCameraManager):
    """
    CameraManager widget for Classifier, extends BaseCameraManager with sequence and crop controls.
    """
    def __init__(self, file_manager=None, parent=None, **kwargs):
        super().__init__(
            cam=kwargs.get("cam"),
            preview=kwargs.get("preview"),
            config_model=kwargs.get("config_model"),
            controls_model=kwargs.get("controls_model"),
            settings_group=kwargs.get("settings_group"),
            parent=parent
        )
        self.file_manager = file_manager
        self.sequence_running = False
        self.sequence_flash_on = False
        self.sequence_timer = QtCore.QTimer(self)
        self.sequence_timer.timeout.connect(self._flash_sequence_btn)
        self.preview.done_signal.connect(self._capture_done)  #= self.preview.signal_done if self.preview and hasattr(self.preview, "signal_done") else None

        # Constrain resolution to IMAGENET_DEFAULT x IMAGENET_DEFAULT (ideal for imagenet)
        # (config_model logic is now obsolete and can be removed)

        # Add extra UI for sequence and crop controls (mode selector removed)
        self._add_extra_controls()

    def _add_extra_controls(self):
        layout = self.layout()

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
        layout.addLayout(interval_layout)

        # Capture button row
        capture_layout = QtWidgets.QHBoxLayout()
        self.capture_btn = QtWidgets.QPushButton("Capture Image")
        self.capture_btn.setToolTip("Capture Image")
        self.capture_btn.clicked.connect(self.capture_image)
        self.capture_btn.setEnabled(False)
        capture_layout.addWidget(self.capture_btn)
        layout.addLayout(capture_layout)

        # Sequence capture button row
        sequence_layout = QtWidgets.QHBoxLayout()
        self.sequence_btn = QtWidgets.QPushButton("Capture Image Sequence")
        self.sequence_btn.setToolTip("Start or stop capturing an image sequence")
        self.sequence_btn.clicked.connect(self.toggle_sequence_capture)
        self.sequence_btn.setEnabled(False)
        sequence_layout.addWidget(self.sequence_btn)
        layout.addLayout(sequence_layout)

    # Removed: _on_size_slider_changed and _on_resample_checkbox_changed (handled by Classifier)

    # ...existing methods for sequence, crop, and validation remain unchanged...

    def _capture_done(self, job):
        logging.info("Image capture completed.")
        try:
            pil_image = self.cam.wait(job)
            if pil_image is None:
                logging.error("No image returned from camera job.")
                self.capture_btn.setDisabled(False)
                return
            # Get file path and settings
            if self.file_manager and hasattr(self.file_manager, "get_new_file_path"):
                file_name = self.file_manager.get_new_file_path()
                quality = self.file_manager.settings_data.get("jpeg_quality", 80)
                resample_on_save = self.file_manager.settings_data.get("resample_on_save", False)
                # Resample if needed
                if resample_on_save:
                    pil_image = pil_image.resize((IMAGENET_DEFAULT, IMAGENET_DEFAULT))
                    logging.info(f"Resampled image to: {IMAGENET_DEFAULT}x{IMAGENET_DEFAULT}")
                # Ensure directory exists
                os.makedirs(os.path.dirname(file_name), exist_ok=True)
                pil_image.save(file_name, format="JPEG", quality=quality)
                logging.info(f"Saved image to {file_name} with quality={quality}")
                if hasattr(self.file_manager, "update_image_count"):
                    self.file_manager.update_image_count()
            else:
                logging.info("FileManagerWidget not available or does not have get_new_file_path().")
        except Exception as e:
            logging.error(f"Error during image capture or save: {e}")
        self.capture_btn.setDisabled(False)

    def capture_image(self):
        logging.info("Capture button pressed.")
        self.capture_btn.setDisabled(True)
        # Start async capture; _capture_done will handle the result
        self.cam.capture_image(signal_function=self.preview.signal_done)

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



    def _set_mode_from_signal(self, mode):
        idx = self.camera_mode_combo.findData(mode)
        if idx != -1 and idx != self.camera_mode_combo.currentIndex():
            self.camera_mode_combo.setCurrentIndex(idx)
            logging.info(f"CameraManager updated dropdown to mode: {mode}")




class Classifier(AIFileManager):
    # Extend the settings schema for classifier-specific settings
    settings_schema = AIFileManager.settings_schema.copy()
    settings_schema.update({
        "square_size": {"type": int, "default": IMAGENET_DEFAULT},
        "resample_on_save": {"type": bool, "default": False},
    })
    """
    Widget for the right dock: 1 column, 2 rows.
    Row 1: FileManager controls (with set/class dropdowns)
    Row 2: CameraManager widget
    """
    def __init__(self, parent=None, **kwargs):
        logging.info(f"Loading Classifier component with settings_group={kwargs.get('settings_group')}")
        super().__init__(parent, settings_group=kwargs.get("settings_group"))

        self.cam = kwargs.get("cam")
        self.config_model = kwargs.get("config_model")
        self.controls_model = kwargs.get("controls_model")
        self.settings_group = kwargs.get("settings_group")

        # Set config_model 'main', 'size' to (square_size, square_size) from settings on init
        if self.config_model is not None:
            square_size = self.settings_data.get("square_size", IMAGENET_DEFAULT)
            self.config_model.set_nested('main', 'size', (square_size, square_size))

        # Add any extra UI unique to Classifier here
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

        # --- Classifier-specific settings widgets ---
        # Square size slider
        self.square_size_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.square_size_slider.setMinimum(IMAGENET_DEFAULT)
        self.square_size_slider.setMaximum(512)
        self.square_size_slider.setValue(self.settings_data["square_size"])
        self.square_size_slider.valueChanged.connect(self._on_square_size_changed)
        self.square_size_label = QtWidgets.QLabel(str(self.square_size_slider.value()))
        sq_layout = QtWidgets.QHBoxLayout()
        sq_layout.addWidget(QtWidgets.QLabel("Square Size"))
        sq_layout.addWidget(self.square_size_slider)
        sq_layout.addWidget(self.square_size_label)
        self.base_layout.addLayout(sq_layout)

        # Resample on save checkbox
        self.resample_checkbox = QtWidgets.QCheckBox("Resample on save")
        self.resample_checkbox.setChecked(self.settings_data["resample_on_save"])
        self.resample_checkbox.stateChanged.connect(self._on_resample_checkbox_changed)
        resample_layout = QtWidgets.QHBoxLayout()
        resample_layout.addWidget(self.resample_checkbox)
        self.base_layout.addLayout(resample_layout)

    def _on_square_size_changed(self, value):
        self.square_size_label.setText(str(value))
        self.settings_data["square_size"] = value
        self.save_settings()
        # Update config_model 'main', 'size' to (square_size, square_size) when changed
        if hasattr(self, 'config_model') and self.config_model is not None:
            self.config_model.set_nested('main', 'size', (value, value))

    def _on_resample_checkbox_changed(self, state):
        self.settings_data["resample_on_save"] = bool(state)
        self.save_settings()

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


