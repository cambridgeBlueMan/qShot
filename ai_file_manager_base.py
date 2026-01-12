from qt import QtWidgets, QtGui, QtCore, Qt
# ai_file_manager_base.py
from abc import ABC, abstractmethod
import os
import logging


class AIFileManager(QtWidgets.QWidget):
    """
    Abstract base class for file manager widgets with extensible, unified settings management.
    Subclasses can extend the settings_schema to add their own settings.
    """

    # Subclasses can extend this dict with their own settings
    settings_schema = {
        "dataset_path": {"type": str, "default": ""},
        "class_labels_path": {"type": str, "default": ""},
        "jpeg_quality": {"type": int, "default": 95},
    }

    def __init__(self, parent=None, settings_group=None):
        super().__init__(parent)
        self.settings = QtCore.QSettings("MyCompany", "CameraCaptureApp")
        self.settings_group = settings_group  # e.g., "detector" or "classifier"
        self.base_layout = QtWidgets.QVBoxLayout()
        # Settings data dict, initialized from schema
        self.settings_data = {k: v["default"] for k, v in self.settings_schema.items()}
        self.init_base_ui()
        self.load_settings()
        # Do NOT call self.setLayout(self.base_layout) here!

        # Connect text changes to validation (add this after creating inputs)
        self.dataset_path_input.textChanged.connect(self._on_paths_changed)
        self.class_labels_input.textChanged.connect(self._on_paths_changed)

    def init_base_ui(self): 
        layout = QtWidgets.QGridLayout()

        # Dataset Path
        layout.addWidget(QtWidgets.QLabel("Dataset Path"), 0, 0)
        self.dataset_path_input = QtWidgets.QLineEdit()
        layout.addWidget(self.dataset_path_input, 0, 1)
        dataset_path_button = QtWidgets.QPushButton("...")
        dataset_path_button.clicked.connect(self.select_dataset_path)
        layout.addWidget(dataset_path_button, 0, 2)

        # Class Labels
        layout.addWidget(QtWidgets.QLabel("Class Labels"), 1, 0)
        self.class_labels_input = QtWidgets.QLineEdit()
        layout.addWidget(self.class_labels_input, 1, 1)
        class_labels_button = QtWidgets.QPushButton("...")
        class_labels_button.clicked.connect(self.select_class_labels_file)
        layout.addWidget(class_labels_button, 1, 2)

        # Init Button
        self.init_button = QtWidgets.QPushButton("Init")
        self.init_button.clicked.connect(self.init_action)
        layout.addWidget(self.init_button, 2, 2)

        # Row: JPEG Quality
        layout.addWidget(QtWidgets.QLabel("jpeg quality"), 5, 0)
        self.jpeg_quality_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.jpeg_quality_slider.setValue(95)
        self.jpeg_quality_slider.setMinimum(0)
        self.jpeg_quality_slider.setMaximum(100)
        self.jpeg_quality_slider.valueChanged.connect(self.save_settings)
        layout.addWidget(self.jpeg_quality_slider, 5, 1)

        self.base_layout.addLayout(layout)

    def select_dataset_path(self):
        """Open a dialog to select the dataset folder and save the setting."""
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Dataset Folder")
        if path:
            self.dataset_path_input.setText(path)
            self.save_settings()

    def select_class_labels_file(self):
        """Open a dialog to select the class labels file and save the setting."""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Class Labels File", filter="Text Files (*.txt)")
        if path:
            self.class_labels_input.setText(path)
            self.save_settings()


    def save_settings(self):
        """Save all settings in settings_data to persistent storage under a group."""
        # Update settings_data from UI widgets (base class only; subclasses should extend if needed)
        self.settings_data["dataset_path"] = self.dataset_path_input.text()
        self.settings_data["class_labels_path"] = self.class_labels_input.text()
        self.settings_data["jpeg_quality"] = self.jpeg_quality_slider.value()
        if self.settings_group:
            self.settings.beginGroup(self.settings_group)
        for key, value in self.settings_data.items():
            self.settings.setValue(key, value)
        if self.settings_group:
            self.settings.endGroup()


    def load_settings(self):
        """Load all settings in settings_schema from persistent storage under a group."""
        if self.settings_group:
            self.settings.beginGroup(self.settings_group)
        for key, meta in self.settings_schema.items():
            value = self.settings.value(key, meta["default"])
            # Convert to correct type
            try:
                value = meta["type"](value)
            except Exception:
                value = meta["default"]
            self.settings_data[key] = value
        if self.settings_group:
            self.settings.endGroup()

        # Update UI widgets from settings_data (base class only; subclasses should extend if needed)
        dataset_path = self.settings_data["dataset_path"]
        labels_path = self.settings_data["class_labels_path"]
        if os.path.isdir(dataset_path):
            self.dataset_path_input.setText(dataset_path)
        else:
            self.dataset_path_input.setText("")
            if dataset_path:
                logging.info(f"Saved dataset path does not exist: {dataset_path}. Field left empty.")
        if labels_path and os.path.isfile(labels_path):
            logging.info(f"Setting labels path: {labels_path}")
            self.class_labels_input.setText(labels_path)
        else:
            self.class_labels_input.setText("")
            if labels_path:
                logging.info(f"Saved labels path does not exist: {labels_path}. Field left empty.")
        self.jpeg_quality_slider.setValue(self.settings_data["jpeg_quality"])

    def _on_paths_changed(self):
        """Called when dataset or labels path changes."""
        # Find any child widget that has the validate_and_update_buttons method
        for child in self.findChildren(QtWidgets.QWidget):
            if hasattr(child, 'validate_and_update_buttons'):
                child.validate_and_update_buttons()

    def get_new_file_path(self, set_value=None, class_value=None, ext=".jpg"):
        import datetime
        dataset_path = self.dataset_path_input.text()
        set_value = set_value or (self.current_set_dropdown.currentText() if hasattr(self, "current_set_dropdown") and self.current_set_dropdown.count() else "unknown_set")
        class_value = class_value or (self.current_class_dropdown.currentText() if hasattr(self, "current_class_dropdown") and self.current_class_dropdown.count() else "unknown_class")
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = os.path.join(
            dataset_path,
            set_value,
            class_value,
            f"{class_value}_{timestamp}{ext}"
        )
        logging.info(f"Generated file path: {file_path}")
        return file_path

    def ensure_dataset_structure(self, class_labels, sets=("train", "test", "val")):
        dataset_path = self.dataset_path_input.text()
        for set_name in sets:
            set_dir = os.path.join(dataset_path, set_name)
            os.makedirs(set_dir, exist_ok=True)
            for class_label in class_labels:
                class_dir = os.path.join(set_dir, class_label)
                os.makedirs(class_dir, exist_ok=True)

    def load_class_labels(self):
        labels_path = self.class_labels_input.text() if hasattr(self, "class_labels_input") else ""
        if os.path.isfile(labels_path):
            with open(labels_path, "r") as f:
                labels = [line.strip() for line in f if line.strip()]
            return labels
        return []

    def update_image_count(self, set_value=None, class_value=None):
        dataset_path = self.dataset_path_input.text()
        set_value = set_value or (self.current_set_dropdown.currentText() if hasattr(self, "current_set_dropdown") else None)
        class_value = class_value or (self.current_class_dropdown.currentText() if hasattr(self, "current_class_dropdown") else None)
        count = 0
        if dataset_path and set_value and class_value:
            folder = os.path.join(dataset_path, set_value, class_value)
            if os.path.isdir(folder):
                count = len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])
        if hasattr(self, "image_count_label"):
            self.image_count_label.setText(str(count))