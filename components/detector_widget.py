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

class CameraManager(QWidget): 
    """
    CameraManager widget that receives camera and csi information and provides capture controls.
    Handles single image capture and UI feedback.
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
        logging.info("CameraManager widget initialized with camera and csi.")

    def capture_image(self):
        """
        Asynchronously capture a single image from the camera to a buffer/array,
        and display it in the area currently occupied by the QGlPicamera2 widget (self.preview).
        """
        logging.info("Capture button pressed.")
        self.capture_btn.setDisabled(True)

        # Connect the preview's done_signal to our handler if not already connected
        if self.preview and hasattr(self.preview, "done_signal"):
            try:
                self.preview.done_signal.disconnect(self._capture_done)
            except Exception:
                pass  # Not previously connected
            self.preview.done_signal.connect(self._capture_done)

        # Start async capture; result will be handled in _capture_done
        self._current_job = self.cam.capture_array(signal_function=self.preview.signal_done)
        logging.info("Async image capture started.")

    def _capture_done(self, job):
        """
        Slot called when image capture is done.
        Receives the Job object, waits for the result, and displays the image.
        """
        logging.info("Image capture completed (async).")
        try:
            img_array = self.cam.wait(job)
            from PyQt5.QtGui import QImage, QPixmap

            if img_array is not None:
                # Convert to RGB or RGBA QImage
                if img_array.shape[2] == 3:
                    height, width, channel = img_array.shape
                    bytes_per_line = 3 * width
                    qimg = QImage(img_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
                elif img_array.shape[2] == 4:
                    height, width, channel = img_array.shape
                    bytes_per_line = 4 * width
                    qimg = QImage(img_array.data, width, height, bytes_per_line, QImage.Format_RGBA8888)
                else:
                    raise ValueError("Unsupported image format for display.")

                pixmap = QPixmap.fromImage(qimg)

                # Swap the central widget in MainWindow with a QLabel showing the captured image
                main_window = self.window()
                if hasattr(main_window, "preview"):
                    main_window.preview.hide()
                    # Remove previous captured image label if exists
                    if hasattr(main_window, "_captured_image_label") and main_window._captured_image_label:
                        main_window._captured_image_label.hide()
                        main_window.centralWidget().layout().removeWidget(main_window._captured_image_label)
                        main_window._captured_image_label.deleteLater()
                        main_window._captured_image_label = None
                    # Create and show the QLabel with the captured image
                    label = AspectRatioPixmapLabel()
                    label.setPixmap(pixmap)
                    label.setMinimumSize(320, 240)
                    main_window.setCentralWidget(label)
                    main_window._captured_image_label = label
                    logging.info("Displayed captured image in central widget.")
                else:
                    logging.error("MainWindow does not have a 'preview' attribute.")
            else:
                logging.error("Failed to capture image: img_array is None.")

        except Exception as e:
            logging.error(f"Error in async image capture: {e}")

        self.capture_btn.setDisabled(False)

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

class AspectRatioPixmapLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        if pixmap:
            super().setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            super().setPixmap(pixmap)

    def resizeEvent(self, event):
        if self._pixmap:
            super().setPixmap(self._pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        super().resizeEvent(event)

class Detector(AIFileManager):
    """
    Widget for the right dock: 1 column, 2 rows.
    Row 1: FileManagerWidget
    Row 2: CameraManager widget
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

        layout.addWidget(CameraManager(cam=cam, csi=csi, modes=modes, file_manager=file_manager_widget, preview=preview))
        self.setLayout(layout)
        logging.info("Detector widget initialized.")

    def get_new_file_path(self):
        # Implement this method
        pass

    def init_action(self):
        # Implement this method
        pass