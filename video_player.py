import sys
from PyQt5 import QtWidgets, QtCore
import vlc
from app_signals import app_signals


class VideoPlayer(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()

        # Layout for the player and the control buttons
        layout = QtWidgets.QVBoxLayout(self)

        # Video frame
        self.video_frame = QtWidgets.QFrame(self)
        layout.addWidget(self.video_frame, stretch=1)

        # Control buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.play_button = QtWidgets.QPushButton("Play")
        self.pause_button = QtWidgets.QPushButton("Pause")
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.replay_button = QtWidgets.QPushButton("Replay")
        self.exit_button = QtWidgets.QPushButton("Exit")

        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.replay_button)
        button_layout.addWidget(self.exit_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect buttons
        self.play_button.clicked.connect(self.play)
        self.pause_button.clicked.connect(self.pause)
        self.stop_button.clicked.connect(self.stop)
        self.replay_button.clicked.connect(self.replay)
        self.exit_button.clicked.connect(self.exit_to_preview)

        self.current_filepath = None

    def play_file(self, filepath):
        # Convert QUrl to string if needed
        if hasattr(filepath, "toLocalFile"):
            filepath = filepath.toLocalFile()
        self.current_filepath = filepath
        media = self.instance.media_new(filepath)
        self.mediaplayer.set_media(media)
        if sys.platform.startswith('linux'):
            self.mediaplayer.set_xwindow(int(self.video_frame.winId()))
        self.mediaplayer.play()
        app_signals.isPlayingChanged.emit(True)

    def play(self):
        if self.mediaplayer.get_media():
            self.mediaplayer.play()
            # app_signals.isPlayingChanged.emit(True)
        elif self.current_filepath:
            self.play_file(self.current_filepath)

    def pause(self):
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            # app_signals.isPlayingChanged.emit(False)

    def stop(self):
        self.mediaplayer.stop()
        # app_signals.isPlayingChanged.emit(False)

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

    def handle_recording_state(self, is_recording):
        # Disable playback controls if recording is active
        self.play_button.setEnabled(not is_recording)
        self.pause_button.setEnabled(not is_recording)
        self.stop_button.setEnabled(not is_recording)
        self.replay_button.setEnabled(not is_recording)
        self.exit_button.setEnabled(not is_recording)


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