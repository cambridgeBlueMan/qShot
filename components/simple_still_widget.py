from components.component_base import ComponentBase
from qt import QtWidgets, Qt
from adjustments import AdjustmentsWidget
from res_combo import ResCombo  # Import ResCombo

class SimpleStill(ComponentBase):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        # Create a horizontal layout for the buttons
        button_row = QtWidgets.QHBoxLayout()
        self.capture_button = QtWidgets.QPushButton("Capture")
        button_row.addWidget(self.capture_button)
        self.capture_button.clicked.connect(self.capture_image)

        self.more_button = QtWidgets.QPushButton("more...")
        self.more_button.setCheckable(True)
        button_row.addWidget(self.more_button)
        self.more_button.toggled.connect(self.toggle_common_controls)

        self.base_layout.addLayout(button_row)

        # Create the 'Common Controls' group box (invisible by default)
        self.common_controls_group = QtWidgets.QGroupBox("Common Controls")
        self.common_controls_group.setVisible(False)
        group_layout = QtWidgets.QVBoxLayout()

        # --- JPEG Quality Slider (first row) ---
        jpeg_layout = QtWidgets.QHBoxLayout()
        jpeg_label = QtWidgets.QLabel("JPEG Quality")
        jpeg_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        jpeg_slider.setMinimum(self.controls_model._control_ranges["JpegQuality"][0])
        jpeg_slider.setMaximum(self.controls_model._control_ranges["JpegQuality"][1])
        jpeg_slider.setValue(self.controls_model.JpegQuality)
        jpeg_slider.setTickInterval(1)
        jpeg_value_label = QtWidgets.QLabel(str(self.controls_model.JpegQuality))

        jpeg_layout.addWidget(jpeg_label)
        jpeg_layout.addWidget(jpeg_slider)
        jpeg_layout.addWidget(jpeg_value_label)
        group_layout.addLayout(jpeg_layout)

        # Connect slider to model
        def on_jpeg_slider_changed(value):
            self.controls_model.JpegQuality = value
            jpeg_value_label.setText(str(value))
        jpeg_slider.valueChanged.connect(on_jpeg_slider_changed)

        def on_jpeg_quality_changed(value):
            jpeg_slider.setValue(value)
            jpeg_value_label.setText(str(value))
        self.controls_model.JpegQualityChanged.connect(on_jpeg_quality_changed)

        # --- Automatic Exposure Control (AE) Checkbox row ---
        ae_layout = QtWidgets.QHBoxLayout()
        ae_checkbox = QtWidgets.QCheckBox("Automatic Exposure Control (AE)")
        ae_checkbox.setChecked(self.controls_model.AeEnable)
        ae_layout.addWidget(ae_checkbox)
        group_layout.addLayout(ae_layout)

        # Connect checkbox to model
        def on_ae_checkbox_changed(state):
            self.controls_model.AeEnable = bool(state)
        ae_checkbox.stateChanged.connect(on_ae_checkbox_changed)

        def on_ae_enable_changed(value):
            ae_checkbox.setChecked(bool(value))
        self.controls_model.AeEnableChanged.connect(on_ae_enable_changed)

        # --- Select Resolution row ---
        res_layout = QtWidgets.QHBoxLayout()
        res_label = QtWidgets.QLabel("Select Resolution")
        res_combo = ResCombo(config_model=self.config_model)
        res_layout.addWidget(res_label)
        res_layout.addWidget(res_combo)
        group_layout.addLayout(res_layout)

        # Add AdjustmentsWidget to the group box
        self.adjustments_widget = AdjustmentsWidget(self.controls_model, mode="dials")
        group_layout.addWidget(self.adjustments_widget)

        self.common_controls_group.setLayout(group_layout)
        self.base_layout.addWidget(self.common_controls_group)
        self.base_layout.addStretch()

        self.preview.done_signal.connect(self.capture_done)

    def capture_done(self, job):
        print("Image capture completed:", job)  
        self.capture_button.setEnabled(True)

    def capture_image(self):
        print("Capture button pressed: capturing still image...")
        if self.cam and self.preview:
            print("Starting image capture...")
            self.cam.capture_file("still.jpg", signal_function=self.preview.signal_done)    
            self.capture_button.setEnabled(False)

    def toggle_common_controls(self, checked):
        if checked:
            print("More... button toggled ON")
            self.common_controls_group.setVisible(True)
            self.more_button.setText("less")
        else:
            print("More... button toggled OFF")
            self.common_controls_group.setVisible(False)
            self.more_button.setText("more...")