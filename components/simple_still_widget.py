from components.component_base import ComponentBase
from qt import QtWidgets

class SimpleStill(ComponentBase):
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
            show_jpeg_quality=True,
            show_ae=True,
            show_resolution=True,
            show_adjustments=True,
            show_filename=True
        )

        # Button row (unique to SimpleStill)
        button_row = QtWidgets.QHBoxLayout()
        self.capture_button = QtWidgets.QPushButton("Capture")
        button_row.addWidget(self.capture_button)
        self.capture_button.clicked.connect(self.capture_image)

        self.more_button = QtWidgets.QPushButton("more...")
        self.more_button.setCheckable(True)
        button_row.addWidget(self.more_button)
        self.more_button.toggled.connect(self.toggle_common_controls)

        self.base_layout.insertLayout(0, button_row)  # Insert at the top

        if self.preview:
            self.preview.done_signal.connect(self.capture_done)

    def capture_done(self, job):
        print("Image capture completed:", job)
        self.capture_button.setEnabled(True)

    def capture_image(self):
        print("Capture button pressed: capturing still image...")
        if self.cam and self.preview:
            file_path = self.paths_model.full_path()
            self.cam.capture_file(file_path, signal_function=self.preview.signal_done)
            self.capture_button.setEnabled(False)
