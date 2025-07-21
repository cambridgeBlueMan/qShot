# ai_file_manager_base.py
from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QSlider, QVBoxLayout
from PyQt6.QtCore import QSettings, Qt
import os
import logging

class AIFileManager(QWidget):
    """
    Abstract base class for file manager widgets.

    Layout and Usage:
    -----------------
    - This class creates a vertical box layout (`self.base_layout`) as the main container.
    - A grid layout is created and added to `self.base_layout` in `init_base_ui()`.
      The grid layout contains all the core file management widgets:
        * Dataset path selector
        * Class labels file selector
        * JPEG quality slider
        * Init button
    - The expectation is that subclasses will add additional layouts or widgets
      to `self.base_layout` (e.g., below the grid), allowing flexible extension
      of the UI while preserving the file management controls at the top.

    Features:
    ---------
    - Provides persistent settings management for dataset path, class labels, and JPEG quality.
    - Offers abstract methods (`get_new_file_path`, `init_action`) that must be implemented by subclasses.
    - Handles loading and saving of settings automatically.
    - Designed for extensibility: inherited classes can add more widgets/layouts to `self.base_layout`.

    Typical subclass usage:
    ----------------------
    class MyComponent(AIFileManager):
        def __init__(self, ...):
            super().__init__(...)
            # Add custom widgets/layouts below the file manager controls
            self.base_layout.addWidget(MyCustomWidget())
            # etc.

        def get_new_file_path(self):
            # Implementation here

        def init_action(self):
            # Implementation here
    """

    def __init__(self, parent=None, settings_group=None):
        super().__init__(parent)
        self.settings = QSettings("MyCompany", "CameraCaptureApp")
        self.settings_group = settings_group  # e.g., "detector" or "classifier"
        self.base_layout = QVBoxLayout()
        self.init_base_ui()
        self.load_settings()  # <-- Add this line!
        # Do NOT call self.setLayout(self.base_layout) here!

        # Connect text changes to validation (add this after creating inputs)
        self.dataset_path_input.textChanged.connect(self._on_paths_changed)
        self.class_labels_input.textChanged.connect(self._on_paths_changed)

    def init_base_ui(self): 
        layout = QGridLayout()

        # Dataset Path
        layout.addWidget(QLabel("Dataset Path"), 0, 0)
        self.dataset_path_input = QLineEdit()
        layout.addWidget(self.dataset_path_input, 0, 1)
        dataset_path_button = QPushButton("...")
        dataset_path_button.clicked.connect(self.select_dataset_path)
        layout.addWidget(dataset_path_button, 0, 2)

        # Class Labels
        layout.addWidget(QLabel("Class Labels"), 1, 0)
        self.class_labels_input = QLineEdit()
        layout.addWidget(self.class_labels_input, 1, 1)
        class_labels_button = QPushButton("...")
        class_labels_button.clicked.connect(self.select_class_labels_file)
        layout.addWidget(class_labels_button, 1, 2)

        # Init Button
        self.init_button = QPushButton("Init")
        self.init_button.clicked.connect(self.init_action)
        layout.addWidget(self.init_button, 2, 2)

        # Row: JPEG Quality
        layout.addWidget(QLabel("jpeg quality"), 5, 0)
        self.jpeg_quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.jpeg_quality_slider.setValue(95)
        self.jpeg_quality_slider.setMinimum(0)
        self.jpeg_quality_slider.setMaximum(100)
        self.jpeg_quality_slider.valueChanged.connect(self.save_settings)
        layout.addWidget(self.jpeg_quality_slider, 5, 1)

        self.base_layout.addLayout(layout)

    def select_dataset_path(self):
        """Open a dialog to select the dataset folder and save the setting."""
        path = QFileDialog.getExistingDirectory(self, "Select Dataset Folder")
        if path:
            self.dataset_path_input.setText(path)
            self.save_settings()

    def select_class_labels_file(self):
        """Open a dialog to select the class labels file and save the setting."""
        path, _ = QFileDialog.getOpenFileName(self, "Select Class Labels File", filter="Text Files (*.txt)")
        if path:
            self.class_labels_input.setText(path)
            self.save_settings()

    def save_settings(self):
        """Save dataset path, class labels, and jpeg quality to persistent storage under a group."""
        if self.settings_group:
            self.settings.beginGroup(self.settings_group)
        self.settings.setValue("dataset_path", self.dataset_path_input.text())
        self.settings.setValue("class_labels_path", self.class_labels_input.text())
        self.settings.setValue("jpeg_quality", self.jpeg_quality_slider.value())
        if self.settings_group:
            self.settings.endGroup()

    def load_settings(self):
        """Load dataset path, class labels, and jpeg quality from persistent storage under a group."""
        if self.settings_group:
            self.settings.beginGroup(self.settings_group)

        dataset_path = self.settings.value("dataset_path", "")
        labels_path = self.settings.value("class_labels_path", "")

        # Debug logging
        logging.info(f"Loading settings - labels_path from settings: '{labels_path}'")
        logging.info(f"labels_path type: {type(labels_path)}")
        logging.info(f"labels_path exists: {os.path.exists(labels_path)}")
        logging.info(f"labels_path isfile: {os.path.isfile(labels_path)}")

        # Dataset path - works fine
        if os.path.isdir(dataset_path):
            self.dataset_path_input.setText(dataset_path)
        else:
            self.dataset_path_input.setText("")
            if dataset_path:
                logging.info(f"Saved dataset path does not exist: {dataset_path}. Field left empty.")

        # Make labels path exactly like dataset path
        if labels_path and os.path.isfile(labels_path):
            logging.info(f"Setting labels path: {labels_path}")
            self.class_labels_input.setText(labels_path)
        else:
            self.class_labels_input.setText("")
            if labels_path:
                logging.info(f"Saved labels path does not exist: {labels_path}. Field left empty.")

        self.jpeg_quality_slider.setValue(int(self.settings.value("jpeg_quality", 95)))

        if self.settings_group:
            self.settings.endGroup()

    def _on_paths_changed(self):
        """Called when dataset or labels path changes."""
        # Find any child widget that has the validate_and_update_buttons method
        for child in self.findChildren(QWidget):
            if hasattr(child, 'validate_and_update_buttons'):
                child.validate_and_update_buttons()

    @abstractmethod
    def get_new_file_path(self):
        """Generate a new file path based on the dataset path, set, and class."""
        pass

    @abstractmethod
    def init_action(self):
        """
        Initialize directories and populate dropdowns.
        Scan the dataset path for set/class folders and populate the dropdowns.
        Also create 'train', 'test', and 'val' directories if missing.
        """
        pass