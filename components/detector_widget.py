import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QFrame
from PyQt5.QtCore import Qt
from ai_file_manager import FileManagerWidget
from ai_file_manager_base import AIFileManager

# Configure logging to overwrite the log file on each run
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s' ,
    filename='app.log',
    filemode='w'
)

class Transport(QWidget): 
    """
    Transport widget that receives camera and csi information and provides capture controls.
    Handles single image capture and UI feedback.
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

        main_layout = QVBoxLayout()
        main_layout.setSpacing(4)  # Reduce vertical spacing between rows

        # Camera Mode row
        camera_mode_layout = QHBoxLayout()
        camera_mode_label = QLabel("Camera Mode")
        camera_mode_layout.addWidget(camera_mode_label)
        combo = QComboBox()
        self._add_sensor_mode_dropdown(camera_mode_layout, modes, combo=combo)
        main_layout.addLayout(camera_mode_layout)

        # Capture button row (its own row)
        capture_layout = QHBoxLayout()
        self.capture_btn = QPushButton("Capture Image")
        self.capture_btn.setToolTip("Capture Image")
        self.capture_btn.clicked.connect(self.capture_image)
        capture_layout.addWidget(self.capture_btn)
        main_layout.addLayout(capture_layout)

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
            # Keep the signal_function logic
            signal_function = getattr(self, "signal_function", None)
            if signal_function:
                self.cam.capture_file(file_name, signal_function=signal_function)
            else:
                self.cam.capture_file(file_name)
        else:
            logging.info("FileManagerWidget not available or does not have get_new_file_path().")

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

class Detector(AIFileManager):
    """
    Widget for the right dock: 1 column, 2 rows.
    Row 1: FileManagerWidget
    Row 2: Transport widget
    """

    def __init__(self, cam=None, csi=0, modes=None, preview=None, parent=None, settings_group=None):
        """
        Initialize the Detector widget.

        Args:
            cam: Camera object.
            csi: Camera serial interface index.
            modes: List of camera modes.
            preview: Preview widget.
            parent: Parent QWidget.
            settings_group: QSettings group name.
        """
        super().__init__(parent, settings_group=settings_group)
        self.cam = cam
        self.csi = csi
        self.modes = modes
        self.preview = preview

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
        logging.info("Detector widget initialized.")

    def get_new_file_path(self):
        # Implement this method
        pass

    def init_action(self):
        # Implement this method
        pass