import os
import logging
from ai_file_manager_base import AIFileManager

class BaseAIFileManager(AIFileManager):
    """
    Base class for AI file manager widgets.
    Handles common dataset/class/label management and file path logic.
    """
    def __init__(self, parent=None, settings_group=None):
        super().__init__(parent, settings_group=settings_group)
        self.settings_group = settings_group
        logging.info(f"{self.__class__.__name__} initialized with settings_group={settings_group}")

    def get_new_file_path(self, set_value=None, class_value=None, ext=".jpg"):
        import datetime
        dataset_path = self.dataset_path_input.text()
        set_value = set_value or (self.current_set_dropdown.currentText() if self.current_set_dropdown.count() else "unknown_set")
        class_value = class_value or (self.current_class_dropdown.currentText() if self.current_class_dropdown.count() else "unknown_class")
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
        set_value = set_value or self.current_set_dropdown.currentText()
        class_value = class_value or self.current_class_dropdown.currentText()
        count = 0
        if dataset_path and set_value and class_value:
            folder = os.path.join(dataset_path, set_value, class_value)
            if os.path.isdir(folder):
                count = len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])
        if hasattr(self, "image_count_label"):
            self.image_count_label.setText(str(count))
