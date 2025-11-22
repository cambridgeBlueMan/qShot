from components.component_base import ComponentBase
from qt import QtWidgets

class SimpleVideo(ComponentBase):
    def __init__(self, parent=None, **kwargs):
        self.cam = kwargs.get("cam")
        self.config_model = kwargs.get("config_model")
        self.controls_model = kwargs.get("controls_model")
        self.paths_model = kwargs.get("paths_model")
        self.preview = kwargs.get("preview")
        super().__init__(
            parent=parent,
            cam=self.cam,
            config_model=self.config_model,
            controls_model=self.controls_model,
            paths_model=self.paths_model,
            show_jpeg_quality=False,  # or True if you want
            show_ae=True,
            show_resolution=True,
            show_adjustments=True,
            show_filename=True
        )

        # Button row (copied from SimpleStill, customize as needed)
        button_row = QtWidgets.QHBoxLayout()
        self.record_button = QtWidgets.QPushButton("Record")
        button_row.addWidget(self.record_button)
        self.record_button.clicked.connect(self.record_video)

        self.more_button = QtWidgets.QPushButton("more...")
        self.more_button.setCheckable(True)
        button_row.addWidget(self.more_button)
        self.more_button.toggled.connect(self.toggle_common_controls)

        self.base_layout.insertLayout(0, button_row)  # Insert at the top

        if self.preview:
            self.preview.done_signal.connect(self.record_done)

    def record_done(self, job):
        print("Video recording completed:", job)
        self.record_button.setEnabled(True)

    def record_video(self):
        print("Record button pressed: starting video recording...")
        if self.cam and self.preview:
            file_path = self.paths_model.full_path(kind="vid")
            self.cam.record_file(file_path, signal_function=self.preview.signal_done)
            self.record_button.setEnabled(False)