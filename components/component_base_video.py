from PyQt5 import QtCore, QtWidgets
from components.component_base import ComponentBase
from app_signals import app_signals
import logging

logger = logging.getLogger(__name__)

AVAILABLE_FPS = [10, 20, 24, 25, 30, 50, 60, 120]

class ComponentBaseVideo(ComponentBase):
    CAPTURE_TYPE = "vid"  # Override for video capture

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        app_signals.isRecordingChanged.connect(self.handle_recording_state)
        app_signals.isPlayingChanged.connect(self.handle_playing_state)

        # --- Video mode selection logic ---
        self.video_mode = self.select_video_mode(min_fps=30)
        logger.info(f"video_mode: {self.video_mode}")
        if self.video_mode:
            if self.config_model:
                self.config_model.set_nested('sensor', 'output_size', self.video_mode['size'])
                self.config_model.set_nested('sensor', 'bit_depth', self.video_mode.get('bit_depth', 8))
            if self.controls_model:
                frame_duration = int(1_000_000 / self.video_mode['fps'])
                self.controls_model.FrameDurationLimits = (frame_duration, frame_duration)
            if hasattr(self, "res_combo"):
                self.res_combo.generateComboItems(self.video_mode)
                self.res_combo.set_largest_resolution()

        if self.fps_combo is not None and self.video_mode and 'fps' in self.video_mode:
            max_mode_fps = float(self.video_mode['fps'])
            fps_options = [fps for fps in AVAILABLE_FPS if fps <= max_mode_fps]
            for fps in fps_options:
                self.fps_combo.addItem(f"{fps} fps", userData=fps)
            self.fps_combo.currentIndexChanged.connect(self.set_fps_in_controls)
        else:
            logger.warning(f"FPS combo not populated: fps_combo={self.fps_combo}, video_mode={self.video_mode}")
        # logger.info(f"fps_combo exists: {hasattr(self, 'fps_combo')}, video_mode: {self.video_mode}")
        # logger.info(f"Type of fps_combo: {type(self.fps_combo)}")
        # logger.info(f"fps_combo is None: {self.fps_combo is None}")
        # logger.info(f"video_mode: {self.video_mode}")
        # logger.info(f"AVAILABLE_FPS: {AVAILABLE_FPS}")

    def select_video_mode(self, min_fps=30):
        if hasattr(self, "cam") and hasattr(self.cam, "sensor_modes") and self.cam.sensor_modes:
            suitable_modes = [m for m in self.cam.sensor_modes if m.get('fps', 0) >= min_fps]
            if suitable_modes:
                # Pick the one with the highest resolution
                best_mode = max(suitable_modes, key=lambda m: m['size'][0] * m['size'][1])
                return best_mode  # Return the mode dictionary
            else:
                # Fallback: pick the highest fps available
                best_mode = max(self.cam.sensor_modes, key=lambda m: m.get('fps', 0))
                return best_mode
        return None

    def set_fps_in_controls(self, index):
        fps = self.fps_combo.itemData(index)
        if self.controls_model and fps:
            frame_duration = int(1_000_000 / fps)
            self.controls_model.FrameDurationLimits = (frame_duration, frame_duration)

    @QtCore.pyqtSlot(bool)
    def handle_recording_state(self, is_recording):
        pass  # To be overridden in subclass

    @QtCore.pyqtSlot(bool)
    def handle_playing_state(self, is_playing):
        pass  # To be overridden in subclass