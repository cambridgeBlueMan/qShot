# ai_file_manager_base.py
from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QSlider
from PyQt5.QtCore import QSettings, Qt

class AIFileManager(QWidget):
    """
    Abstract base class for file manager widgets.
    Provides dataset path, class labels, init button, and settings logic.
    """

    def __init__(self):
        super().__init__()
        self.settings = QSettings("MyCompany", "CameraCaptureApp")
        self.init_base_ui()

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
        self.jpeg_quality_slider = QSlider(Qt.Horizontal)
        self.jpeg_quality_slider.setValue(95)
        self.jpeg_quality_slider.setMinimum(0)
        self.jpeg_quality_slider.setMaximum(100)
        self.jpeg_quality_slider.valueChanged.connect(self.save_settings)
        layout.addWidget(self.jpeg_quality_slider, 5, 1)

        self.setLayout(layout)

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
        """Save dataset path and class labels path to persistent storage."""
        self.settings.setValue("dataset_path", self.dataset_path_input.text())
        self.settings.setValue("class_labels_path", self.class_labels_input.text())
        self.settings.setValue("jpeg_quality", self.jpeg_quality_slider.value())

    def load_settings(self):
        """Load dataset path and class labels path from persistent storage."""
        self.dataset_path_input.setText(self.settings.value("dataset_path", ""))
        self.class_labels_input.setText(self.settings.value("class_labels_path", ""))
        self.jpeg_quality_slider.setValue(int(self.settings.value("jpeg_quality", 95)))

    @abstractmethod
    def get_new_file_path(self):
        """Generate a new file path based on the dataset path, set, and class."""
        pass

    @abstractmethod
    def init_action(self):
        """Initialize directories and populate dropdowns."""
        pass