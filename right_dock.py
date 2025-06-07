import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox
from PyQt5.QtGui import QIcon
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
    Transport widget that receives camera and csi information and provides player controls.
    """
    def __init__(self, cam=None, csi=0, modes=None, parent=None):
        super().__init__(parent)
        self.cam = cam
        self.csi = csi
        self.modes = modes

        main_layout = QVBoxLayout()
        self._add_sensor_mode_dropdown(main_layout, modes)

        controls_layout = QHBoxLayout()
        self._add_player_controls(controls_layout)
        main_layout.addLayout(controls_layout)

        self.setLayout(main_layout)
        logging.info("Transport widget initialized with camera and csi.")

    def _add_player_controls(self, layout):
        # Start button
        start_btn = QPushButton()
        start_btn.setIcon(QIcon.fromTheme("media-playback-start"))
        start_btn.setToolTip("Start")

        # Stop button
        stop_btn = QPushButton()
        stop_btn.setIcon(QIcon.fromTheme("media-playback-stop"))
        stop_btn.setToolTip("Stop")

        # Pause button
        pause_btn = QPushButton()
        pause_btn.setIcon(QIcon.fromTheme("media-playback-pause"))
        pause_btn.setToolTip("Pause")

        # Resume button
        resume_btn = QPushButton()
        resume_btn.setIcon(QIcon.fromTheme("media-playback-play"))  # Often same as start
        resume_btn.setToolTip("Resume")

        # Add buttons to layout
        layout.addWidget(start_btn)
        layout.addWidget(stop_btn)
        layout.addWidget(pause_btn)
        layout.addWidget(resume_btn)
        logging.info("Player controls added to Transport widget.")

    def _add_sensor_mode_dropdown(self, layout, modes):
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
    def __init__(self, cam=None, csi=0, modes=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(FileManagerWidget())
        layout.addWidget(Transport(cam=cam, csi=csi, modes=modes))
        self.setLayout(layout)
        logging.info("RightDock widget initialized.")