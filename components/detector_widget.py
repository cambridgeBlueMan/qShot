from qt import QtWidgets, QtGui, QtCore, Qt
from components.base_camera_manager import BaseCameraManager
from ai_file_manager_base import AIFileManager
"""
Detector Widget Module
----------------------

This module implements the Detector widget for an AI annotation/capture application using PyQt6.
It provides a GUI for capturing images from a camera, drawing bounding boxes, managing class labels,
and saving both images and annotation data (in Pascal VOC XML format).

Classes and Responsibilities:
----------------------------

- Detector: The main widget for annotation, file management, and UI.
    - Manages dataset paths, class labels, and annotation table.
    - Integrates CameraManager for image capture and annotation.
    - Handles saving images and annotations in Pascal VOC format.
    - Provides UI for freezing/unfreezing camera, saving, and managing bounding boxes.
    - Instantiates CameraManager and passes itself for callback.
    - Receives bounding box data from BBoxLabel via CameraManager.
    - Updates annotation table and manages annotation data.

- CameraManager: Handles camera controls, image capture, and preview.
    - Receives camera and configuration objects.
    - Provides UI for selecting camera mode.
    - Handles freezing/unfreezing the camera preview.
    - On freeze, captures an image, displays it in a BBoxLabel, and enables annotation.
    - On unfreeze, restores the live preview.
    - Connects bounding box completion to the Detector widget for annotation management.
    - Instantiated and managed by the Detector widget.
    - Communicates with Detector to update annotation data.

- BBoxLabel: A QtWidgets.QLabel subclass for drawing and storing bounding boxes on images.
    - Handles mouse events to let the user draw bounding boxes.
    - Scales boxes correctly when the widget is resized.
    - Stores all boxes and their associated class indices.
    - Emits box_completed signal when a new box is drawn.
    - Used by CameraManager to display and annotate captured images.
    - Connected to the Detector widget to add new bounding box rows to the annotation table.

- SaveChangesDialog: A dialog to confirm saving changes before leaving a frozen image.
    - Simple dialog with "Yes" and "No" buttons.
    - Used to prompt the user to save changes before discarding or switching images.

Class Interactions and Workflow:
-------------------------------

1. Initialization
   - Detector is created, receiving camera/config objects.
   - Detector creates a CameraManager and passes itself as file_manager.
   - CameraManager sets up camera controls and mode selection.

2. Image Capture and Annotation
   - User clicks "Freeze" in Detector, which calls CameraManager.toggle_freeze().
   - CameraManager captures an image, displays it in a BBoxLabel.
   - User draws bounding boxes on the image; BBoxLabel emits box_completed.
   - Detector.add_bbox_row() is called to add the new box to the annotation table.

3. Annotation Management
   - User can edit class labels, delete boxes, or add more boxes.
   - Table rows are kept in sync with the bounding boxes in BBoxLabel.

4. Saving
   - User clicks "Save" to write the image and annotation XML to disk.
   - Detector.saveFrame() saves the image and generates Pascal VOC XML with all bounding boxes.

5. Cleanup
   - On unfreeze or navigation, SaveChangesDialog may prompt the user to save changes.

Summary Table
-------------

| Class         | Role/Responsibility                                   | Interacts With         |
|---------------|------------------------------------------------------|------------------------|
| Detector      | Main annotation widget, manages UI and saving         | CameraManager, BBoxLabel |
| CameraManager | Camera controls, image capture, annotation preview    | Detector, BBoxLabel    |
| BBoxLabel     | Drawing/storing bounding boxes, emits box_completed   | CameraManager, Detector|
| SaveChangesDialog | Prompt user to save changes                       | Detector               |

"""

import logging
import os
from ai_file_manager_base import AIFileManager
import importlib.util
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree
from PIL import Image
import random

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)

def generate_color(class_index, alpha=180):
    """
    Generate a unique color for a given class index.
    Returns (r, g, b, a) tuple.
    """
    random.seed(class_index)
    r = random.randint(50, 255)
    g = random.randint(50, 255)
    b = random.randint(50, 255)
    return (r, g, b, alpha)

