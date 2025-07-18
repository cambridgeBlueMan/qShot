import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QSlider, QFileDialog
)
from PyQt6.QtCore import Qt, QSettings
from ai_file_manager_base import AIFileManager  # Import the base class

# Configure logging to overwrite the log file on each run
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)

IMG_EXT = ".jpg"
IMG_PREFIX = "image_"


class FileManagerWidget(AIFileManager):
    """
    A widget for managing files in a dataset directory.
    Extends AIFileManager with additional UI and logic.
    """

    def __init__(self):
        """
        Initialize the FileManagerWidget.

        Sets up the UI, loads saved settings, and initializes actions.
        """
        super().__init__()
        self.setWindowTitle("Camera Capture Widgets")
        self.settings = QSettings("MyCompany", "CameraCaptureApp")  # Organization and app name
        self.resize(500, 250)  # Adjust the width and height (30% wider)
        self.initUI()
        self.load_settings()  # Load saved settings on startup
        self.init_action()  # Initialize the action to create directories and populate dropdowns
        logging.info("FileManagerWidget initialized.")

    def initUI(self):
        """
        Set up the user interface for the FileManagerWidget.

        Creates layout, input fields, buttons, sliders, and dropdowns.
        Connects dropdown changes to status updates.
        """
        layout = QGridLayout()

        # Adjust column widths
        layout.setColumnStretch(0, 1)  # Column 1: Good width
        layout.setColumnStretch(1, 5)  # Column 2: 50% wider for full path and file name
        layout.setColumnStretch(2, 1)  # Column 3: Smaller, but label still fully displayed

        # Row 1: Dataset Path
        layout.addWidget(QLabel("Dataset Path"), 0, 0)
        self.dataset_path_input = QLineEdit()
        layout.addWidget(self.dataset_path_input, 0, 1)
        dataset_path_button = QPushButton("...")
        dataset_path_button.clicked.connect(self.select_dataset_path)
        layout.addWidget(dataset_path_button, 0, 2)

        # Row 2: Class Labels
        layout.addWidget(QLabel("Class Labels"), 1, 0)
        self.class_labels_input = QLineEdit()
        layout.addWidget(self.class_labels_input, 1, 1)
        class_labels_button = QPushButton("...")
        class_labels_button.clicked.connect(self.select_class_labels_file)
        layout.addWidget(class_labels_button, 1, 2)

        # Row 3: Init Row
        # First two columns are empty
        init_button = QPushButton("Init")
        init_button.clicked.connect(self.init_action)
        layout.addWidget(init_button, 2, 2)

        # Row 4: Current Set
        layout.addWidget(QLabel("current set"), 3, 0)
        self.current_set_dropdown = QComboBox()
        layout.addWidget(self.current_set_dropdown, 3, 1)

        # Row 5: Current Class
        layout.addWidget(QLabel("current class"), 4, 0)
        self.current_class_dropdown = QComboBox()
        layout.addWidget(self.current_class_dropdown, 4, 1)

        # Row 6: JPEG Quality
        layout.addWidget(QLabel("jpeg quality"), 5, 0)
        self.jpeg_quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.jpeg_quality_slider.setValue(95)
        self.jpeg_quality_slider.setMinimum(0)
        self.jpeg_quality_slider.setMaximum(100)
        self.jpeg_quality_slider.valueChanged.connect(self.save_settings)  # Save slider value on change
        layout.addWidget(self.jpeg_quality_slider, 5, 1)

        # Row 7: Status
        layout.addWidget(QLabel("status"), 6, 0)
        self.status_label = QLabel("empty label")
        layout.addWidget(self.status_label, 6, 1)

        self.setLayout(layout)

        # Connect dropdown changes to status update
        self.current_set_dropdown.currentIndexChanged.connect(self.update_status_label)
        self.current_class_dropdown.currentIndexChanged.connect(self.update_status_label)
        logging.info("UI initialized for FileManagerWidget.")

    def select_dataset_path(self):
        """
        Open a dialog to select the dataset folder.

        Updates the dataset path input field and saves the setting.
        """
        path = QFileDialog.getExistingDirectory(self, "Select Dataset Folder")
        if path:
            self.dataset_path_input.setText(path)
            self.save_settings()  # Save dataset path
            logging.info(f"Dataset path selected: {path}")

    def select_class_labels_file(self):
        """
        Open a dialog to select the class labels file.

        Updates the class labels input field and saves the setting.
        """
        path, _ = QFileDialog.getOpenFileName(self, "Select Class Labels File", filter="Text Files (*.txt)")
        if path:
            self.class_labels_input.setText(path)
            self.save_settings()  # Save class labels path
            logging.info(f"Class labels file selected: {path}")

    def save_settings(self):
        """
        Save settings to persistent storage.

        Includes dataset path, class labels path, and JPEG quality slider value.
        """
        self.settings.setValue("dataset_path", self.dataset_path_input.text())
        self.settings.setValue("class_labels_path", self.class_labels_input.text())
        self.settings.setValue("jpeg_quality", self.jpeg_quality_slider.value())
        logging.info("Settings saved.")

    def load_settings(self):
        """
        Load settings from persistent storage.

        Restores dataset path, class labels path, and JPEG quality slider value.
        """
        self.dataset_path_input.setText(self.settings.value("dataset_path", ""))
        self.class_labels_input.setText(self.settings.value("class_labels_path", ""))
        self.jpeg_quality_slider.setValue(int(self.settings.value("jpeg_quality", 95)))
        logging.info("Settings loaded.")

    def init_action(self):
        """
        Validate inputs, create directories, and populate dropdowns.

        Checks if the dataset path is valid and if the class labels file exists.
        Creates directories for training, testing, and validation sets.
        Populates dropdowns with sets and classes.
        """
        import os

        dataset_path = self.dataset_path_input.text()
        class_labels_path = self.class_labels_input.text()

        # Validate dataset path
        if not os.path.isdir(dataset_path):
            print("Invalid dataset folder!")
            self.status_label.setText("Invalid dataset folder!")
            logging.warning("Invalid dataset folder!")
            return

        # Validate class labels file
        if not os.path.isfile(class_labels_path) or not class_labels_path.endswith(".txt"):
            print("Invalid class labels file!")
            self.status_label.setText("Invalid class labels file!")
            logging.warning("Invalid class labels file!")
            return

        # Read class labels and create directories
        try:
            types = ["train", "test", "val"]
            with open(class_labels_path, "r") as file:
                labels = [line.strip() for line in file if line.strip()]

            # Create directories
            for type_ in types:
                type_dir = os.path.join(dataset_path, type_)
                os.makedirs(type_dir, exist_ok=True)  # Create type directory
                for label in labels:
                    label_dir = os.path.join(type_dir, label)
                    os.makedirs(label_dir, exist_ok=True)  # Create label subdirectory

            # Populate dropdowns
            self.current_set_dropdown.clear()
            self.current_set_dropdown.addItems(types)

            self.current_class_dropdown.clear()
            self.current_class_dropdown.addItems(labels)

            print("Directories created and dropdowns populated successfully!")
            self.status_label.setText("Initialization successful!")
            logging.info("Directories created and dropdowns populated successfully.")
        except Exception as e:
            print(f"Error creating directories: {e}")
            self.status_label.setText(f"Error: {e}")
            logging.error(f"Error creating directories: {e}")

    def update_status_label(self):
        """
        Update the status label with the count of .jpg files in the selected folder.

        Counts the number of .jpg files in the folder corresponding to the selected set and class.
        """
        import os

        dataset_path = self.dataset_path_input.text()
        selected_set = self.current_set_dropdown.currentText()  # Get selected set from dropdown
        selected_class = self.current_class_dropdown.currentText()  # Get selected class from dropdown

        # Determine the folder path for the selected set and class
        folder_path = os.path.join(dataset_path, selected_set, selected_class)

        # Count the number of .jpg files in the folder
        if os.path.isdir(folder_path):
            jpg_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".jpg")]
            jpg_count = len(jpg_files)
            self.status_label.setText(f"{jpg_count} .jpg files in {selected_set}/{selected_class}")
            logging.info(f"{jpg_count} .jpg files in {selected_set}/{selected_class}")
        else:
            self.status_label.setText(f"Folder {selected_set}/{selected_class} does not exist!")
            logging.warning(f"Folder {selected_set}/{selected_class} does not exist!")

    def get_new_file_path(self):
        """
        Generate a new file path based on the dataset path, selected set, and class.

        Uses the selected set and class to determine the folder path.
        Generates a timestamp-based filename and assembles the full file path.
        """
        import os
        from datetime import datetime

        # Update the status label
        # self.update_status_label()

        dataset_path = self.dataset_path_input.text()
        selected_set = self.current_set_dropdown.currentText()  # Get selected set from dropdown
        selected_class = self.current_class_dropdown.currentText()  # Get selected class from dropdown

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Format: YYYYMMDDHHMMSS

        # Assemble file path
        file_path = os.path.join(
            dataset_path,
            selected_set,  # Add the selected set as a subdirectory
            selected_class,  # Add the selected class as a subdirectory
            f"{selected_class}_{timestamp}{IMG_EXT}"  # Use selected_class in the filename
        )

        print(f"Generated file path: {file_path}")  # Diagnostic print statement
        logging.info(f"Generated file path: {file_path}")
        return file_path


if __name__ == "__main__":
    """
    Entry point for the application.

    Creates and displays the FileManagerWidget.
    """
    app = QApplication(sys.argv)
    window = FileManagerWidget()  # Update instantiation to use FileManagerWidget
    window.show()
    window.get_new_file_path()  # Call to generate a new file path
    sys.exit(app.exec_())