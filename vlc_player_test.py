import sys
import vlc
from qt import QtWidgets, QtCore

class VLCPlayerWidget(QtWidgets.QFrame):
    def __init__(self, filepath=None, parent=None):
        super().__init__(parent)
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()
        self.setMinimumSize(640, 480)
        if filepath:
            QtCore.QTimer.singleShot(500, lambda: self.play_file(filepath))

    def play_file(self, filepath):
        media = self.instance.media_new(filepath)
        self.mediaplayer.set_media(media)
        if sys.platform.startswith('linux'):
            self.mediaplayer.set_xwindow(int(self.winId()))
        elif sys.platform == "win32":
            self.mediaplayer.set_hwnd(int(self.winId()))
        elif sys.platform == "darwin":
            self.mediaplayer.set_nsobject(int(self.winId()))
        self.mediaplayer.play()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, filepath=None):
        super().__init__()
        self.setWindowTitle("VLC Video Player Test")
        self.player = VLCPlayerWidget(filepath, self)
        self.setCentralWidget(self.player)
        self.resize(700, 500)

def main():
    app = QtWidgets.QApplication(sys.argv)
    # Use first argument as video path, or default
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = "/home/lea/Videos/vid_9ec8d262d8.mp4"
    window = MainWindow(video_path)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()