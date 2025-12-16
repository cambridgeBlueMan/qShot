from components.component_base_video import ComponentBaseVideo
from qt import QtWidgets, QtCore
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import subprocess
from app_signals import app_signals

class SimpleVideo(ComponentBaseVideo):

    def __init__(self, parent=None, **kwargs):
        self.cam = kwargs.get("cam")
        self.config_model = kwargs.get("config_model")
        self.controls_model = kwargs.get("controls_model")
        self.paths_model = kwargs.get("paths_model")
        self.preview = kwargs.get("preview")
        self.resolutions_model = kwargs.get("resolutions_model")
        super().__init__(
            parent=parent,
            cam=self.cam,
            config_model=self.config_model,
            controls_model=self.controls_model,
            paths_model=self.paths_model,
            resolutions_model=self.resolutions_model,
            show_jpeg_quality=False,
            show_ae=True,
            show_resolution=True,
            show_adjustments=True,
            show_filename=True,
            show_terminal=True
        )

        self.is_recording = False
        self.flash_on = False
        self.flash_timer = QtCore.QTimer(self)
        self.flash_timer.setInterval(1000)  # 1 second
        self.flash_timer.timeout.connect(self.flash_record_button)

        # Button row
        button_row = QtWidgets.QHBoxLayout()
        self.record_button = QtWidgets.QPushButton("Record")
        button_row.addWidget(self.record_button)
        self.record_button.clicked.connect(self.toggle_recording)

        self.more_button = QtWidgets.QPushButton("more...")
        self.more_button.setCheckable(True)
        button_row.addWidget(self.more_button)
        self.more_button.toggled.connect(self.toggle_common_controls)

        self.base_layout.insertLayout(0, button_row)

        # Restore the preview signal connection
        # if self.preview:
        #     self.preview.done_signal.connect(self.record_done)

    def flash_record_button(self):
        if self.flash_on:
            self.record_button.setStyleSheet("")
            self.flash_on = False
        else:
            self.record_button.setStyleSheet("background-color: red; color: white;")
            self.flash_on = True

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        file_path = self.paths_model.full_path(kind="vid")
        self.last_video_path = file_path
        self.append_terminal(f"Recording to: {file_path}", color="#FFD700")
        if self.cam:
            encoder = H264Encoder(10000000)
            # Pass self.record_done as the signal function
            output = FfmpegOutput(file_path, audio=True, )
            self.cam.start_encoder(encoder, output)
            self.is_recording = True
            self.record_button.setText("Stop")
            self.flash_timer.start()
            self.flash_on = False
            self.record_button.setStyleSheet("")  # Ensure initial state
            app_signals.isRecordingChanged.emit(True)

    def stop_recording(self):
        self.append_terminal("Stopping video recording...", color="#FFD700")
        if self.cam:
            self.cam.stop_encoder()
        # Do NOT reset UI or output link here; let record_done handle it
        file_path = getattr(self, "last_video_path", None)
        if file_path:
            file_url = f"file://{file_path}"
            self.append_terminal(
                f'Video recording completed: <a href="{file_url}">{file_path}</a>',
                color="#A8FF60"
            )
        else:
            self.append_terminal("Video recording completed.", color="#A8FF60")
        self.is_recording = False
        self.flash_timer.stop()
        self.record_button.setStyleSheet("")
        self.record_button.setText("Record")
        self.record_button.setEnabled(True)
        app_signals.isRecordingChanged.emit(False)

    def record_done(self, job):
        file_path = getattr(self, "last_video_path", None)
        if file_path:
            file_url = f"file://{file_path}"
            self.append_terminal(
                f'Video recording completed: <a href="{file_url}">{file_path}</a>',
                color="#A8FF60"
            )
        else:
            self.append_terminal("Video recording completed.", color="#A8FF60")
        self.is_recording = False
        self.flash_timer.stop()
        self.record_button.setStyleSheet("")
        self.record_button.setText("Record")
        self.record_button.setEnabled(True)

    def handle_terminal_link(self, filepath):
        main_window = self.window()
        if hasattr(main_window, "show_video_player"):
            main_window.show_video_player(filepath)

    def handle_playing_state(self, is_playing):
        # Disable recording controls if a video is playing
        self.record_button.setEnabled(not is_playing)