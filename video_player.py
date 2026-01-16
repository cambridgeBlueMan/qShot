import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import vlc
from app_signals import app_signals


class VideoPlayer(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()
        # Focus to receive shortcuts
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # Layout for the player and the control buttons
        layout = QtWidgets.QVBoxLayout(self)

        # Video frame
        self.video_frame = QtWidgets.QFrame(self)
        layout.addWidget(self.video_frame, stretch=1)

        # Position slider
        self.position_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 1000)
        self.position_slider.setSingleStep(5)
        self.position_slider.setPageStep(50)
        layout.addWidget(self.position_slider)

        # Control buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.play_button = QtWidgets.QPushButton("Play")
        self.pause_button = QtWidgets.QPushButton("Pause")
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.back_button = QtWidgets.QPushButton("⏪ Back 10s")
        self.fwd_button = QtWidgets.QPushButton("⏩ Forward 10s")
        self.replay_button = QtWidgets.QPushButton("Replay")
        self.exit_button = QtWidgets.QPushButton("Exit")

        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.fwd_button)
        button_layout.addWidget(self.replay_button)
        button_layout.addWidget(self.exit_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect buttons
        self.play_button.clicked.connect(self.play)
        self.pause_button.clicked.connect(self.pause)
        self.stop_button.clicked.connect(self.stop)
        self.back_button.clicked.connect(self.seek_back_10s)
        self.fwd_button.clicked.connect(self.seek_forward_10s)
        self.replay_button.clicked.connect(self.replay)
        self.exit_button.clicked.connect(self.exit_to_preview)
        self.position_slider.sliderReleased.connect(self.seek_to_slider)
        self.position_slider.sliderPressed.connect(self._on_slider_pressed)
        self.position_slider.valueChanged.connect(self._on_slider_changed)

        # Shortcuts
        QtWidgets.QShortcut(QtGui.QKeySequence("Space"), self, activated=self.toggle_play_pause)
        QtWidgets.QShortcut(QtGui.QKeySequence("Left"), self, activated=lambda: self.seek_ms(-5000))
        QtWidgets.QShortcut(QtGui.QKeySequence("Right"), self, activated=lambda: self.seek_ms(5000))
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Left"), self, activated=self.seek_back_10s)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Right"), self, activated=self.seek_forward_10s)
        QtWidgets.QShortcut(QtGui.QKeySequence("Home"), self, activated=self.seek_to_start)
        QtWidgets.QShortcut(QtGui.QKeySequence("End"), self, activated=self.seek_to_end)
        QtWidgets.QShortcut(QtGui.QKeySequence("Esc"), self, activated=self.exit_to_preview)

        # VLC events: end-of-media
        em = self.mediaplayer.event_manager()
        em.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_end_reached)

        # Timer to sync slider with playback
        self._slider_timer = QtCore.QTimer(self)
        self._slider_timer.setInterval(500)
        self._slider_timer.timeout.connect(self.update_slider)
        self._slider_dragging = False

        self.current_filepath = None

    def play_file(self, filepath):
        import datetime, inspect
        def diag(msg):
            frame = inspect.currentframe().f_back
            print(f"[DIAG {datetime.datetime.now().isoformat()}] line {frame.f_lineno}: {msg}")

        diag(f"play_file called with filepath={filepath}")
        # Convert QUrl to string if needed
        if hasattr(filepath, "toLocalFile"):
            diag("filepath has toLocalFile method, converting")
            filepath = filepath.toLocalFile()
        self.current_filepath = filepath
        diag(f"Set self.current_filepath={self.current_filepath}")
        media = self.instance.media_new(filepath)
        diag("Created VLC media object")
        self.mediaplayer.set_media(media)
        diag("Set media to mediaplayer")
        if sys.platform.startswith('linux'):
            diag("Setting X window for VLC")
            self.mediaplayer.set_xwindow(int(self.video_frame.winId()))
        # Pause for 1 second to allow GUI to load
        import time
        diag("Pausing for 1 second before starting playback...")
        time.sleep(1)
        self.mediaplayer.play()
        diag("Called mediaplayer.play()")
        app_signals.isPlayingChanged.emit(True)
        diag("Emitted isPlayingChanged(True)")
        self._slider_timer.start()
        diag("Started slider timer")

    def play(self):
        if self.mediaplayer.get_media():
            self.mediaplayer.play()
            # app_signals.isPlayingChanged.emit(True)
        elif self.current_filepath:
            self.play_file(self.current_filepath)
        self._slider_timer.start()

    def pause(self):
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            # app_signals.isPlayingChanged.emit(False)
        # keep timer running; position still updates on pause

    def stop(self):
        self.mediaplayer.stop()
        app_signals.isPlayingChanged.emit(False)
        self._slider_timer.stop()
        self.position_slider.setValue(0)

    def replay(self):
        if self.current_filepath:
            self.stop()
            self.play_file(self.current_filepath)

    def exit_to_preview(self):
        # Ask the main window to show the preview
        main_window = self.window()
        if hasattr(main_window, "show_preview"):
            main_window.show_preview()
        app_signals.isPlayingChanged.emit(False)
        self._slider_timer.stop()

    def handle_recording_state(self, is_recording):
        # Disable playback controls if recording is active
        self.play_button.setEnabled(not is_recording)
        self.pause_button.setEnabled(not is_recording)
        self.stop_button.setEnabled(not is_recording)
        self.replay_button.setEnabled(not is_recording)
        self.exit_button.setEnabled(not is_recording)
        self.position_slider.setEnabled(not is_recording)

    def toggle_play_pause(self):
        if self.mediaplayer.is_playing():
            self.pause()
        else:
            self.play()

    def seek_ms(self, delta_ms):
        cur = self.mediaplayer.get_time()
        length = self.mediaplayer.get_length()
        if cur < 0:
            cur = 0
        if length <= 0:
            return
        target = max(0, min(cur + int(delta_ms), length))
        self.mediaplayer.set_time(target)
        self.position_slider.setValue(target)

    def seek_to_start(self):
        self.mediaplayer.set_time(0)
        self.position_slider.setValue(0)

    def seek_to_end(self):
        length = self.mediaplayer.get_length()
        if length > 0:
            self.mediaplayer.set_time(length)
            self.position_slider.setValue(length)

    def update_slider(self):
        if not self._slider_dragging and self.mediaplayer is not None:
            length = self.mediaplayer.get_length()  # ms
            if length > 0:
                pos = self.mediaplayer.get_time()  # ms
                # Map to slider range
                self.position_slider.setRange(0, length)
                self.position_slider.setValue(max(0, min(max(0, pos), length)))

    def seek_to_slider(self):
        if self.mediaplayer is not None:
            target = self.position_slider.value()
            # VLC expects ms
            length = self.mediaplayer.get_length()
            if length > 0:
                clamped = max(0, min(int(target), length))
                self.mediaplayer.set_time(clamped)
        self._slider_dragging = False

    def _on_slider_pressed(self):
        self._slider_dragging = True

    def _on_slider_changed(self, value):
        # Optional live seek while dragging
        if self._slider_dragging and self.mediaplayer is not None:
            length = self.mediaplayer.get_length()
            if length > 0:
                clamped = max(0, min(int(value), length))
                self.mediaplayer.set_time(clamped)

    def seek_back_10s(self):
        if self.mediaplayer is not None:
            cur = self.mediaplayer.get_time()
            self.mediaplayer.set_time(max(0, cur - 10000))

    def seek_forward_10s(self):
        if self.mediaplayer is not None:
            cur = self.mediaplayer.get_time()
            length = self.mediaplayer.get_length()
            self.mediaplayer.set_time(min(length, cur + 10000))

    def _on_end_reached(self, event):
        # Reset UI and state when media ends
        self._slider_timer.stop()
        self.position_slider.setValue(0)
        app_signals.isPlayingChanged.emit(False)


# Standalone test
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = "/home/lea/Videos/vid_9ec8d262d8.mp4"
    player = VideoPlayer()
    player.show()
    player.play_file(video_path)
    sys.exit(app.exec_())