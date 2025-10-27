from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QTableWidgetSelectionRange, QGridLayout, QApplication, QMainWindow
)
from PyQt6.QtCore import Qt
import sys

class PathsWidget(QWidget):
    """
    UI to view/change PathModel settings using a table (grid) layout.
    """
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.model = kwargs.get("path_model")
        layout = QVBoxLayout(self)

        grid = QGridLayout()

        # Still folder row
        grid.addWidget(QLabel("Still folder:"), 0, 0)
        self.still_edit = QLineEdit(self.model.still_folder)
        grid.addWidget(self.still_edit, 0, 1)
        btn = QPushButton("Browse")
        btn.clicked.connect(self._browse_still)
        grid.addWidget(btn, 0, 2)

        # Video folder row
        grid.addWidget(QLabel("Video folder:"), 1, 0)
        self.video_edit = QLineEdit(self.model.video_folder)
        grid.addWidget(self.video_edit, 1, 1)
        btn2 = QPushButton("Browse")
        btn2.clicked.connect(self._browse_video)
        grid.addWidget(btn2, 1, 2)

        # Image root row
        grid.addWidget(QLabel("Image root:"), 2, 0)
        self.img_root = QLineEdit(self.model.rootnames.get("img", "img_"))
        grid.addWidget(self.img_root, 2, 1)

        # Strategy row
        grid.addWidget(QLabel("Strategy:"), 3, 0)
        self.strategy = QComboBox()
        self.strategy.addItems(["date", "sequence", "hash"])
        self.strategy.setCurrentText(self.model.strategy)
        grid.addWidget(self.strategy, 3, 1)

        # Generate sample and Save row
        self.preview_label = QLabel(self.model.generate_filename("img"))
        grid.addWidget(self.preview_label, 4, 0, 1, 2)
        gen_btn = QPushButton("Generate sample")
        gen_btn.clicked.connect(self._generate_sample)
        grid.addWidget(gen_btn, 4, 2)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        grid.addWidget(save_btn, 5, 2)

        layout.addLayout(grid)
        self.setLayout(layout)

        # update model->widget if changed externally
        self.model.pathsChanged.connect(self._update_from_model)

    def _browse_still(self):
        d = QFileDialog.getExistingDirectory(self, "Select still folder", self.model.still_folder)
        if d:
            self.still_edit.setText(d)
            self.model.set_still_folder(d)

    def _browse_video(self):
        d = QFileDialog.getExistingDirectory(self, "Select video folder", self.model.video_folder)
        if d:
            self.video_edit.setText(d)
            self.model.set_video_folder(d)

    def _generate_sample(self):
        self.preview_label.setText(self.model.generate_filename("img"))

    def _save(self):
        self.model.set_rootname("img", self.img_root.text())
        self.model.set_strategy(self.strategy.currentText())
        # also sync edits to folder fields
        self.model.set_still_folder(self.still_edit.text())
        self.model.set_video_folder(self.video_edit.text())

    def _update_from_model(self):
        self.still_edit.setText(self.model.still_folder)
        self.video_edit.setText(self.model.video_folder)
        self.img_root.setText(self.model.rootnames.get("img", "img_"))
        self.strategy.setCurrentText(self.model.strategy)
        self.preview_label.setText(self.model.generate_filename("img"))

# Standalone test harness
if __name__ == "__main__":
    from path_model import PathModel  # Adjust import if needed
    app = QApplication(sys.argv)
    path_model = PathModel()
    widget = PathsWidget(path_model=path_model)
    window = QMainWindow()
    window.setCentralWidget(widget)
    window.setWindowTitle("Test PathsWidget")
    window.resize(600, 250)
    window.show()
    sys.exit(app.exec())