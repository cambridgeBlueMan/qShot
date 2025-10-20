from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc
from PyQt6 import QtGui as qtg
from viewport import Viewport
from app_signals import app_signals
from config_model import ConfigModel
from controls_model import ControlsModel
from player import Player
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w' 
)
SENSOR_FRAME_DIVIDER = 8

def apply_scaler_crop_from_player(controls_model, cam=None):
    """
    Adapter for Player: receives interpolated state dict with keys x,y,w,h
    and applies as ScalerCrop via controls_model or directly to cam.
    """
    def apply_fn(state):
        try:
            crop = (int(state.get('x', 0)), int(state.get('y', 0)),
                    int(state.get('w', 0)), int(state.get('h', 0)))
            if controls_model is not None:
                controls_model.ScalerCrop = crop
            elif cam is not None:
                try:
                    cam.set_controls({"ScalerCrop": list(crop)})
                except Exception:
                    logging.exception("Failed to set controls on cam")
        except Exception:
            logging.exception("apply_fn failed")
    return apply_fn

class Zoomer(qtw.QWidget):
    """
    Zoomer: Main UI/controller for managing camera zoom presets and playback.

    Responsibilities:
    - Hosts the draggable Viewport widget for interactive zoom region selection.
    - Displays and manages a table of zoom presets (sensor coordinates, duration, pause).
    - Provides Add/Delete buttons for preset management.
    - Provides UI controls to select start/end rows and play back interpolated zoom transitions using Player.
    - Connects Player's `state` signal to main-thread slots that update ControlsModel or camera controls.
    - Handles all camera/control writes on the main (GUI) thread for thread safety.
    - Keeps UI elements (spinboxes, table) in sync with the underlying model.

    Key Interactions:
    - User drags or resizes the Viewport: emits posChanged/scrolled, updates ControlsModel.ScalerCrop.
    - Double-click or Add button: saves current viewport as a new preset (in sensor coordinates).
    - Delete button: removes selected preset(s) from the table.
    - Play: interpolates between selected start/end presets over the specified duration using Player.
    - Stop: halts playback and re-enables UI controls.

    Signals/Slots:
    - Connects to app_signals and config_model for global mode/config changes.
    - Connects Player's state/progress/finished/stopped signals for real-time feedback and control.

    Threading:
    - All camera/control updates are performed on the main thread.
    - Player runs in a background thread and emits state for main-thread application.

    Extensibility:
    - Designed to support additional "players" for other camera controls.
    - Can be extended to support multiple concurrent control streams.

    """
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

        layout.addWidget(self.zoom_frame)

        # Create the viewport widget inside the zoom_frame
        self.viewport = Viewport(self.zoom_frame)
        self.viewport.setParent(self.zoom_frame)
        self.viewport.move(0, 0)

        # Add preview widget if provided
        # if self.preview is not None:
        #    layout.addWidget(self.preview)

        # Zoom sets view
        self.zoomsets_view = qtw.QTableView(self)
        self.zoomsets_view.setModel(self.zoomsets_model)
        # select entire rows on click, single selection only
        self.zoomsets_view.setSelectionBehavior(qtw.QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.zoomsets_view)

        # Add buttons row: Add (save) and Delete
        btn_row = qtw.QHBoxLayout()

        self.add_button = qtw.QPushButton("Add", self)
        self.add_button.setToolTip("Save the current viewport position and size as a new preset.")
        self.add_button.clicked.connect(self.save_current_viewport_as_preset)
        btn_row.addWidget(self.add_button)

        self.delete_button = qtw.QPushButton("Delete", self)
        self.delete_button.setToolTip("Delete the currently selected preset(s) from the presets table.")
        self.delete_button.clicked.connect(self.delete_selected_presets)
        btn_row.addWidget(self.delete_button)

        layout.addLayout(btn_row)
        # Player controls row: start/end row selectors and Play/Stop
        if self.zoomsets_model is not None:
            player_row = qtw.QHBoxLayout()

            self.start_label = qtw.QLabel("Start row:", self)
            player_row.addWidget(self.start_label)
            self.start_spin = qtw.QSpinBox(self)
            self.start_spin.setMinimum(1)
            self.start_spin.setMaximum(max(1, self.zoomsets_model.rowCount()))
            player_row.addWidget(self.start_spin)

            self.end_label = qtw.QLabel("End row:", self)
            player_row.addWidget(self.end_label)
            self.end_spin = qtw.QSpinBox(self)
            self.end_spin.setMinimum(1)
            self.end_spin.setMaximum(max(1, self.zoomsets_model.rowCount()))
            player_row.addWidget(self.end_spin)

            self.play_button = qtw.QPushButton("Play", self)
            self.play_button.setToolTip("Interpolate controls from Start row to End row using the duration value.")
            self.play_button.clicked.connect(self._on_play_clicked)
            player_row.addWidget(self.play_button)

            self.stop_button = qtw.QPushButton("Stop", self)
            self.stop_button.setToolTip("Stop the running player.")
            self.stop_button.clicked.connect(self._on_stop_clicked)
            self.stop_button.setEnabled(False)
            player_row.addWidget(self.stop_button)

            layout.addLayout(player_row)

            # Keep spin ranges in sync with model changes
            try:
                self.zoomsets_model.rowsInserted.connect(self._update_row_spin_ranges)
                self.zoomsets_model.rowsRemoved.connect(self._update_row_spin_ranges)
                self.zoomsets_model.modelReset.connect(self._update_row_spin_ranges)
            except Exception:
                pass

        self.setLayout(layout)

        app_signals.mode_changed.connect(self.on_global_mode_changed) 
        self.config_model.configChanged.connect(self.on_config_changed)  # <-- Connect signal here

        if self.cam is not None:
            self.viewport.setCamera(self.cam)

        # Connect doubleClicked signal to save_current_viewport_as_preset slot
        self.viewport.doubleClicked.connect(self.save_current_viewport_as_preset)

        # Connect viewport signals to slots
        self.viewport.scrolled.connect(self.setViewportSize)
        self.viewport.posChanged.connect(self.setViewportPos)

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

    def setViewportPos(self, x, y):
        """
        Slot to handle viewport position changes.
        """
        # When moving, clamp so the viewport stays inside the frame
        max_x = self.zoom_frame.width() - self.viewport.bWidth
        max_y = self.zoom_frame.height() - self.viewport.bHeight
        x = max(0, min(x, max_x))
        y = max(0, min(y, max_y))
        self.viewport.move(x, y)

        # Pass new ScalerCrop to controls_model
        if self.controls_model is not None:
            scaler_crop = self._get_scaler_crop()
            if scaler_crop:
                self.controls_model.ScalerCrop = scaler_crop

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
            frame_width = 640 // SENSOR_FRAME_DIVIDER
            frame_height = 480 // SENSOR_FRAME_DIVIDER
            return frame_width, frame_height

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
        Save the current viewport as a preset in SENSOR coordinates.
        Store as [x, y, w, h, duration (s), pause (s)] where duration is a float.
        """
        # Prefer canonical mapping to sensor coordinates
        scaler_crop = self._get_scaler_crop()

        if scaler_crop is None:
            # Fallback: map widget coords -> sensor coords using SENSOR_FRAME_DIVIDER
            x = self.viewport.x() * SENSOR_FRAME_DIVIDER
            y = self.viewport.y() * SENSOR_FRAME_DIVIDER
            w = self.viewport.bWidth * SENSOR_FRAME_DIVIDER
            h = self.viewport.bHeight * SENSOR_FRAME_DIVIDER
            scaler_crop = (int(x), int(y), int(w), int(h))
        else:
            scaler_crop = tuple(int(v) for v in scaler_crop)

        # defaults: duration in seconds (float) and pause in seconds (float)
        duration = 3.0
        pause = 1.0

        zdata = [scaler_crop[0], scaler_crop[1], scaler_crop[2], scaler_crop[3], float(duration), float(pause)]

        if self.zoomsets_model is not None:
            self.zoomsets_model.insertRows(self.zoomsets_model.rowCount(), 1, zdata=zdata)
            # keep spinners up to date
            self._update_row_spin_ranges()

    def delete_selected_presets(self):
        """
        Delete the selected rows from the zoomsets table.
        """
        selection = self.zoomsets_view.selectionModel().selectedRows()
        # Remove from bottom up to avoid row index shifting
        for index in sorted(selection, key=lambda x: x.row(), reverse=True):
            self.zoomsets_model.removeRows(index.row(), 1)

    def play_range(self, start_row, end_row):
        if self.zoomsets_model is None:
            return
        apply_fn = apply_scaler_crop_from_player(self.controls_model, cam=self.cam)
        self.player = Player(self.zoomsets_model, apply_fn, start_row, end_row, steps_per_second=30)
        # self.player.progress.connect(lambda p: logging.info(f"Player progress: {p:.2f}"))
        self.player.finished.connect(lambda: logging.info("Player finished"))
        self.player.stopped.connect(lambda: logging.info("Player stopped"))
        # update UI when player finishes / is stopped
        self.player.finished.connect(self._on_player_done)
        self.player.stopped.connect(self._on_player_done)
        self.play_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.player.start()

    def _on_play_clicked(self):
        if self.zoomsets_model is None:
            return
        # Adjust for 1-based UI to 0-based model indices
        start = int(self.start_spin.value()) - 1
        end = int(self.end_spin.value()) - 1
        if start > end:
            start, end = end, start
        self.play_range(start, end)

    def _on_stop_clicked(self):
        if hasattr(self, "player") and self.player is not None:
            try:
                self.player.stop()
            except Exception:
                logging.exception("Failed to stop player")

    def _on_player_done(self):
        # Called when player finishes or is stopped
        try:
            self.play_button.setEnabled(True)
            self.stop_button.setEnabled(False)
        except Exception:
            pass

    def _update_row_spin_ranges(self, *args, **kwargs):
        """
        Keep start/end spinboxes in sync with the current zoomsets_model row count.
        """
        if self.zoomsets_model is None:
            return
        max_row = max(1, self.zoomsets_model.rowCount())
        # preserve current values where possible, clamp to valid range
        s = min(self.start_spin.value() if hasattr(self, "start_spin") else 1, max_row)
        e = min(self.end_spin.value() if hasattr(self, "end_spin") else 1, max_row)
        self.start_spin.setMinimum(1)
        self.end_spin.setMinimum(1)
        self.start_spin.setMaximum(max_row)
        self.end_spin.setMaximum(max_row)
        self.start_spin.setValue(s)
        self.end_spin.setValue(e)