class BBoxLabel(QtWidgets.QLabel):
    """
    QtWidgets.QLabel subclass for drawing bounding boxes on an image.
    Stores boxes in original image coordinates so they persist and scale on resize.

    Responsibilities:
    - Handles mouse events for drawing bounding boxes.
    - Stores boxes in original image coordinates.
    - Emits a signal when a box is completed.

    Interactions:
    - Used by CameraManager to display and annotate captured images.
    - Connected to Detector to add new bounding box rows to the annotation table.
    """
    box_completed = QtCore.pyqtSignal(int, int, int, int, int)  # x, y, w, h, class_index

    def __init__(self, pixmap=None, parent=None):
        super().__init__(parent)
        if pixmap is not None:
            self.setPixmap(pixmap)
        self.boxes = []  # List of QtCore.QRect in original image coordinates
        self.box_colors = []  # List of class indices for each box
        self.start = None  # In widget coords while drawing
        self.end = None    # In widget coords while drawing
        self.drawing = False
        self.annotation_enabled = True
        self._original_pixmap_size = None

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        if pixmap:
            super().setPixmap(
                pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        else:
            super().setPixmap(pixmap)
        self._original_pixmap_size = pixmap.size() if pixmap else None
        self.update()

    def enable_annotation(self, enabled=True):
        self.annotation_enabled = enabled

    def _to_image_coords(self, point):
        """Convert widget coordinates to original image coordinates."""
        if not self._original_pixmap_size:
            return point
        label_rect = self.rect()
        scale_x = self._original_pixmap_size.width() / label_rect.width()
        scale_y = self._original_pixmap_size.height() / label_rect.height()
        return QtCore.QPoint(int(point.x() * scale_x), int(point.y() * scale_y))

    def _to_widget_coords(self, point):
        """Convert original image coordinates to widget coordinates."""
        if not self._original_pixmap_size:
            return point
        label_rect = self.rect()
        scale_x = label_rect.width() / self._original_pixmap_size.width()
        scale_y = label_rect.height() / self._original_pixmap_size.height()
        return QtCore.QPoint(int(point.x() * scale_x), int(point.y() * scale_y))

    def mousePressEvent(self, event):
        if self.annotation_enabled and event.button() == Qt.MouseButton.LeftButton:
            self.start = event.pos()
            self.end = self.start
            self.drawing = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.annotation_enabled and self.drawing:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.annotation_enabled and event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.end = event.pos()
            # Store box in original image coordinates
            p1 = self._to_image_coords(self.start)
            p2 = self._to_image_coords(self.end)
            rect = QtCore.QRect(p1, p2).normalized()
            self.boxes.append(rect)
            class_index = 0
            self.box_colors.append(class_index)
            self.drawing = False
            self.start = None
            self.end = None
            self.update()
            x, y, w, h = rect.getRect()
            self.box_completed.emit(x, y, w, h, class_index)

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.pixmap() or not self._original_pixmap_size:
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        for i, rect in enumerate(self.boxes):
            p1 = self._to_widget_coords(rect.topLeft())
            p2 = self._to_widget_coords(rect.bottomRight())
            scaled_rect = QtCore.QRect(p1, p2)
            class_index = self.box_colors[i] if i < len(self.box_colors) else 0
            r, g, b, a = generate_color(class_index)
            color = QtGui.QColor(r, g, b, a)
            painter.setPen(QtGui.QPen(color, 2, Qt.PenStyle.SolidLine))
            painter.drawRect(scaled_rect)

        # Draw current box, scaled
        if self.drawing and self.start and self.end:
            painter.setPen(QtGui.QPen(Qt.GlobalColor.green, 2, Qt.PenStyle.DashLine))
            # Convert current start/end to image coords, then back to widget coords for scaling
            p1_img = self._to_image_coords(self.start)
            p2_img = self._to_image_coords(self.end)
            p1 = self._to_widget_coords(p1_img)
            p2 = self._to_widget_coords(p2_img)
            rect = QtCore.QRect(p1, p2).normalized()
            painter.drawRect(rect)

    def get_bboxes(self):
        """Return bounding boxes as (x, y, w, h) in original image coordinates."""
        return [rect.getRect() for rect in self.boxes]

    def resizeEvent(self, event):
        if hasattr(self, "_pixmap") and self._pixmap:
            super().setPixmap(
                self._pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        super().resizeEvent(event)
        
class SaveChangesDialog(QtWidgets.QDialog):
    """
    Dialog to confirm saving changes when leaving a frozen image.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save Changes?")
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("You have a frozen image. Save changes before leaving?"))
        btn_yes = QtWidgets.QPushButton("Yes")
        btn_no = QtWidgets.QPushButton("No")
        btn_yes.clicked.connect(lambda: self.done(1))
        btn_no.clicked.connect(lambda: self.done(0))
        layout.addWidget(btn_yes)
        layout.addWidget(btn_no)
        self.setLayout(layout)

class CameraManager(BaseCameraManager):
    """
    CameraManager widget for Detector, extends BaseCameraManager with freeze/annotation logic (mode selector removed).

    Responsibilities:
    - Allows freezing (capturing) the current camera image.
    - Displays the captured image using BBoxLabel for annotation.
    - Handles restoring the live preview.

    Interactions:
    - Instantiated by Detector.
    - Communicates with Detector to update annotation data.
    - Uses BBoxLabel for drawing and storing bounding boxes.
    """

    def __init__(self, file_manager=None, parent=None, **kwargs):
        super().__init__(
            cam=kwargs.get("cam"),
            preview=kwargs.get("preview"),
            config_model=kwargs.get("config_model"),
            controls_model=kwargs.get("controls_model"),
            settings_group=kwargs.get("settings_group"),
            parent=parent
        )
        self.file_manager = file_manager
        self.frozen = False  # Track freeze state
        # No mode selector UI

    def freeze_image(self):
        logging.info("Freeze button pressed.")
        if self.preview and hasattr(self.preview, "done_signal"):
            try:
                self.preview.done_signal.disconnect(self._capture_done)
            except Exception:
                pass
            self.preview.done_signal.connect(self._capture_done)
        self._current_job = self.cam.capture_image(signal_function=self.preview.signal_done)
        logging.info("Async image capture started (capture_image).")
        self.frozen = True

    def _capture_done(self, job):
        logging.info("Image capture completed (async, PIL image).")
        try:

            pil_img = self.cam.wait(job)
            # from PyQt6.QtGui import QImage, QPixmap
            logging.info(f"pil_img type: {type(pil_img)} size: {getattr(pil_img, 'size', None)} mode: {getattr(pil_img, 'mode', None)}")
            if pil_img is not None:
                # Convert unsupported modes to RGB
                if pil_img.mode == "RGB":
                    img_for_qt = pil_img
                elif pil_img.mode == "RGBA":
                    img_for_qt = pil_img
                elif pil_img.mode == "RGBX":
                    logging.info("Converting RGBX to RGB for display.")
                    img_for_qt = pil_img.convert("RGB")
                else:
                    raise ValueError(f"Unsupported PIL image mode for display: {pil_img.mode}")

                img_data = img_for_qt.tobytes()
                width, height = img_for_qt.size
                if img_for_qt.mode == "RGB":
                    qimg = QtGui.QImage(img_data, width, height, QtGui.QImage.Format.Format_RGB888)
                elif img_for_qt.mode == "RGBA":
                    qimg = QtGui.QImage(img_data, width, height, QtGui.QImage.Format.Format_RGBA8888)

                pixmap = QtGui.QPixmap.fromImage(qimg)
                logging.info(f"Created pixmap: {pixmap.size()}, isNull: {pixmap.isNull()}")

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
                    detector_widget.captured_img_array = pil_img  # Store for later saving
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
                logging.error("Failed to capture image: pil_img is None.")

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

    def toggle_freeze(self):
        if not self.frozen:
            self.freeze_image()
        else:
            self.restore_preview()
        main_window = self.window()
        if hasattr(main_window, "detector_widget"):
            main_window.detector_widget.update_freeze_button()
        elif hasattr(main_window, "parent") and hasattr(main_window.parent(), "update_freeze_button"):
            main_window.parent().update_freeze_button()

    def cleanup(self):
        if self.frozen:
            dlg = SaveChangesDialog(self)
            dlg.exec_()
            self.restore_preview()

    def get_bbox_label(self):
        return getattr(self, "bbox_label", None)

class Detector(AIFileManager):
    """
    Detector widget for annotation. Inherits file management UI from AIFileManager.

    Responsibilities:
    - Manages dataset paths, class labels, and annotation table.
    - Integrates CameraManager for image capture and annotation.
    - Handles saving images and annotations in Pascal VOC format.
    - Provides UI for freezing/unfreezing camera, saving, and managing bounding boxes.

    Interactions:
    - Instantiates CameraManager and passes itself for callback.
    - Receives bounding box data from BBoxLabel via CameraManager.
    - Updates annotation table and manages annotation data.
    """

    def __init__(self, parent=None, **kwargs):
        logging.info(f"Loading Detector component with settings_group={kwargs.get('settings_group')}")
        super().__init__(parent, settings_group=kwargs.get("settings_group"))

        self.cam = kwargs.get("cam")
        self.csi = kwargs.get("csi", 0)
        self.modes = self.cam.sensor_modes
        self.preview = kwargs.get("preview")
        self.config_model = kwargs.get("config_model")
        self.controls_model = kwargs.get("controls_model")
        self.settings_group = kwargs.get("settings_group")

        # --- CameraManager ---
        self.camera_manager = CameraManager(
            file_manager=self, **kwargs
        )
        self.base_layout.addWidget(self.camera_manager)

        # --- Table Widget for bounding boxes ---
        self.bbox_table = QtWidgets.QTableWidget(0, 6)
        self.bbox_table.setHorizontalHeaderLabels(["Class", "X", "Y", "Width", "Height", "Delete"])
        self.bbox_table.verticalHeader().setVisible(False)
        self.bbox_table.setEditTriggers(QtWidgets.QTableWidget.EditTrigger.NoEditTriggers)
        self.bbox_table.setSelectionBehavior(QtWidgets.QTableWidget.SelectionBehavior.SelectRows)
        self.bbox_table.setSelectionMode(QtWidgets.QTableWidget.SelectionMode.SingleSelection)
        self.bbox_table.setMinimumHeight(150)
        header = self.bbox_table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.base_layout.addWidget(self.bbox_table)

        # --- Checkboxes row ---
        checkbox_layout = QtWidgets.QHBoxLayout()
        self.save_on_unfreeze_cb = QtWidgets.QCheckBox("Save on Unfreeze")
        self.save_on_unfreeze_cb.setChecked(True)  # Default to True
        self.clear_on_unfreeze_cb = QtWidgets.QCheckBox("Clear on Unfreeze")
        self.clear_on_unfreeze_cb.setChecked(True)  # Default to True
        self.merge_sets_cb = QtWidgets.QCheckBox("Merge Sets")
        checkbox_layout.addWidget(self.save_on_unfreeze_cb)
        checkbox_layout.addWidget(self.clear_on_unfreeze_cb)
        checkbox_layout.addWidget(self.merge_sets_cb)
        self.base_layout.addLayout(checkbox_layout)

        # --- Freeze/Unfreeze and Save Buttons row ---
        button_row = QtWidgets.QHBoxLayout()
        self.freeze_btn = QtWidgets.QPushButton("Freeze")
        self.freeze_btn.setToolTip("Freeze the current camera image or return to live preview")
        self.freeze_btn.clicked.connect(self.handle_freeze_clicked)
        button_row.addWidget(self.freeze_btn)

        self.save_btn = QtWidgets.QPushButton(QtGui.QIcon("save.png"), "Save")
        self.save_btn.setToolTip("Save current bounding boxes or annotations")
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
        was_frozen = self.camera_manager.frozen
        self.camera_manager.toggle_freeze()
        # Now update the button label based on the new state
        self.update_freeze_button()
        # If we just unfroze and "Save on Unfreeze" is checked, save the frame
        if was_frozen and not self.camera_manager.frozen and self.save_on_unfreeze_cb.isChecked():
            self.saveFrame()

    def update_freeze_button(self):
        if self.camera_manager.frozen:
            self.freeze_btn.setText("Unfreeze")
        else:
            self.freeze_btn.setText("Freeze")

    def add_bbox_row(self, class_name=None, x=0, y=0, width=0, height=0):
        class_labels = self.load_class_labels()
        row = self.bbox_table.rowCount()
        self.bbox_table.insertRow(row)
        class_combo = QtWidgets.QComboBox()
        if class_labels:
            class_combo.addItems(class_labels)
        else:
            class_combo.addItem("No labels found")
        if class_name and class_name in class_labels:
            class_combo.setCurrentText(class_name)
        self.bbox_table.setCellWidget(row, 0, class_combo)
        self.bbox_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(x)))
        self.bbox_table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(y)))
        self.bbox_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(width)))
        self.bbox_table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(height)))
        delete_btn = QtWidgets.QPushButton("Delete")
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

        # Save the captured image (PIL Image) as JPEG
        if hasattr(self, "captured_img_array") and self.captured_img_array is not None:
            pil_img = self.captured_img_array
            # Convert to RGB if needed
            if pil_img.mode not in ["RGB", "RGBA"]:
                pil_img = pil_img.convert("RGB")
            elif pil_img.mode == "RGBA":
                pil_img = pil_img.convert("RGB")
            # Get JPEG quality from controls_model if available, else use 80
            quality = 80
            if hasattr(self, 'controls_model') and self.controls_model is not None:
                quality = getattr(self.controls_model, 'JpegQuality', 80)
                if not isinstance(quality, int):
                    try:
                        quality = int(quality)
                    except Exception:
                        quality = 80
            pil_img.save(imgPath, "JPEG", quality=quality)
            print(f"Saved image to {imgPath} with quality={quality}")

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