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
        self.jpeg_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.jpeg_slider.setMinimum(self.controls_model._control_ranges["JpegQuality"][0])
        self.jpeg_slider.setMaximum(self.controls_model._control_ranges["JpegQuality"][1])
        self.jpeg_slider.setValue(self.controls_model.JpegQuality)
        self.jpeg_slider.setTickInterval(1)
        self.jpeg_value_label = QtWidgets.QLabel(str(self.controls_model.JpegQuality))

        jpeg_layout.addWidget(jpeg_label)
        jpeg_layout.addWidget(self.jpeg_slider)
        jpeg_layout.addWidget(self.jpeg_value_label)
        group_layout.addLayout(jpeg_layout)

        # Connect slider to model
        self.jpeg_slider.valueChanged.connect(self.on_jpeg_slider_changed)
        self.controls_model.JpegQualityChanged.connect(self.on_jpeg_quality_changed)

        # --- Automatic Exposure Control (AE) Checkbox row ---
        ae_layout = QtWidgets.QHBoxLayout()
        self.ae_checkbox = QtWidgets.QCheckBox("Automatic Exposure Control (AE)")
        self.ae_checkbox.setChecked(self.controls_model.AeEnable)
        ae_layout.addWidget(self.ae_checkbox)
        group_layout.addLayout(ae_layout)

        # Connect checkbox to model
        self.ae_checkbox.stateChanged.connect(self.on_ae_checkbox_changed)
        self.controls_model.AeEnableChanged.connect(self.on_ae_enable_changed)

        # --- Select Resolution row ---
        res_layout = QtWidgets.QHBoxLayout()
        res_label = QtWidgets.QLabel("Select Resolution")
        self.res_combo = ResCombo(config_model=self.config_model)
        res_layout.addWidget(res_label)
        res_layout.addWidget(self.res_combo)
        group_layout.addLayout(res_layout)

        # Examine available sensor_modes and choose the highest resolution.
        # For still photos, framerate is not important, so we select the mode
        # with the largest size tuple (highest resolution) and update the config_model
        # accordingly. This ensures the camera is configured for maximum image quality.
        highest_mode_dict = None
        if hasattr(self.cam, "sensor_modes") and self.cam.sensor_modes:
            highest_mode_dict = self.cam.sensor_modes[-1]
            if self.config_model:
                if 'size' in highest_mode_dict:
                    self.config_model.set_nested('sensor', 'output_size', highest_mode_dict['size'])
                if 'bit_depth' in highest_mode_dict:
                    self.config_model.set_nested('sensor', 'bit_depth', highest_mode_dict['bit_depth'])
                # Diagnostic to confirm values are set
                print("ConfigModel sensor.output_size:", self.config_model._config.get('sensor', {}).get('output_size'))
                print("ConfigModel sensor.bit_depth:", self.config_model._config.get('sensor', {}).get('bit_depth'))
            # Pass highest_mode_dict to ResCombo's generate_combo_items method
            self.res_combo.generateComboItems(highest_mode_dict)
            self.res_combo.set_largest_resolution()

        # Connect resolution combo index change to handler
        self.res_combo.currentIndexChanged.connect(self.set_size_in_config)

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

    # --- Signal Handlers as Class Methods ---
    def on_jpeg_slider_changed(self, value):
        self.controls_model.JpegQuality = value
        self.jpeg_value_label.setText(str(value))

    def on_jpeg_quality_changed(self, value):
        self.jpeg_slider.setValue(value)
        self.jpeg_value_label.setText(str(value))

    def on_ae_checkbox_changed(self, state):
        self.controls_model.AeEnable = bool(state)

    def on_ae_enable_changed(self, value):
        self.ae_checkbox.setChecked(bool(value))

    # def on_res_combo_index_changed(self, index):
    #     size = self.res_combo.itemData(index)
    #     if size and self.config_model:
    #         self.config_model.set_nested('sensor', 'output_size', size)
    #         print(f"Resolution changed to: {size}")
    
    def set_size_in_config(self, index):
        """
        Slot to set the 'main', 'size' value in the config dictionary when the combo selection changes.
        Also stops and restarts the camera to apply the new configuration.
        """
        size = self.res_combo.itemData(index)
        if size and self.config_model and self.cam:
            self.config_model.set_nested('main', 'size', size)
            print(f"Set config['main']['size'] to {size}")
            # Stop, reconfigure, and restart camera
            was_running = getattr(self.cam, 'started', False)
            if was_running:
                self.cam.stop()
            config_dict = self.config_model.to_dict()
            self.cam.configure(config_dict)
            if was_running:
                self.cam.start()