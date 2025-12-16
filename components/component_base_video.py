from PyQt5 import QtCore
from components.component_base import ComponentBase
from app_signals import app_signals
class ComponentBaseVideo(ComponentBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        app_signals.isRecordingChanged.connect(self.handle_recording_state)
        app_signals.isPlayingChanged.connect(self.handle_playing_state)

    @QtCore.pyqtSlot(bool)
    def handle_recording_state(self, is_recording):
        pass  # To be overridden in subclass

    @QtCore.pyqtSlot(bool)
    def handle_playing_state(self, is_playing):
        pass  # To be overridden in subclass