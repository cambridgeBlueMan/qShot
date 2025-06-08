import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QLineEdit, QDoubleSpinBox, QFrame
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
    """
    def __init__(self, cam=None, csi=0, modes=None, file_manager=None, preview=None, parent=None):
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

        self.setLayout(main_layout)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        logging.info("Transport widget initialized with camera and csi.")

    def _capture_done(self, job):
        result = self.cam.wait(job)
        self.capture_btn.setDisabled(False)

    def capture_image(self):
        logging.info("Capture button pressed.")
        # Disable the button to prevent multiple clicks
        self.capture_btn.setDisabled(True)
        if self.preview and hasattr(self.preview, "done_signal"):
            self.preview.done_signal.connect(self._capture_done)
        # Get a file name from the file manager widget if available
        if self.file_manager and hasattr(self.file_manager, "get_new_file_path"):
            file_name = self.file_manager.get_new_file_path()
            logging.info(f"Generated file path from FileManagerWidget: {file_name}")
            signal_function = self.preview.signal_done if self.preview and hasattr(self.preview, "signal_done") else None
            self.cam.capture_file(file_name, signal_function=signal_function)  # Pass signal_function as argument
        else:
            logging.info("FileManagerWidget not available or does not have get_new_file_path().")
        # Implement image capture logic here

    def toggle_sequence_capture(self):
        logging.info("Sequence capture button pressed.")
        self.sequence_running = not self.sequence_running
        if self.sequence_running:
            self.sequence_timer.start(500)  # Flash every 500 ms
        else:
            self.sequence_timer.stop()
            self.sequence_btn.setStyleSheet("")  # Reset to default

    def _flash_sequence_btn(self):
        # Alternate the button's background color
        if self.sequence_flash_on:
            self.sequence_btn.setStyleSheet("")
        else:
            self.sequence_btn.setStyleSheet("background-color: red; color: white;")
        self.sequence_flash_on = not self.sequence_flash_on

    def _add_sensor_mode_dropdown(self, layout, modes, combo=None):
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

class RightDock(QWidget):
    """
    Widget for the right dock: 1 column, 2 rows.
    Row 1: FileManagerWidget
    Row 2: Transport widget
    """
    def __init__(self, cam=None, csi=0, modes=None, preview=None, parent=None):
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
        logging.info("RightDock widget initialized.")