import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QLineEdit, QDoubleSpinBox, QFrame, QSpinBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, Qt
from ai_file_manager import FileManagerWidget

# Configure logging to overwrite the log file on each run
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)

class Transport(QWidget): 
    """
    Transport widget that receives camera and csi information and provides capture controls.
    Handles single and interval image capture, as well as UI feedback for sequence capture.
    """

    def __init__(self, cam=None, csi=0, modes=None, file_manager=None, preview=None, parent=None):
        """
        Initialize the Transport widget.

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

        # Group the two horizontal layouts in a vertical layout
        selector_layout = QVBoxLayout()
        # selector_layout.setSpacing(2)  # Even less space between these rows

        # Camera Mode row
        camera_mode_layout = QHBoxLayout()
        camera_mode_label = QLabel("Camera Mode")
        camera_mode_layout.addWidget(camera_mode_label)
        combo = QComboBox()
        self._add_sensor_mode_dropdown(camera_mode_layout, modes, combo=combo)
        selector_layout.addLayout(camera_mode_layout)

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
        selector_layout.addLayout(interval_layout)

        # Add the selector_layout to the main_layout
        main_layout.addLayout(selector_layout)

        # Capture button row (its own row)
        capture_layout = QHBoxLayout()
        self.capture_btn = QPushButton("Capture Image")
        self.capture_btn.setToolTip("Capture Image")
        self.capture_btn.clicked.connect(self.capture_image)
        capture_layout.addWidget(self.capture_btn)
        main_layout.addLayout(capture_layout)

        # Sequence capture button row (its own row)
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
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        logging.info("Transport widget initialized with camera and csi.")

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

class Detector(QWidget):
    """
    Widget for the right dock: 1 column, 2 rows.
    Row 1: FileManagerWidget
    Row 2: Transport widget
    """

    def __init__(self, cam=None, csi=0, modes=None, preview=None, parent=None):
        """
        Initialize the Classifier widget.

        Args:
            cam: Camera object.
            csi: Camera serial interface index.
            modes: List of camera modes.
            preview: Preview widget.
            parent: Parent QWidget.
        """
        super().__init__(parent)
        layout = QVBoxLayout()
        file_manager_widget = FileManagerWidget()
        layout.addWidget(file_manager_widget)

        # Add a visible separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        palette = self.palette()
        bg_color = palette.color(palette.Dark).name()
        separator.setStyleSheet(f"background-color: {bg_color}; height: 2px; border: none;")
        layout.addWidget(separator)

        layout.addWidget(Transport(cam=cam, csi=csi, modes=modes, file_manager=file_manager_widget, preview=preview))
        self.setLayout(layout)
        logging.info("Classifier widget initialized.")