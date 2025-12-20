from qt import QtWidgets, QtCore, Qt

DIAL_SIZE = 60  # Add this near the top of the file, after imports

class AdjustmentsWidget(QtWidgets.QWidget):
    def __init__(self, controls_model, parent=None, mode="sliders", **kwargs):
        super().__init__(parent)
        self.controls_model = controls_model

        # Default values for each adjustment
        self.defaults = {
            "contrast": 1.0,
            "sharpness": 1.0,
            "brightness": 0.0,
            "saturation": 1.0,
        }

        group = QtWidgets.QGroupBox("Adjustments")
        group_layout = QtWidgets.QVBoxLayout()
        group_layout.setSpacing(12)      # Increase spacing between rows (default is 6)
        group_layout.setContentsMargins(10, 16, 10, 16)  # Add more top/bottom margin

        # --- Mode Selection (Slider/Dial) ---
        mode_layout = QtWidgets.QHBoxLayout()
        self.slider_radio = QtWidgets.QRadioButton("Sliders")
        self.dial_radio = QtWidgets.QRadioButton("Dials")
        # Set initial mode based on argument
        if mode == "dials":
            self.dial_radio.setChecked(True)
        else:
            self.slider_radio.setChecked(True)
        mode_layout.addWidget(self.slider_radio)
        mode_layout.addWidget(self.dial_radio)
        group_layout.addLayout(mode_layout)

        # --- Contrast ---
        min_val, max_val, default = self.controls_model._control_ranges.get("Contrast", (0.0, 32.0, 1.0))
        self.contrast_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(int(min_val * 10), int(max_val * 10))  # Use model values for range
        contrast_row = QtWidgets.QHBoxLayout()
        contrast_row.addWidget(QtWidgets.QLabel("Contrast"))
        contrast_row.addWidget(self.contrast_slider)
        self.contrast_reset_btn = QtWidgets.QPushButton("Reset")
        self.contrast_reset_btn.setFixedWidth(60)
        self.contrast_reset_btn.setStyleSheet("font-size: 9pt; padding: 1px 4px;")
        self.contrast_reset_btn.clicked.connect(self.reset_contrast)
        contrast_row.addWidget(self.contrast_reset_btn)
        #group_layout.addLayout(contrast_row)

        # --- Sharpness ---
        min_val, max_val, default = self.controls_model._control_ranges.get("Sharpness", (0.0, 16.0, 1.0))
        self.sharpness_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.sharpness_slider.setRange(int(min_val * 10), int(max_val * 10))  # Use model values for range
        sharpness_row = QtWidgets.QHBoxLayout()
        sharpness_row.addWidget(QtWidgets.QLabel("Sharpness"))
        sharpness_row.addWidget(self.sharpness_slider)
        self.sharpness_reset_btn = QtWidgets.QPushButton("Reset")
        self.sharpness_reset_btn.setFixedWidth(60)
        self.sharpness_reset_btn.setStyleSheet("font-size: 9pt; padding: 1px 4px;")
        self.sharpness_reset_btn.clicked.connect(self.reset_sharpness)
        sharpness_row.addWidget(self.sharpness_reset_btn)
        #group_layout.addLayout(sharpness_row)

        # --- Brightness ---
        min_val, max_val, default = self.controls_model._control_ranges.get("Brightness", (-1.0, 1.0, 0.0))
        self.brightness_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(int(min_val * 100), int(max_val * 100))  # -100 to +100
        brightness_row = QtWidgets.QHBoxLayout()
        brightness_row.addWidget(QtWidgets.QLabel("Brightness"))
        brightness_row.addWidget(self.brightness_slider)
        self.brightness_reset_btn = QtWidgets.QPushButton("Reset")
        self.brightness_reset_btn.setFixedWidth(60)
        self.brightness_reset_btn.setStyleSheet("font-size: 9pt; padding: 1px 4px;")
        self.brightness_reset_btn.clicked.connect(self.reset_brightness)
        brightness_row.addWidget(self.brightness_reset_btn)
        #group_layout.addLayout(brightness_row)

        # --- Saturation ---
        min_val, max_val, default = self.controls_model._control_ranges.get("Saturation", (0.0, 32.0, 1.0))
        self.saturation_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setRange(int(min_val * 10), int(max_val * 10))  # 0 to 320
        saturation_row = QtWidgets.QHBoxLayout()
        saturation_row.addWidget(QtWidgets.QLabel("Saturation"))
        saturation_row.addWidget(self.saturation_slider)
        self.saturation_reset_btn = QtWidgets.QPushButton("Reset")
        self.saturation_reset_btn.setFixedWidth(60)
        self.saturation_reset_btn.setStyleSheet("font-size: 9pt; padding: 1px 4px;")
        self.saturation_reset_btn.clicked.connect(self.reset_saturation)
        saturation_row.addWidget(self.saturation_reset_btn)
        #group_layout.addLayout(saturation_row)

        # --- Dials Row (Horizontal) ---
        dials_row = QtWidgets.QHBoxLayout()
        dials_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # --- Contrast Dial ---
        min_val, max_val, default = self.controls_model._control_ranges.get("Contrast", (0.0, 32.0, 1.0))
        contrast_dial_col = QtWidgets.QVBoxLayout()
        contrast_dial_col.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        contrast_dial_col.addWidget(QtWidgets.QLabel("Contrast"))
        self.contrast_dial = QtWidgets.QDial()
        self.contrast_dial.setRange(int(min_val * 10), int(max_val * 10))
        self.contrast_dial.setValue(self.contrast_to_slider(default))
        self.contrast_dial.setFixedSize(DIAL_SIZE, DIAL_SIZE)
        contrast_dial_col.addWidget(self.contrast_dial)
        self.contrast_dial_reset_btn = QtWidgets.QPushButton("Reset")
        self.contrast_dial_reset_btn.setFixedWidth(60)
        self.contrast_dial_reset_btn.setStyleSheet("font-size: 9pt; padding: 1px 4px;")
        self.contrast_dial_reset_btn.clicked.connect(self.reset_contrast)
        contrast_dial_col.addWidget(self.contrast_dial_reset_btn)
        contrast_dial_widget = QtWidgets.QWidget()
        contrast_dial_widget.setLayout(contrast_dial_col)
        dials_row.addWidget(contrast_dial_widget)

        # --- Sharpness Dial ---
        min_val, max_val, default = self.controls_model._control_ranges.get("Sharpness", (0.0, 16.0, 1.0))
        sharpness_dial_col = QtWidgets.QVBoxLayout()
        sharpness_dial_col.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        sharpness_dial_col.addWidget(QtWidgets.QLabel("Sharpness"))
        self.sharpness_dial = QtWidgets.QDial()
        self.sharpness_dial.setRange(int(min_val * 10), int(max_val * 10))
        self.sharpness_dial.setValue(self.sharpness_to_slider(default))
        self.sharpness_dial.setFixedSize(DIAL_SIZE, DIAL_SIZE)
        sharpness_dial_col.addWidget(self.sharpness_dial)
        self.sharpness_dial_reset_btn = QtWidgets.QPushButton("Reset")
        self.sharpness_dial_reset_btn.setFixedWidth(60)
        self.sharpness_dial_reset_btn.setStyleSheet("font-size: 9pt; padding: 1px 4px;")
        self.sharpness_dial_reset_btn.clicked.connect(self.reset_sharpness)
        sharpness_dial_col.addWidget(self.sharpness_dial_reset_btn)
        sharpness_dial_widget = QtWidgets.QWidget()
        sharpness_dial_widget.setLayout(sharpness_dial_col)
        dials_row.addWidget(sharpness_dial_widget)

        # --- Brightness Dial ---
        min_val, max_val, default = self.controls_model._control_ranges.get("Brightness", (-1.0, 1.0, 0.0))
        brightness_dial_col = QtWidgets.QVBoxLayout()
        brightness_dial_col.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        brightness_dial_col.addWidget(QtWidgets.QLabel("Brightness"))
        self.brightness_dial = QtWidgets.QDial()
        self.brightness_dial.setRange(int(min_val * 100), int(max_val * 100))
        self.brightness_dial.setValue(self.brightness_to_slider(default))
        self.brightness_dial.setFixedSize(DIAL_SIZE, DIAL_SIZE)
        brightness_dial_col.addWidget(self.brightness_dial)
        self.brightness_dial_reset_btn = QtWidgets.QPushButton("Reset")
        self.brightness_dial_reset_btn.setFixedWidth(60)
        self.brightness_dial_reset_btn.setStyleSheet("font-size: 9pt; padding: 1px 4px;")
        self.brightness_dial_reset_btn.clicked.connect(self.reset_brightness)
        brightness_dial_col.addWidget(self.brightness_dial_reset_btn)
        brightness_dial_widget = QtWidgets.QWidget()
        brightness_dial_widget.setLayout(brightness_dial_col)
        dials_row.addWidget(brightness_dial_widget)

        # --- Saturation Dial ---
        min_val, max_val, default = self.controls_model._control_ranges.get("Saturation", (0.0, 32.0, 1.0))
        saturation_dial_col = QtWidgets.QVBoxLayout()
        saturation_dial_col.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        saturation_dial_col.addWidget(QtWidgets.QLabel("Saturation"))
        self.saturation_dial = QtWidgets.QDial()
        self.saturation_dial.setRange(int(min_val * 10), int(max_val * 10))
        self.saturation_dial.setValue(self.saturation_to_slider(default))
        self.saturation_dial.setFixedSize(DIAL_SIZE, DIAL_SIZE)
        saturation_dial_col.addWidget(self.saturation_dial)
        self.saturation_dial_reset_btn = QtWidgets.QPushButton("Reset")
        self.saturation_dial_reset_btn.setFixedWidth(60)
        self.saturation_dial_reset_btn.setStyleSheet("font-size: 9pt; padding: 1px 4px;")
        self.saturation_dial_reset_btn.clicked.connect(self.reset_saturation)
        saturation_dial_col.addWidget(self.saturation_dial_reset_btn)
        saturation_dial_widget = QtWidgets.QWidget()
        saturation_dial_widget.setLayout(saturation_dial_col)
        dials_row.addWidget(saturation_dial_widget)

        # --- Add dials row to a container for show/hide ---
        self.dials_container = QtWidgets.QWidget()
        self.dials_container.setLayout(dials_row)
        group_layout.addWidget(self.dials_container)
        self.dials_container.hide()

        # --- Sliders Container (Vertical) ---
        self.sliders_container = QtWidgets.QWidget()
        sliders_layout = QtWidgets.QVBoxLayout()
        sliders_layout.setSpacing(12)
        sliders_layout.setContentsMargins(0, 0, 0, 0)
        sliders_layout.addLayout(contrast_row)
        sliders_layout.addLayout(sharpness_row)
        sliders_layout.addLayout(brightness_row)
        sliders_layout.addLayout(saturation_row)
        self.sliders_container.setLayout(sliders_layout)
        group_layout.addWidget(self.sliders_container)
        group_layout.addWidget(self.dials_container)
        group_layout.addStretch()
        group.setLayout(group_layout)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(group)
        self.setLayout(main_layout)

        # --- Hookups: Contrast ---
        self.contrast_slider.valueChanged.connect(self.on_contrast_slider_changed)
        controls_model.ContrastChanged.connect(self.on_model_contrast_changed)
        self.contrast_slider.setValue(self.contrast_to_slider(controls_model.Contrast))

        # --- Hookups: Sharpness ---
        self.sharpness_slider.valueChanged.connect(self.on_sharpness_slider_changed)
        controls_model.SharpnessChanged.connect(self.on_model_sharpness_changed)
        self.sharpness_slider.setValue(self.sharpness_to_slider(controls_model.Sharpness))

        # --- Hookups: Brightness ---
        self.brightness_slider.valueChanged.connect(self.on_brightness_slider_changed)
        controls_model.BrightnessChanged.connect(self.on_model_brightness_changed)
        self.brightness_slider.setValue(self.brightness_to_slider(controls_model.Brightness))

        # --- Hookups: Saturation ---
        self.saturation_slider.valueChanged.connect(self.on_saturation_slider_changed)
        controls_model.SaturationChanged.connect(self.on_model_saturation_changed)
        self.saturation_slider.setValue(self.saturation_to_slider(controls_model.Saturation))

        # --- Update control mode on radio button toggle ---
        self.slider_radio.toggled.connect(self.update_control_mode)

        # Connect slider and dial to their slots
        self.contrast_slider.valueChanged.connect(self.on_contrast_slider_changed)
        self.contrast_dial.valueChanged.connect(self.on_contrast_dial_changed)

        # Connect model signal to update both widgets
        controls_model.ContrastChanged.connect(self.on_model_contrast_changed)

        # --- Hookups: Sharpness Dials ---
        self.sharpness_dial.valueChanged.connect(self.on_sharpness_dial_changed)
        self.controls_model.SharpnessChanged.connect(self.on_model_sharpness_changed)

        # --- Hookups: Brightness Dials ---
        self.brightness_dial.valueChanged.connect(self.on_brightness_dial_changed)
        self.controls_model.BrightnessChanged.connect(self.on_model_brightness_changed)

        # --- Hookups: Saturation Dials ---
        self.saturation_dial.valueChanged.connect(self.on_saturation_dial_changed)
        self.controls_model.SaturationChanged.connect(self.on_model_saturation_changed)

        self.update_control_mode()  # Ensure correct initial mode

    # --- Mapping functions (adjust as needed for your value ranges) ---
    def contrast_to_slider(self, contrast):

        min_val, max_val, default = self.controls_model._control_ranges.get("Contrast", (0.0, 32.0, 1.0))
        slider_min, slider_max, slider_mid = int(min_val * 10), int(max_val * 10), int(((max_val - min_val) /2)* 10)
        # print(f"Contrast slider_min={slider_min}, slider_max={slider_max}, slider_mid={slider_mid}, min_val={min_val}, max_val={max_val}, default={default}")
        if contrast <= 1.0:
            return int((contrast / 1.0) * slider_mid)
        else:
            return int(slider_mid + ((contrast - 1.0) / (32.0 - 1.0)) * (slider_max - slider_mid))
        
    def slider_to_contrast(self, slider_value):
        min_val, max_val, default = self.controls_model._control_ranges.get("Contrast", (0.0, 16.0, 1.0))
        slider_min, slider_max, slider_mid = int(min_val * 10), int(max_val * 10), int(((max_val - min_val) /2)* 10)
        if slider_value <= slider_mid:
            return (slider_value / slider_mid) * 1.0
        else:
            return 1.0 + ((slider_value - slider_mid) / (slider_max - slider_mid)) * (32.0 - 1.0)

    def sharpness_to_slider(self, sharpness):
        min_val, max_val, default = self.controls_model._control_ranges.get("Sharpness", (0.0, 16.0, 1.0))
        slider_min, slider_max, slider_mid = int(min_val * 10), int(max_val * 10), int(((max_val - min_val) / 2) * 10)
        if sharpness <= 1.0:
            return int((sharpness / 1.0) * slider_mid)
        else:
            return int(slider_mid + ((sharpness - 1.0) / (16.0 - 1.0)) * (slider_max - slider_mid))

    def slider_to_sharpness(self, slider_value):
        min_val, max_val, default = self.controls_model._control_ranges.get("Sharpness", (0.0, 16.0, 1.0))
        slider_min, slider_max, slider_mid = int(min_val * 10), int(max_val * 10), int(((max_val - min_val) / 2) * 10)
        if slider_value <= slider_mid:
            return (slider_value / slider_mid) * 1.0
        else:
            return 1.0 + ((slider_value - slider_mid) / (slider_max - slider_mid)) * (16.0 - 1.0)

    def brightness_to_slider(self, brightness):
        # Linear mapping: float -1.0..1.0 -> int -100..100
        return int(brightness * 100)

    def slider_to_brightness(self, slider_value):
        # Linear mapping: int -100..100 -> float -1.0..1.0
        return slider_value / 100.0

    def saturation_to_slider(self, saturation):
        min_val, max_val, default = self.controls_model._control_ranges.get("Saturation", (0.0, 32.0, 1.0))
        slider_min, slider_max, slider_mid = int(min_val * 10), int(max_val * 10), int(((max_val - min_val) / 2) * 10)
        if saturation <= 1.0:
            return int((saturation / 1.0) * slider_mid)
        else:
            return int(slider_mid + ((saturation - 1.0) / (max_val - 1.0)) * (slider_max - slider_mid))

    def slider_to_saturation(self, slider_value):
        min_val, max_val, default = self.controls_model._control_ranges.get("Saturation", (0.0, 32.0, 1.0))
        slider_min, slider_max, slider_mid = int(min_val * 10), int(max_val * 10), int(((max_val - min_val) / 2) * 10)
        if slider_value <= slider_mid:
            return (slider_value / slider_mid) * 1.0
        else:
            return 1.0 + ((slider_value - slider_mid) / (slider_max - slider_mid)) * (max_val - 1.0)

    # --- Slots for slider changes ---
    def on_contrast_slider_changed(self, value):
        contrast = self.slider_to_contrast(value)
        self.controls_model.Contrast = contrast
        self.contrast_slider.setToolTip(f"Contrast: {contrast:.2f}")

    def on_contrast_dial_changed(self, value):
        contrast = self.slider_to_contrast(value)
        self.controls_model.Contrast = contrast
        self.contrast_dial.setToolTip(f"Contrast: {contrast:.2f}")

    def on_sharpness_slider_changed(self, value):
        sharpness = self.slider_to_sharpness(value)
        self.sharpness_slider.setToolTip(f"Sharpness: {sharpness:.2f}")
        QtWidgets.QToolTip.showText(
            self.sharpness_slider.mapToGlobal(self.sharpness_slider.rect().center()),
            f"Sharpness: {sharpness:.2f}",
            self.sharpness_slider
        )
        self.controls_model.Sharpness = sharpness

    def on_sharpness_dial_changed(self, value):
        sharpness = self.slider_to_sharpness(value)
        self.controls_model.Sharpness = sharpness
        self.sharpness_dial.setToolTip(f"Sharpness: {sharpness:.2f}")


    def on_brightness_slider_changed(self, value):
        brightness = self.slider_to_brightness(value)
        self.brightness_slider.setToolTip(f"Brightness: {brightness:.2f}")
        QtWidgets.QToolTip.showText(
            self.brightness_slider.mapToGlobal(self.brightness_slider.rect().center()),
            f"Brightness: {brightness:.2f}",
            self.brightness_slider
        )
        self.controls_model.Brightness = brightness

    def on_brightness_dial_changed(self, value):
        brightness = self.slider_to_brightness(value)
        self.controls_model.Brightness = brightness
        self.brightness_dial.setToolTip(f"Brightness: {brightness:.2f}")

    def on_saturation_slider_changed(self, value):
        saturation = self.slider_to_saturation(value)
        self.saturation_slider.setToolTip(f"Saturation: {saturation:.2f}")
        QtWidgets.QToolTip.showText(
            self.saturation_slider.mapToGlobal(self.saturation_slider.rect().center()),
            f"Saturation: {saturation:.2f}",
            self.saturation_slider
        )
        self.controls_model.Saturation = saturation

    def on_saturation_dial_changed(self, value):
        saturation = self.slider_to_saturation(value)
        self.controls_model.Saturation = saturation
        self.saturation_dial.setToolTip(f"Saturation: {saturation:.2f}")

    # --- Reset buttons ---
    def reset_contrast(self):
        min_val, max_val, default = self.controls_model._control_ranges.get("Contrast", (0.0, 32.0, 1.0))
        self.contrast_slider.setValue(self.contrast_to_slider(default))
    def reset_sharpness(self):
        min_val, max_val, default = self.controls_model._control_ranges.get("Sharpness", (0.0, 16.0, 1.0))
        self.sharpness_slider.setValue(self.sharpness_to_slider(default))
    def reset_brightness(self):
        min_val, max_val, default = self.controls_model._control_ranges.get("Brightness", (-1.0, 1.0, 0.0))
        self.brightness_slider.setValue(self.brightness_to_slider(default))
    def reset_saturation(self):
        min_val, max_val, default = self.controls_model._control_ranges.get("Saturation", (0.0, 32.0, 1.0))
        self.saturation_slider.setValue(self.saturation_to_slider(default))

    # --- Slots for model changes ---
    def on_model_contrast_changed(self, value):
        slider_val = self.contrast_to_slider(value)
        self.contrast_slider.blockSignals(True)
        self.contrast_slider.setValue(slider_val)
        self.contrast_slider.blockSignals(False)
        self.contrast_dial.blockSignals(True)
        self.contrast_dial.setValue(slider_val)
        self.contrast_dial.blockSignals(False)
    def on_model_sharpness_changed(self, value):
        slider_val = self.sharpness_to_slider(value)
        self.sharpness_slider.blockSignals(True)
        self.sharpness_slider.setValue(slider_val)
        self.sharpness_slider.blockSignals(False)
        self.sharpness_dial.blockSignals(True)
        self.sharpness_dial.setValue(slider_val)
        self.sharpness_dial.blockSignals(False)

    def on_model_brightness_changed(self, value):
        slider_val = self.brightness_to_slider(value)
        self.brightness_slider.blockSignals(True)
        self.brightness_slider.setValue(slider_val)
        self.brightness_slider.blockSignals(False)
        self.brightness_dial.blockSignals(True)
        self.brightness_dial.setValue(slider_val)
        self.brightness_dial.blockSignals(False)

    def on_model_saturation_changed(self, value):
        slider_val = self.saturation_to_slider(value)
        self.saturation_slider.blockSignals(True)
        self.saturation_slider.setValue(slider_val)
        self.saturation_slider.blockSignals(False)
        self.saturation_dial.blockSignals(True)
        self.saturation_dial.setValue(slider_val)
        self.saturation_dial.blockSignals(False)

    def update_control_mode(self):
        if self.slider_radio.isChecked():
            self.sliders_container.show()
            self.dials_container.hide()
        else:
            self.sliders_container.hide()
            self.dials_container.show()

# Example usage:
if __name__ == "__main__":
    import sys
    from controls_model import ControlsModel

    app = QtWidgets.QApplication(sys.argv)
    controls_model = ControlsModel()
    w = AdjustmentsWidget(controls_model)
    w.show()
    sys.exit(app.exec())