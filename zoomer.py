from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc
from PyQt6 import QtGui as qtg
from viewport import Viewport
from app_signals import app_signals
from config_model import ConfigModel
from controls_model import ControlsModel
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w' 
)
SENSOR_FRAME_DIVIDER = 8

class Zoomer(qtw.QWidget):
    """A widget for controlling zoom using a DragButton."""

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.zoomsets_model = kwargs.get("zoomsets_model")
        layout = qtw.QVBoxLayout(self)

        self.cam = kwargs.get("cam")
        self.preview = kwargs.get("preview")
        self.config_model = kwargs.get("config_model")
        self.controls_model = kwargs.get("controls_model")  # <-- Add this line

        # Checkbox to enable zoom
        self.enable_zoom_checkbox = qtw.QCheckBox("Enable zoom")
        layout.addWidget(self.enable_zoom_checkbox)

        # QFrame for zoom area
        self.zoom_frame = qtw.QFrame(self)
        self.zoom_frame.setFrameShape(qtw.QFrame.Shape.Box)

        frame_width, frame_height = self._calculate_frame_size()
        self.zoom_frame.setFixedSize(frame_width, frame_height)
        frame_layout = qtw.QVBoxLayout(self.zoom_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)

        self.viewport = Viewport(self.zoom_frame)
        self.viewport.setParent(self.zoom_frame)
        self.viewport.move(0, 0)

        # Connect signals to slots
        self.viewport.scrolled.connect(self.setViewportSize)
        self.viewport.posChanged.connect(self.setViewportPos)

        # Do NOT add self.viewport to any layout!

        layout.addWidget(self.zoom_frame)

        # Add preview widget if provided
        # if self.preview is not None:
        #    layout.addWidget(self.preview)

        # Zoom sets view
        self.zoomsets_view = qtw.QTableView(self)
        self.zoomsets_view.setModel(self.zoomsets_model)
        layout.addWidget(self.zoomsets_view)

        # Add button to save current viewport as preset
        self.save_preset_button = qtw.QPushButton("Save Preset", self)
        self.save_preset_button.clicked.connect(self.save_current_viewport_as_preset)
        layout.addWidget(self.save_preset_button)

        # Add button to delete selected preset(s)
        self.delete_preset_button = qtw.QPushButton("Delete Selected Preset(s)", self)
        self.delete_preset_button.clicked.connect(self.delete_selected_presets)
        layout.addWidget(self.delete_preset_button)

        self.setLayout(layout)

        app_signals.mode_changed.connect(self.on_global_mode_changed) 
        self.config_model.configChanged.connect(self.on_config_changed)  # <-- Connect signal here

        if self.cam is not None:
            self.viewport.setCamera(self.cam)

        # Connect doubleClicked signal to save_current_viewport_as_preset slot
        self.viewport.doubleClicked.connect(self.save_current_viewport_as_preset)

    def on_global_mode_changed(self, mode):
        # Handle mode change here (update UI, internal state, etc.)
        print(f"Zoomer received global mode change: {mode}")
        # Add any logic you need for reacting to mode changes

    def on_config_changed(self, config_dict):
        """
        Slot to handle config_model configChanged signal.
        Expects the full config dictionary as payload.
        Uses the 'size' key from the 'main' dictionary and scales it.
        """
        main_dict = config_dict.get('main', {})
        size_tuple = main_dict.get('size', None)
        logging.info(f"Zoomer: config_changed received main.size = {size_tuple}")
        if size_tuple is not None and isinstance(size_tuple, (tuple, list)) and len(size_tuple) == 2:
            viewport_width, viewport_height = self._calculate_frame_size(size_tuple)
            self.viewport.setSize(viewport_width, viewport_height)

    def eventFilter(self, obj, event):
        if event.type() == qtc.QEvent.Type.Close:
            self.zoomer.close()
        return super().eventFilter(obj, event)

    def setViewportSize(self, delta):
        """
        Adjust the viewport (DragButton) size in response to mouse wheel events,
        using logic similar to zoomTab.
        """
        # Get current size and position
        old_width = self.viewport.bWidth
        old_height = self.viewport.bHeight
        old_x = self.viewport.x()
        old_y = self.viewport.y()

        # Scale factor: zoom in/out by 10% per wheel step
        scale = 1.1 if delta > 0 else 0.9

        # Calculate new size
        new_width = int(old_width * scale)
        new_height = int(old_height * scale)

        # Clamp to minimum and maximum, preserving aspect ratio
        min_size = 10
        max_width = self.zoom_frame.width()
        max_height = self.zoom_frame.height()

        # Compute scale factors for width and height
        scale_w = max_width / new_width if new_width > max_width else 1.0
        scale_h = max_height / new_height if new_height > max_height else 1.0
        overall_scale = min(scale_w, scale_h, 1.0)

        # Apply the overall scale to both dimensions
        new_width = max(min_size, int(new_width * overall_scale))
        new_height = max(min_size, int(new_height * overall_scale))

        # Center the viewport on its old center
        center_x = old_x + old_width // 2
        center_y = old_y + old_height // 2
        new_x = max(0, min(center_x - new_width // 2, max_width - new_width))
        new_y = max(0, min(center_y - new_height // 2, max_height - new_height))

        # Apply new size and position
        self.viewport.setGeometry(new_x, new_y, new_width, new_height)
        self.viewport.setSize(new_width, new_height)

        # Pass new ScalerCrop to controls_model
        if self.controls_model is not None:
            scaler_crop = self._get_scaler_crop()
            if scaler_crop:
                self.controls_model.ScalerCrop = scaler_crop
                logging.info(f"Zoomer: set ScalerCrop to {scaler_crop}")

    def setViewportPos(self, x, y):
        """
        Slot to handle viewport position changes.
        """
        # Pass new ScalerCrop to controls_model
        if self.controls_model is not None:
            scaler_crop = self._get_scaler_crop()
            if scaler_crop:
                self.controls_model.ScalerCrop = scaler_crop
                logging.info(f"Zoomer: set ScalerCrop to {scaler_crop}")

    def _calculate_frame_size(self, size_tuple=None):
        """
        Calculate the zoom frame or viewport size based on a given size_tuple
        (e.g., output_size from config), or fall back to camera PixelArraySize.
        Uses SENSOR_FRAME_DIVIDER to scale the size.
        """
        if size_tuple is not None:
            sensor_width, sensor_height = size_tuple
        elif (
            self.cam is not None and
            hasattr(self.cam, "camera_properties") and
            isinstance(self.cam.camera_properties, dict) and
            "PixelArraySize" in self.cam.camera_properties
        ):
            sensor_width, sensor_height = self.cam.camera_properties["PixelArraySize"]
        else:
            # Fallback to a default size if nothing is available
            return 640 // SENSOR_FRAME_DIVIDER, 480 // SENSOR_FRAME_DIVIDER

        frame_width = max(1, sensor_width // SENSOR_FRAME_DIVIDER)
        frame_height = max(1, sensor_height // SENSOR_FRAME_DIVIDER)
        return frame_width, frame_height

    def _get_scaler_crop(self):
        """
        Calculate the ScalerCrop rectangle (x, y, w, h) in sensor coordinates
        based on the viewport's position and size.
        """
        if (
            self.cam is not None and
            hasattr(self.cam, "camera_properties") and
            isinstance(self.cam.camera_properties, dict) and
            "PixelArraySize" in self.cam.camera_properties
        ):
            sensor_width, sensor_height = self.cam.camera_properties["PixelArraySize"]
        else:
            return None

        # Map viewport position/size to sensor coordinates
        x = self.viewport.x() * SENSOR_FRAME_DIVIDER
        y = self.viewport.y() * SENSOR_FRAME_DIVIDER
        w = self.viewport.bWidth * SENSOR_FRAME_DIVIDER
        h = self.viewport.bHeight * SENSOR_FRAME_DIVIDER

        # Clamp to sensor bounds
        x = max(0, min(x, sensor_width - w))
        y = max(0, min(y, sensor_height - h))
        return (x, y, w, h)

    def save_current_viewport_as_preset(self):
        """
        Save the current viewport position and size as a new preset in the zoomsets model.
        """
        x = self.viewport.x()
        y = self.viewport.y()
        w = self.viewport.bWidth
        h = self.viewport.bHeight
        speed = 1  # Default or get from UI if available
        pause = 1.0  # Default or get from UI if available
        zdata = [x, y, w, h, speed, pause]
        if self.zoomsets_model is not None:
            self.zoomsets_model.insertRows(self.zoomsets_model.rowCount(), 1, zdata=zdata)

    def delete_selected_presets(self):
        """
        Delete the selected rows from the zoomsets table.
        """
        selection = self.zoomsets_view.selectionModel().selectedRows()
        # Remove from bottom up to avoid row index shifting
        for index in sorted(selection, key=lambda x: x.row(), reverse=True):
            self.zoomsets_model.removeRows(index.row(), 1)

if __name__ == "__main__":
    import sys
    from picamera2 import Picamera2
    from picamera2.previews.qt import QGl6Picamera2 as QGlPicamera2

    app = qtw.QApplication(sys.argv)
    camera = Picamera2()
    preview = QGlPicamera2(camera)
    camera.start()
    # Use a real preview configuration for the config model
    config_model = ConfigModel(initial_config=camera.create_preview_configuration())
    config_model.set_nested('main', 'size', (320, 240))
    main_size = config_model.get_nested('main', 'size')
    print(f"Test: config_model['main']['size'] = {main_size}")

    zoomer = Zoomer(cam=camera, config_model=config_model)

    # Create a container widget and layout
    container = qtw.QWidget()
    layout = qtw.QHBoxLayout(container)
    layout.addWidget(zoomer)
    layout.addWidget(preview)
    container.setWindowTitle("Zoomer & Preview")
    container.resize(1100, 400)
    container.show()

    sys.exit(app.exec())