from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog
)
from PyQt6.QtCore import Qt

class PathsWidget(QWidget):
    """
    Simple UI to view/change PathModel settings.
    Other code should use PathModel directly; this widget only edits it.
    """
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.model = kwargs.get("path_model")
        layout = QVBoxLayout(self)

        # Still folder
        row = QHBoxLayout()
        row.addWidget(QLabel("Still folder:"))
        self.still_edit = QLineEdit(self.model.still_folder)
        row.addWidget(self.still_edit)
        btn = QPushButton("Browse")
        btn.clicked.connect(self._browse_still)
        row.addWidget(btn)
        layout.addLayout(row)

        # Video folder
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Video folder:"))
        self.video_edit = QLineEdit(self.model.video_folder)
        row2.addWidget(self.video_edit)
        btn2 = QPushButton("Browse")
        btn2.clicked.connect(self._browse_video)
        row2.addWidget(btn2)
        layout.addLayout(row2)

        # Rootnames and strategy
        rn_row = QHBoxLayout()
        rn_row.addWidget(QLabel("Image root:"))
        self.img_root = QLineEdit(self.model.rootnames.get("img", "img_"))
        rn_row.addWidget(self.img_root)
        rn_row.addWidget(QLabel("Strategy:"))
        self.strategy = QComboBox()
        self.strategy.addItems(["date", "sequence", "hash"])
        self.strategy.setCurrentText(self.model.strategy)
        rn_row.addWidget(self.strategy)
        layout.addLayout(rn_row)

        # Quick generate button + preview
        gen_row = QHBoxLayout()
        self.preview_label = QLabel(self.model.generate_filename("img"))
        gen_btn = QPushButton("Generate sample")
        gen_btn.clicked.connect(self._generate_sample)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        gen_row.addWidget(self.preview_label)
        gen_row.addWidget(gen_btn)
        gen_row.addWidget(save_btn)
        layout.addLayout(gen_row)

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