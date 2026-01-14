import sys
from qt import QtWidgets, QtGui, QtCore

class ImageViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None
        self.setWindowTitle("Image Viewer")
        self.layout = QtWidgets.QVBoxLayout(self)

        # Image display
        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.image_label.setSizePolicy(size_policy)
        self.layout.addWidget(self.image_label, 1)

        # Controls row (Exit only)
        controls = QtWidgets.QHBoxLayout()
        self.exit_button = QtWidgets.QPushButton("Exit")
        self.exit_button.clicked.connect(self.exit_to_preview)
        controls.addStretch(1)
        controls.addWidget(self.exit_button)
        self.layout.addLayout(controls)

    def load_file(self, filepath: str):
        # Convert QUrl to local file if needed
        if hasattr(filepath, "toLocalFile"):
            filepath = filepath.toLocalFile()
        pm = QtGui.QPixmap(filepath)
        if pm.isNull():
            QtWidgets.QMessageBox.critical(self, "Error", f"Could not load image:\n{filepath}")
            return
        self._pixmap = pm
        self._update_scaled()

    def exit_to_preview(self):
        # Ask MainWindow to show preview
        main_window = self.window()
        if hasattr(main_window, "show_preview"):
            main_window.show_preview()

    def resizeEvent(self, event: QtGui.QResizeEvent):
        super().resizeEvent(event)
        self._update_scaled()

    def _update_scaled(self):
        if self._pixmap is None:
            return
        target_size = self.image_label.size()
        if target_size.width() <= 0 or target_size.height() <= 0:
            return
        scaled = self._pixmap.scaled(target_size, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled)
