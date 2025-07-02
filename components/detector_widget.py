import logging
import os
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QCheckBox, QHeaderView,
    QTableWidget, QTableWidgetItem, QDialog, QFrame, QWidget  # <-- Add QWidget here
)
from PyQt5.QtCore import Qt
from ai_file_manager_base import AIFileManager
from components.bboxlabel import BBoxLabel
from generate_color import generate_color
import importlib.util

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)

class SaveChangesDialog(QDialog):
    """Dialog to confirm saving changes when leaving a frozen image."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save Changes?")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("You have a frozen image. Save changes before leaving?"))
        btn_yes = QPushButton("Yes")
        btn_no = QPushButton("No")
        btn_yes.clicked.connect(lambda: self.done(1))
        btn_no.clicked.connect(lambda: self.done(0))
        layout.addWidget(btn_yes)
        layout.addWidget(btn_no)
        self.setLayout(layout)

class CameraManager(QWidget):
    """
    CameraManager widget that receives camera and csi information and provides capture controls.
    Handles single image capture and UI feedback.
    """

    def __init__(self, cam=None, csi=0, modes=None, file_manager=None, preview=None, parent=None):
        super().__init__(parent)
        self.cam = cam
        self.csi = csi
        self.modes = modes
        self.file_manager = file_manager
        self.preview = preview
        self.frozen = False  # Track freeze state

        main_layout = QVBoxLayout()
        main_layout.setSpacing(4)  # Reduce vertical spacing between rows

        # Camera Mode row
        camera_mode_layout = QHBoxLayout()
        camera_mode_label = QLabel("Camera Mode")
        camera_mode_layout.addWidget(camera_mode_label)
        combo = QComboBox()
        self._add_sensor_mode_dropdown(camera_mode_layout, modes, combo=combo)
        main_layout.addLayout(camera_mode_layout)

        self.setLayout(main_layout)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        logging.info("CameraManager widget initialized with camera and csi.")

    def toggle_freeze(self):
        if not self.frozen:
            self.freeze_image()
        else:
            self.restore_preview()

    def freeze_image(self):
        logging.info("Freeze button pressed.")
        if self.preview and hasattr(self.preview, "done_signal"):
            try:
                self.preview.done_signal.disconnect(self._capture_done)
            except Exception:
                pass  # Not previously connected
            self.preview.done_signal.connect(self._capture_done)
        self._current_job = self.cam.capture_array(signal_function=self.preview.signal_done)
        logging.info("Async image capture started.")

    def _capture_done(self, job):
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

                main_window = self.window()
                if hasattr(main_window, "central_stack"):
                    # Remove previous captured image label if exists
                    if hasattr(main_window, "_captured_image_label") and main_window._captured_image_label:
                        main_window.central_stack.removeWidget(main_window._captured_image_label)
                        main_window._captured_image_label.deleteLater()
                        main_window._captured_image_label = None
                    # Create and show the BBoxLabel with the captured image
                    label = BBoxLabel()
                    label.setPixmap(pixmap)
                    label.setMinimumSize(320, 240)
                    main_window.central_stack.addWidget(label)
                    main_window.central_stack.setCurrentWidget(label)
                    main_window._captured_image_label = label
                    self.frozen = True
                    logging.info("Displayed captured image in central widget.")
                else:
                    logging.error("MainWindow does not have a 'central_stack' attribute.")
            else:
                logging.error("Failed to capture image: img_array is None.")

        except Exception as e:
            logging.error(f"Error in async image capture: {e}")

    def restore_preview(self):
        """Restore the live preview widget."""
        main_window = self.window()
        if hasattr(main_window, "central_stack"):
            main_window.central_stack.setCurrentWidget(main_window.preview)
            if hasattr(main_window, "_captured_image_label") and main_window._captured_image_label:
                main_window.central_stack.removeWidget(main_window._captured_image_label)
                main_window._captured_image_label.deleteLater()
                main_window._captured_image_label = None
            self.frozen = False
            logging.info("Restored live preview in central widget.")
        else:
            logging.error("MainWindow does not have a 'central_stack' attribute.")

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

    def cleanup(self):
        """
        Called when the Detector component is being removed.
        Shows a save dialog if frozen, and always restores preview.
        """
        print("CameraManager.cleanup called")
        print(f"CameraManager.cleanup: frozen={self.frozen}")
        if self.frozen:
            print("Showing SaveChangesDialog")
            dlg = SaveChangesDialog(self)
            dlg.exec_()
            self.restore_preview()  # Always restore preview and remove frozen image

class Detector(AIFileManager):
    """
    Detector widget for annotation. Inherits file management UI from AIFileManager.
    """

    def __init__(self, cam=None, csi=0, modes=None, preview=None, parent=None, settings_group=None):
        logging.info(f"Loading Detector component with settings_group={settings_group}")
        super().__init__(parent, settings_group=settings_group)
        self.cam = cam
        self.csi = csi
        self.modes = modes
        self.preview = preview

        # --- CameraManager ---
        self.camera_manager = CameraManager(cam=cam, csi=csi, modes=modes, file_manager=self, preview=preview)
        self.base_layout.addWidget(self.camera_manager)

        # --- Table Widget for bounding boxes ---
        self.bbox_table = QTableWidget(0, 6)
        self.bbox_table.setHorizontalHeaderLabels(["Class", "X", "Y", "Width", "Height", "Delete"])
        self.bbox_table.verticalHeader().setVisible(False)
        self.bbox_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.bbox_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.bbox_table.setSelectionMode(QTableWidget.SingleSelection)
        self.bbox_table.setMinimumHeight(150)
        header = self.bbox_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.base_layout.addWidget(self.bbox_table)

        # --- Checkboxes row ---
        checkbox_layout = QHBoxLayout()
        self.save_on_unfreeze_cb = QCheckBox("Save on Unfreeze")
        self.clear_on_unfreeze_cb = QCheckBox("Clear on Unfreeze")
        self.merge_sets_cb = QCheckBox("Merge Sets")
        checkbox_layout.addWidget(self.save_on_unfreeze_cb)
        checkbox_layout.addWidget(self.clear_on_unfreeze_cb)
        checkbox_layout.addWidget(self.merge_sets_cb)
        self.base_layout.addLayout(checkbox_layout)

        # --- Freeze/Unfreeze and Save Buttons row ---
        button_row = QHBoxLayout()
        self.freeze_btn = QPushButton("Freeze")
        self.freeze_btn.setToolTip("Freeze the current camera image or return to live preview")
        self.freeze_btn.clicked.connect(self.handle_freeze_clicked)
        button_row.addWidget(self.freeze_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.setToolTip("Save current bounding boxes or annotations")
        # self.save_btn.clicked.connect(self.save_annotations)  # Implement as needed
        button_row.addWidget(self.save_btn)

        self.base_layout.addLayout(button_row)

        self.setLayout(self.base_layout)
        logging.info("Detector widget initialized.")

    def load_class_labels(self):
        """Load class labels from the labels.txt file specified in settings."""
        labels_path = None
        if hasattr(self, "settings_group") and hasattr(self, "settings"):
            self.settings.beginGroup(self.settings_group or "General")
            labels_path = self.settings.value("class_labels_path", type=str)
            self.settings.endGroup()
        logging.info(f"Loading class labels from: {labels_path}")
        if labels_path and os.path.exists(labels_path):
            with open(labels_path, "r") as f:
                labels = [line.strip() for line in f if line.strip()]
                logging.info(f"Loaded labels: {labels}")
                return labels
        logging.warning("No labels found or labels.txt missing.")
        return []

    def handle_freeze_clicked(self):
        self.freeze_btn.setDisabled(True)
        was_frozen = self.camera_manager.frozen
        self.camera_manager.toggle_freeze()
        # Only add a row when going from preview to frozen
        if not was_frozen:
            self.add_bbox_row()
        self.update_freeze_button()

    def update_freeze_button(self):
        self.freeze_btn.setDisabled(False)
        if self.camera_manager.frozen:
            self.freeze_btn.setText("Unfreeze")
        else:
            self.freeze_btn.setText("Freeze")

    def add_bbox_row(self, class_name=None, x=0, y=0, width=0, height=0):
        class_labels = self.load_class_labels()
        row = self.bbox_table.rowCount()
        self.bbox_table.insertRow(row)
        class_combo = QComboBox()
        if class_labels:
            class_combo.addItems(class_labels)
        else:
            class_combo.addItem("No labels found")
        if class_name and class_name in class_labels:
            class_combo.setCurrentText(class_name)
        self.bbox_table.setCellWidget(row, 0, class_combo)
        self.bbox_table.setItem(row, 1, QTableWidgetItem(str(x)))
        self.bbox_table.setItem(row, 2, QTableWidgetItem(str(y)))
        self.bbox_table.setItem(row, 3, QTableWidgetItem(str(width)))
        self.bbox_table.setItem(row, 4, QTableWidgetItem(str(height)))
        delete_btn = QPushButton("Delete")
        self.bbox_table.setCellWidget(row, 5, delete_btn)

    def load_component_widget(self):
        action = self.sender()
        name = action.data()
        class_name = None
        module_name = None
        try:
            module_name = f"{name}_widget"
            module_path = os.path.join(os.path.dirname(__file__), "components", f"{module_name}.py")
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            class_name = name.capitalize()
            widget_class = getattr(module, class_name)
            widget_instance = widget_class(**self.get_component_args(name))
            widget_instance.setWindowTitle(class_name)
            old_widget = self.right_dock.widget()
            if old_widget is not None:
                if hasattr(old_widget, "cleanup"):
                    old_widget.cleanup()
                old_widget.deleteLater()
            self.right_dock.setWidget(widget_instance)
            self.right_dock.show()
            logging.info(f"Instantiated and inserted widget: {class_name} into right dock (previous content cleaned up)")
        except Exception as e:
            logging.error(f"Failed to load or instantiate {class_name} from {module_name}: {e}")
            QMessageBox.critical(self, "Error", f"Could not load component '{class_name}':\n{e}")