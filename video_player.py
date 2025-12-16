import sys
from PyQt5 import QtWidgets, QtCore
import vlc
from app_signals import app_signals


class VideoPlayer(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()

        # Layout for the player and the exit button
        layout = QtWidgets.QVBoxLayout(self)

        # Video frame
        self.video_frame = QtWidgets.QFrame(self)
        layout.addWidget(self.video_frame, stretch=1)

        # Exit button
        self.exit_button = QtWidgets.QPushButton("Exit", self)
        self.exit_button.clicked.connect(self.exit_to_preview)
        layout.addWidget(self.exit_button)

        self.setLayout(layout)

    def play_file(self, filepath):
        # Convert QUrl to string if needed
        if hasattr(filepath, "toLocalFile"):
            filepath = filepath.toLocalFile()
        media = self.instance.media_new(filepath)
        self.mediaplayer.set_media(media)
        if sys.platform.startswith('linux'):
            self.mediaplayer.set_xwindow(int(self.video_frame.winId()))
        elif sys.platform == "win32":
            self.mediaplayer.set_hwnd(int(self.video_frame.winId()))
        elif sys.platform == "darwin":
            self.mediaplayer.set_nsobject(int(self.video_frame.winId()))
        self.mediaplayer.play()
        app_signals.isPlayingChanged.emit(True)

    def exit_to_preview(self):
        # Ask the main window to show the preview
        main_window = self.window()
        if hasattr(main_window, "show_preview"):
            main_window.show_preview()
        app_signals.isPlayingChanged.emit(False)

    def handle_recording_state(self, is_recording):
        # Disable playback controls if recording is active
        self.exit_button.setEnabled(not is_recording)
        # ...other UI updates...


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