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
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree
from PIL import Image

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

                    # Connect the signal to the Detector's add_bbox_row
                    detector_widget = self.file_manager  # Detector instance
                    detector_widget.captured_img_array = img_array  # Store for later saving
                    detector_widget.bbox_label = label   # Always set this!
                    self.bbox_label = label  # Store reference
                    label.box_completed.connect(
                        lambda x, y, w, h, class_index: detector_widget.add_bbox_row(
                            class_name=None, x=x, y=y, width=w, height=h
                        )
                    )
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

    def get_bbox_label(self):
        return getattr(self, "bbox_label", None)

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
        self.save_on_unfreeze_cb.setChecked(True)  # Default to True
        self.clear_on_unfreeze_cb = QCheckBox("Clear on Unfreeze")
        self.clear_on_unfreeze_cb.setChecked(True)  # Default to True
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
        self.update_freeze_button()
        # If we just unfroze and "Save on Unfreeze" is checked, save the frame
        if was_frozen and not self.camera_manager.frozen and self.save_on_unfreeze_cb.isChecked():
            self.saveFrame()

    def update_freeze_button(self):
        self.freeze_btn.setDisabled(False)
        if self.camera_manager.frozen:
            self.freeze_btn.setText("Unfreeze")
        else:
            self.freeze_btn.setText("Freeze")
        self.freeze_btn.repaint()

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

        def on_class_changed(index):
            # Find the current row for this combo box
            for r in range(self.bbox_table.rowCount()):
                if self.bbox_table.cellWidget(r, 0) is class_combo:
                    bbox_label = getattr(self, "bbox_label", None)
                    if bbox_label and r < len(bbox_label.box_colors):
                        bbox_label.box_colors[r] = index
                        bbox_label.update() 
                    break

        class_combo.currentIndexChanged.connect(on_class_changed)

        def on_delete_clicked():
            # Find the current row for this delete button
            for r in range(self.bbox_table.rowCount()):
                if self.bbox_table.cellWidget(r, 5) is delete_btn:
                    self.bbox_table.removeRow(r)
                    bbox_label = getattr(self, "bbox_label", None)
                    if bbox_label:
                        if r < len(bbox_label.boxes):
                            bbox_label.boxes.pop(r)
                        if r < len(bbox_label.box_colors):
                            bbox_label.box_colors.pop(r)
                        bbox_label.update()
                    break

        delete_btn.clicked.connect(on_delete_clicked)

    def saveFrame(self):
        print("Saving frame...")
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        imgFilename = f"{timestamp}.jpg"
        dataset_path = self.dataset_path_input.text()
        imgPath = os.path.join(dataset_path, "JPEGImages", imgFilename)
        xmlPath = os.path.join(dataset_path, "Annotations", f"{timestamp}.xml")

        # Save the captured image array as JPEG
        if hasattr(self, "captured_img_array") and self.captured_img_array is not None:
            img = self.captured_img_array
            # Convert RGB or RGBA to PIL Image
            if img.shape[2] == 3:
                pil_img = Image.fromarray(img, mode="RGB")
            elif img.shape[2] == 4:
                pil_img = Image.fromarray(img, mode="RGBA").convert("RGB")
            else:
                raise ValueError("Unsupported image format for saving.")
            pil_img.save(imgPath, "JPEG")
            print(f"Saved image to {imgPath}")

        # Create annotation XML
        root = Element("annotation")
        SubElement(root, "filename").text = imgFilename
        SubElement(root, "folder").text = os.path.basename(dataset_path)
        source = SubElement(root, "source")
        SubElement(source, "database").text = os.path.basename(dataset_path)
        SubElement(source, "annotation").text = "custom"
        SubElement(source, "image").text = "custom"
        size = SubElement(root, "size")
        # Use actual image width and height
        SubElement(size, "width").text = str(pil_img.width)
        SubElement(size, "height").text = str(pil_img.height)
        SubElement(size, "depth").text = "3"
        SubElement(root, "segmented").text = "0"

        # Add bounding boxes
        for n in range(self.bbox_table.rowCount()):
            object_elem = SubElement(root, "object")
            class_name = self.bbox_table.cellWidget(n, 0).currentText()
            SubElement(object_elem, "name").text = class_name
            SubElement(object_elem, "pose").text = "unspecified"
            SubElement(object_elem, "truncated").text = "0"
            SubElement(object_elem, "difficult").text = "0"
            bbox = SubElement(object_elem, "bndbox")
            # Get values from table
            x = int(self.bbox_table.item(n, 1).text())
            y = int(self.bbox_table.item(n, 2).text())
            width = int(self.bbox_table.item(n, 3).text())
            height = int(self.bbox_table.item(n, 4).text())
            xmin = x
            ymin = y
            xmax = x + width
            ymax = y + height
            SubElement(bbox, "xmin").text = str(xmin)
            SubElement(bbox, "ymin").text = str(ymin)
            SubElement(bbox, "xmax").text = str(xmax)
            SubElement(bbox, "ymax").text = str(ymax)

        tree = ElementTree(root)
        tree.write(xmlPath)
        print(f"Saved annotation XML to {xmlPath}")

    def select_dataset_path(self):
        super().select_dataset_path()  # Call the base class method to show dialog and save setting

        # Now create the required folders in the selected path
        dataset_path = self.dataset_path_input.text()
        for subdir in ["Annotations", "ImageSets", "JPEGImages"]:
            os.makedirs(os.path.join(dataset_path, subdir), exist_ok=True)

    def select_class_labels_file(self):
        super().select_class_labels_file()  # Call the base class method to show dialog and save setting

        # Now create the required folder in the dataset path
        dataset_path = self.dataset_path_input.text()
        imagesets_main = os.path.join(dataset_path, "ImageSets", "Main") 
        os.makedirs(imagesets_main, exist_ok=True)