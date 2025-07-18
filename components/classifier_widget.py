import logging
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QLineEdit,
    QDoubleSpinBox, QFrame, QSpinBox, QSlider, QFileDialog
)
from PyQt6.QtGui import QIcon, QColor, QPalette
from PyQt6.QtCore import QTimer, Qt, QSettings
from ai_file_manager_base import AIFileManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)

IMG_EXT = ".jpg"

class CameraManager(QWidget):
    """
    CameraManager widget that receives camera and csi information and provides capture controls.
    Handles single and interval image capture, as well as UI feedback for sequence capture.
    """

    def __init__(self, cam=None, csi=0, modes=None, file_manager=None, preview=None, parent=None):
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
        self.cam = cam
        self.csi = csi
        self.modes = modes
        self.file_manager = file_manager
        self.preview = preview
        self.sequence_running = False  # Track sequence state
        self.sequence_flash_on = False  # Track flash state
        self.sequence_timer = QTimer(self)
        self.sequence_timer.timeout.connect(self._flash_sequence_btn)
        self.signal_function = self.preview.signal_done if self.preview and hasattr(self.preview, "signal_done") else None

        main_layout = QVBoxLayout()
        main_layout.setSpacing(4)  # Reduce vertical spacing between rows

        # Camera Mode row
        camera_mode_layout = QHBoxLayout()
        camera_mode_label = QLabel("Camera Mode")
        camera_mode_layout.addWidget(camera_mode_label)
        combo = QComboBox()
        self._add_sensor_mode_dropdown(camera_mode_layout, modes, combo=combo)
        main_layout.addLayout(camera_mode_layout)

        # Sequence interval row
        interval_layout = QHBoxLayout()
        interval_label = QLabel("Sequence Interval")
        self.sequence_interval_spin = QDoubleSpinBox()
        self.sequence_interval_spin.setDecimals(1)
        self.sequence_interval_spin.setSingleStep(0.1)
        self.sequence_interval_spin.setMinimum(0.1)
        self.sequence_interval_spin.setMaximum(10.0)
        self.sequence_interval_spin.setValue(0.5)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.sequence_interval_spin)
        main_layout.addLayout(interval_layout)

        # Capture button row
        capture_layout = QHBoxLayout()
        self.capture_btn = QPushButton("Capture Image")
        self.capture_btn.setToolTip("Capture Image")
        self.capture_btn.clicked.connect(self.capture_image)
        capture_layout.addWidget(self.capture_btn)
        main_layout.addLayout(capture_layout)

        # Sequence capture button row
        sequence_layout = QHBoxLayout()
        self.sequence_btn = QPushButton("Capture Image Sequence")
        self.sequence_btn.setToolTip("Start or stop capturing an image sequence")
        self.sequence_btn.clicked.connect(self.toggle_sequence_capture)
        sequence_layout.addWidget(self.sequence_btn)
        main_layout.addLayout(sequence_layout)

        # X/Y position row
        pos_layout = QHBoxLayout()
        xpos_label = QLabel("X pos")
        self.xpos_spin = QSpinBox()
        self.xpos_spin.setRange(0, 816)
        self.xpos_spin.setValue(0)
        ypos_label = QLabel("Y pos")
        self.ypos_spin = QSpinBox()
        self.ypos_spin.setRange(0, 608)
        self.ypos_spin.setValue(0)
        set_btn = QPushButton("Set")
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

    def _capture_done(self, job):
        """
        Slot called when image capture is done.
        Re-enables the capture button and logs completion.

        Args:
            job: The job object returned by the camera capture.
        """
        logging.info("Image capture completed.")
        result = self.cam.wait(job)
        self.file_manager.update_status_label()
        self.capture_btn.setDisabled(False)

    def capture_image(self):
        """
        Capture a single image using the camera and file manager.
        Disables the capture button until capture is complete.
        """
        logging.info("Capture button pressed.")
        # Disable the button to prevent multiple clicks
        self.capture_btn.setDisabled(True)
        if self.preview and hasattr(self.preview, "done_signal"):
            self.preview.done_signal.connect(self._capture_done)
        # Get a file name from the file manager widget if available
        if self.file_manager and hasattr(self.file_manager, "get_new_file_path"):
            file_name = self.file_manager.get_new_file_path()
            logging.info(f"Generated file path from FileManagerWidget: {file_name}")
            self.cam.capture_file(file_name, signal_function=self.signal_function)
        else:
            logging.info("FileManagerWidget not available or does not have get_new_file_path().")

    def toggle_sequence_capture(self):
        """
        Toggle the sequence capture mode.
        Starts or stops interval image capture and button flashing.
        """
        logging.info("Sequence capture button pressed.")
        self.sequence_running = not self.sequence_running
        if self.sequence_running:
            self.sequence_timer.start(500)  # Flash every 500 ms
            self.start_interval_capture()   # Start interval image capture
            logging.info("Started sequence capture.")
        else:
            self.sequence_timer.stop()
            self.sequence_btn.setStyleSheet("")  # Reset to default
            self.stop_interval_capture()    # Stop interval image capture
            logging.info("Stopped sequence capture.")

    def _flash_sequence_btn(self):
        """
        Alternate the sequence button's background color to indicate active sequence capture.
        """
        if self.sequence_flash_on:
            self.sequence_btn.setStyleSheet("")
        else:
            self.sequence_btn.setStyleSheet("background-color: red; color: white;")
        self.sequence_flash_on = not self.sequence_flash_on

    def _add_sensor_mode_dropdown(self, layout, modes, combo=None):
        """
        Add a sensor mode dropdown to the given layout.

        Args:
            layout: The layout to add the dropdown to.
            modes: List of camera modes.
            combo: Optional QComboBox to use.
        """
        if combo is None:
            combo = QComboBox()
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
        """
        Start capturing images at intervals specified by sequence_interval_spin.
        """
        interval = self.sequence_interval_spin.value()
        if interval <= 0:
            logging.warning("Interval must be greater than 0.")
            return
        # Stop any existing timer to avoid multiple timers running
        if hasattr(self, 'interval_capture_timer') and self.interval_capture_timer.isActive():
            self.interval_capture_timer.stop()
        # Create and start the timer
        self.interval_capture_timer = QTimer(self)
        self.interval_capture_timer.timeout.connect(self.capture_image)
        self.interval_capture_timer.start(int(interval * 1000))  # QTimer expects milliseconds
        logging.info(f"Started interval capture every {interval} seconds.")

    def stop_interval_capture(self):
        """
        Stop the interval image capture timer.
        """
        if hasattr(self, 'interval_capture_timer') and self.interval_capture_timer.isActive():
            self.interval_capture_timer.stop()
            logging.info("Stopped interval capture.")

    def _update_scaler_crop(self):
        """
        Update the camera's ScalerCrop control with the current X and Y positions.
        Width and height are set to 640 and 480.
        """
        x = self.xpos_spin.value()
        y = self.ypos_spin.value()
        width = 640
        height = 480
        try:
            self.cam.set_controls({"ScalerCrop": (x, y, width, height)})
            logging.info(f"ScalerCrop set to: x={x}, y={y}, width={width}, height={height}")
        except Exception as e:
            logging.error(f"Failed to set ScalerCrop: {e}")

