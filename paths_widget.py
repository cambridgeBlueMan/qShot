import sys
from qt import QtWidgets, QtGui, QtCore, Qt

class PathsWidget(QtWidgets.QWidget):
    """
    UI to view/change PathModel settings using two group boxes: Paths and File name.
    """
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.model = kwargs.get("path_model")
        layout = QtWidgets.QVBoxLayout(self)

        # --- Paths group box ---
        paths_group = QtWidgets.QGroupBox("Paths")
        paths_group.setStyleSheet("""
            QtWidgets.QGroupBox {
                font-weight: bold;
            }
        """)
        paths_grid = QtWidgets.QGridLayout()
        # Still folder row
        paths_grid.addWidget(QtWidgets.QLabel("Still folder:"), 0, 0)
        self.still_edit = QtWidgets.QLineEdit(self.model.still_folder)
        self.still_edit.setReadOnly(True)
        self.still_edit.setFrame(False)
        self.still_edit.setStyleSheet(
            "QtWidgets.QLineEdit { background: #f5f5f5; color: #222; border: none; padding: 2px 4px; }"
        )
        paths_grid.addWidget(self.still_edit, 0, 1)
        btn = QtWidgets.QPushButton("Browse")
        btn.clicked.connect(self._browse_still)
        paths_grid.addWidget(btn, 0, 2)
        # Video folder row
        paths_grid.addWidget(QtWidgets.QLabel("Video folder:"), 1, 0)
        self.video_edit = QtWidgets.QLineEdit(self.model.video_folder)
        self.video_edit.setReadOnly(True)
        self.video_edit.setFrame(False)
        self.video_edit.setStyleSheet(
            "QtWidgets.QLineEdit { background: #f5f5f5; color: #222; border: none; padding: 2px 4px; }"
        )
        paths_grid.addWidget(self.video_edit, 1, 1)
        btn2 = QtWidgets.QPushButton("Browse")
        btn2.clicked.connect(self._browse_video)
        paths_grid.addWidget(btn2, 1, 2)
        paths_group.setLayout(paths_grid)
        layout.addWidget(paths_group)

        # --- File name group box ---
        filename_group = QtWidgets.QGroupBox("File name")
        filename_group.setStyleSheet("""
            QtWidgets.QGroupBox {
                font-weight: bold;
            }
        """)
        filename_grid = QtWidgets.QGridLayout()
        # Image root row
        filename_grid.addWidget(QtWidgets.QLabel("Image root:"), 0, 0)
        self.img_root = QtWidgets.QLineEdit(self.model.rootnames.get("img", "img_"))
        filename_grid.addWidget(self.img_root, 0, 1)
        # Strategy row
        filename_grid.addWidget(QtWidgets.QLabel("Strategy:"), 1, 0)
        self.strategy = QtWidgets.QComboBox()
        self.strategy.addItems(["date", "sequence", "hash"])
        self.strategy.setCurrentText(self.model.strategy)
        filename_grid.addWidget(self.strategy, 1, 1)
        # Generate sample and Save row
        self.preview_label = QtWidgets.QLabel(self.model.generate_filename("img"))
        filename_grid.addWidget(self.preview_label, 2, 0, 1, 2)
        gen_btn = QtWidgets.QPushButton("Generate sample")
        gen_btn.clicked.connect(self._generate_sample)
        filename_grid.addWidget(gen_btn, 2, 2)
        save_btn = QtWidgets.QPushButton("Save")
        save_btn.clicked.connect(self._save)
        filename_grid.addWidget(save_btn, 3, 2)
        filename_group.setLayout(filename_grid)
        layout.addWidget(filename_group)

        # Add stretch to keep group boxes compact on resize
        layout.addStretch(1)

        self.setLayout(layout)

        # update model->widget if changed externally
        self.model.pathsChanged.connect(self._update_from_model)

    def _browse_still(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Select still folder", self.model.still_folder)
        if d:
            self.still_edit.setText(d)
            self.model.set_still_folder(d)

    def _browse_video(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Select video folder", self.model.video_folder)
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
    app = QtWidgets.QApplication(sys.argv)
    path_model = PathModel()
    widget = PathsWidget(path_model=path_model)
    window = QtWidgets.QMainWindow()
    window.setCentralWidget(widget)
    window.setWindowTitle("Test PathsWidget")
    window.resize(600, 250)
    window.show()
    sys.exit(app.exec())