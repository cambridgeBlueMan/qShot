from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout, QWidget
import logging
from ai_file_manager_base import AIFileManager
from res_combo import ResCombo
# from config_model import config_model
from app_signals import app_signals  # <-- Include app_signals
from controls_model import controls_model
import pprint

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='a'
)

"""
test_widget.py

This module defines the Test component for the application. The Test class inherits from AIFileManager
and is intended as a minimal, self-contained example for experimentation, documentation, and understanding
of how to build components that integrate with the application's file management infrastructure.

The Test widget demonstrates:
- How to inherit from AIFileManager to get dataset/class label management UI for free.
- How to add custom widgets (like labels and buttons) to the base layout.
- How to implement required abstract methods from the base class.
- How to use logging and simple event handling.

This file is intended as a living example and playground for gradually building up and documenting
component development best practices in this codebase.
"""

class Test(AIFileManager):
    """
    A simple test component that inherits from AIFileManager.
    Demonstrates adding custom UI elements to the base file manager interface.
    """

    def __init__(self, **kwargs):
        # Extract known arguments with defaults
        parent = kwargs.get("parent", None)
        super().__init__(parent)

        self.cam = kwargs.get("cam")
        self.modes = kwargs.get("modes")
        self.preview = kwargs.get("preview")
        self.config_model = kwargs.get("config_model")
        self.settings_group = kwargs.get("settings_group")

        # Create widgets first
        self.label = QLabel("This is the Test widget.")
        self.button = QPushButton("Click Me")
        self.button.clicked.connect(self.on_button_clicked)
        self.res_combo = ResCombo(config_model=self.config_model)
        self.camera_mode_combo = QComboBox()
        self.framerate_combo = QComboBox()
        self.available_framerates = [5, 10, 15, 20, 25, 30, 40, 50, 60, 120]

        # Layout setup
        self.base_layout.addWidget(self.label)
        self.base_layout.addWidget(self.button)
        self.base_layout.addWidget(self.res_combo)

        mode_layout = QHBoxLayout()
        mode_label = QLabel("Camera Mode")
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.camera_mode_combo)
        self.base_layout.addLayout(mode_layout)

        fr_layout = QHBoxLayout()
        fr_label = QLabel("Frame Rate")
        fr_layout.addWidget(fr_label)
        fr_layout.addWidget(self.framerate_combo)
        self.base_layout.addLayout(fr_layout)

        self.setLayout(self.base_layout)

        # Populate mode dropdown
        self._add_sensor_mode_dropdown(self.modes)
        self.camera_mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self.framerate_combo.currentIndexChanged.connect(self._on_framerate_changed)

        # Connect signals
        app_signals.mode_changed.connect(self.on_global_mode_changed)
        if self.config_model:
            self.config_model.configChanged.connect(self.on_config_changed)

        # Initialize UI to highest mode
        if self.camera_mode_combo.count() > 0:
            self.camera_mode_combo.setCurrentIndex(self.camera_mode_combo.count() - 1)
            self._on_mode_changed(self.camera_mode_combo.currentIndex())

    def on_button_clicked(self):
        self.label.setText("Button clicked!")
        logging.info("Test widget button was clicked.")

    def get_new_file_path(self):
        # Implement the abstract method from AIFileManager
        return "test_file.txt"

    def _add_sensor_mode_dropdown(self, modes):
        self.camera_mode_combo.clear()
        if modes:
            for idx, mode in enumerate(modes):
                desc = f"{idx}: {mode.get('size', '')} {mode.get('format', '')}"
                self.camera_mode_combo.addItem(desc, userData=mode)
            logging.info(f"Sensor mode dropdown populated with {len(modes)} modes.")
        else:
            self.camera_mode_combo.addItem("No sensor modes found")
            logging.warning("No sensor modes found for dropdown.")

    def _on_mode_changed(self, index):
        mode = self.camera_mode_combo.itemData(index)
        if mode and self.config_model:
            self.config_model.set_nested('sensor', 'output_size', mode.get('size'))
            self.config_model.set_nested('sensor', 'bit_depth', mode.get('bit_depth'))
            logging.info(f"Test widget camera mode changed: {mode}")
            app_signals.mode_changed.emit(mode)

    def _on_framerate_changed(self, index):
        framerate = self.framerate_combo.itemData(index)
        if framerate:
            frame_duration = int(1e6 / framerate)
            controls_model.FrameDurationLimits = (frame_duration, frame_duration)
            logging.info(f"Test widget framerate changed: {framerate} fps (FrameDurationLimits set to ({frame_duration}, {frame_duration}))")
            pp = pprint.PrettyPrinter(indent=2)
            if self.config_model:
                pp.pprint(self.config_model.to_dict().get('main'))

    def on_global_mode_changed(self, mode):
        self.res_combo.generateComboItems(mode)
        if self.res_combo.count() > 0:
            self.res_combo.setCurrentIndex(self.res_combo.count() - 1)

        self.framerate_combo.clear()
        max_fps = mode.get("fps") if mode else None
        valid_framerates = []
        if max_fps:
            for fr in self.available_framerates:
                if fr <= max_fps:
                    self.framerate_combo.addItem(f"{fr} fps", userData=fr)
                    valid_framerates.append(fr)
        else:
            for fr in self.available_framerates:
                self.framerate_combo.addItem(f"{fr} fps", userData=fr)
                valid_framerates.append(fr)
        if self.framerate_combo.count() > 0:
            self.framerate_combo.setCurrentIndex(self.framerate_combo.count() - 1)

    def on_config_changed(self, cfg):
        cam_name = getattr(self.cam, 'camera_name', str(self.cam)) if self.cam is not None else "Unknown Camera"
        print(f"Config changed for {cam_name}:")
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(cfg.get('main'))
        if self.cam is not None:
            was_running = self.cam.started
            if was_running:
                self.cam.stop()
            self.cam.configure(cfg)
            if was_running:
                self.cam.start()