class Classifier(AIFileManager):
    """
    Widget for the right dock: 1 column, 2 rows.
    Row 1: FileManager controls (with set/class dropdowns)
    Row 2: CameraManager widget
    """

    def __init__(self, cam=None, csi=0, modes=None, preview=None, parent=None, settings_group=None):
        logging.info(f"Loading Classifier component with settings_group={settings_group}")
        super().__init__(parent, settings_group=settings_group)
        self.cam = cam
        self.csi = csi
        self.modes = modes
        self.preview = preview

        # --- Add a visible separator first ---
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        palette = self.palette()
        bg_color = palette.color(QPalette.ColorRole.Dark).name()
        separator.setStyleSheet(f"background-color: {bg_color}; height: 2px; border: none;")
        self.base_layout.addWidget(separator)

        # --- Set Dropdown Row ---
        set_layout = QHBoxLayout()
        set_layout.addWidget(QLabel("Current Set:"))
        self.current_set_dropdown = QComboBox()
        set_layout.addWidget(self.current_set_dropdown)
        self.base_layout.addLayout(set_layout)

        # --- Class Dropdown Row ---
        class_layout = QHBoxLayout()
        class_layout.addWidget(QLabel("Current Class:"))
        self.current_class_dropdown = QComboBox() 
        class_layout.addWidget(self.current_class_dropdown)
        self.base_layout.addLayout(class_layout)

        # CameraManager controls (was Transport)
        logging.info("Instantiating CameraManager for Classifier component")
        self.camera_manager = CameraManager(cam=cam, csi=csi, modes=modes, file_manager=self, preview=preview)
        self.base_layout.addWidget(self.camera_manager)

        self.setLayout(self.base_layout)  # Only call setLayout here!
        logging.info("Classifier widget initialized.")

        # Populate dropdowns on init
        self.init_action()

    def get_new_file_path(self):
        """
        Generate a new file path based on the dataset path, selected set, and class.
        """
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
        """
        Scan the dataset path for set/class folders and populate the dropdowns.
        """
        dataset_path = self.dataset_path_input.text()
        self.current_set_dropdown.clear()
        self.current_class_dropdown.clear()
        if not os.path.isdir(dataset_path):
            logging.warning(f"Dataset path does not exist: {dataset_path}")
            return
        sets = [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]
        self.current_set_dropdown.addItems(sets)
        if sets:
            first_set = sets[0]
            classes = [d for d in os.listdir(os.path.join(dataset_path, first_set))
                       if os.path.isdir(os.path.join(dataset_path, first_set, d))]
            self.current_class_dropdown.addItems(classes)
        # Update classes when set changes
        self.current_set_dropdown.currentIndexChanged.connect(self._update_class_dropdown)

    def _update_class_dropdown(self):
        dataset_path = self.dataset_path_input.text()
        set_value = self.current_set_dropdown.currentText()
        self.current_class_dropdown.clear()
        set_path = os.path.join(dataset_path, set_value)
        if os.path.isdir(set_path):
            classes = [d for d in os.listdir(set_path) if os.path.isdir(os.path.join(set_path, d))]
            self.current_class_dropdown.addItems(classes)