try:
    from PyQt6 import QtWidgets, QtCore
    Qt = QtCore.Qt
except ImportError:
    from PyQt5 import QtWidgets, QtCore
    Qt = QtCore.Qt

class AdjustmentsWidget(QtWidgets.QWidget):
    def __init__(self, controls_model, parent=None, **kwargs):
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
        group_layout.addLayout(contrast_row)

        # --- Sharpness ---
        self.sharpness_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.sharpness_slider.setRange(0, 320)
        sharpness_row = QtWidgets.QHBoxLayout()
        sharpness_row.addWidget(QtWidgets.QLabel("Sharpness"))
        sharpness_row.addWidget(self.sharpness_slider)
        self.sharpness_reset_btn = QtWidgets.QPushButton("Reset")
        self.sharpness_reset_btn.setFixedWidth(60)
        self.sharpness_reset_btn.setStyleSheet("font-size: 9pt; padding: 1px 4px;")
        self.sharpness_reset_btn.clicked.connect(self.reset_sharpness)
        sharpness_row.addWidget(self.sharpness_reset_btn)
        group_layout.addLayout(sharpness_row)

        # --- Brightness ---
        self.brightness_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 320)
        brightness_row = QtWidgets.QHBoxLayout()
        brightness_row.addWidget(QtWidgets.QLabel("Brightness"))
        brightness_row.addWidget(self.brightness_slider)
        self.brightness_reset_btn = QtWidgets.QPushButton("Reset")
        self.brightness_reset_btn.setFixedWidth(60)
        self.brightness_reset_btn.setStyleSheet("font-size: 9pt; padding: 1px 4px;")
        self.brightness_reset_btn.clicked.connect(self.reset_brightness)
        brightness_row.addWidget(self.brightness_reset_btn)
        group_layout.addLayout(brightness_row)

        # --- Saturation ---
        self.saturation_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setRange(0, 320)
        saturation_row = QtWidgets.QHBoxLayout()
        saturation_row.addWidget(QtWidgets.QLabel("Saturation"))
        saturation_row.addWidget(self.saturation_slider)
        self.saturation_reset_btn = QtWidgets.QPushButton("Reset")
        self.saturation_reset_btn.setFixedWidth(60)
        self.saturation_reset_btn.setStyleSheet("font-size: 9pt; padding: 1px 4px;")
        self.saturation_reset_btn.clicked.connect(self.reset_saturation)
        saturation_row.addWidget(self.saturation_reset_btn)
        group_layout.addLayout(saturation_row)

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

    # --- Mapping functions (adjust as needed for your value ranges) ---
    def contrast_to_slider(self, contrast):

        min_val, max_val, default = self.controls_model._control_ranges.get("Contrast", (0.0, 32.0, 1.0))
        slider_min, slider_max, slider_mid = int(min_val * 10), int(max_val * 10), int(((max_val - min_val) /2)* 10)
        print(f"Contrast slider_min={slider_min}, slider_max={slider_max}, slider_mid={slider_mid}, min_val={min_val}, max_val={max_val}, default={default}")
        if contrast <= 1.0:
            return int((contrast / 1.0) * slider_mid)
        else:
            return int(slider_mid + ((contrast - 1.0) / (32.0 - 1.0)) * (slider_max - slider_mid))
    def slider_to_contrast(self, slider_value):
        slider_min, slider_max, slider_mid = 0, 320, 160
        if slider_value <= slider_mid:
            return (slider_value / slider_mid) * 1.0
        else:
            return 1.0 + ((slider_value - slider_mid) / (slider_max - slider_mid)) * (32.0 - 1.0)

    def sharpness_to_slider(self, sharpness):
        slider_min, slider_max, slider_mid = 0, 320, 160
        if sharpness <= 1.0:
            return int((sharpness / 1.0) * slider_mid)
        else:
            return int(slider_mid + ((sharpness - 1.0) / (32.0 - 1.0)) * (slider_max - slider_mid))
    def slider_to_sharpness(self, slider_value):
        slider_min, slider_max, slider_mid = 0, 320, 160
        if slider_value <= slider_mid:
            return (slider_value / slider_mid) * 1.0
        else:
            return 1.0 + ((slider_value - slider_mid) / (slider_max - slider_mid)) * (32.0 - 1.0)

    def brightness_to_slider(self, brightness):
        # Assuming brightness range is -1.0 to 1.0
        return int((brightness + 1.0) * 160)
    def slider_to_brightness(self, slider_value):
        return (slider_value / 160.0) - 1.0

    def saturation_to_slider(self, saturation):
        slider_min, slider_max, slider_mid = 0, 320, 160
        if saturation <= 1.0:
            return int((saturation / 1.0) * slider_mid)
        else:
            return int(slider_mid + ((saturation - 1.0) / (32.0 - 1.0)) * (slider_max - slider_mid))
    def slider_to_saturation(self, slider_value):
        slider_min, slider_max, slider_mid = 0, 320, 160
        if slider_value <= slider_mid:
            return (slider_value / slider_mid) * 1.0
        else:
            return 1.0 + ((slider_value - slider_mid) / (slider_max - slider_mid)) * (32.0 - 1.0)

    # --- Slots for slider changes ---
    def on_contrast_slider_changed(self, value):
        contrast = self.slider_to_contrast(value)
        self.contrast_slider.setToolTip(f"Contrast: {contrast:.2f}")
        QtWidgets.QToolTip.showText(
            self.contrast_slider.mapToGlobal(self.contrast_slider.rect().center()),
            f"Contrast: {contrast:.2f}",
            self.contrast_slider
        )
        self.controls_model.Contrast = contrast

    def on_sharpness_slider_changed(self, value):
        sharpness = self.slider_to_sharpness(value)
        self.sharpness_slider.setToolTip(f"Sharpness: {sharpness:.2f}")
        QtWidgets.QToolTip.showText(
            self.sharpness_slider.mapToGlobal(self.sharpness_slider.rect().center()),
            f"Sharpness: {sharpness:.2f}",
            self.sharpness_slider
        )
        self.controls_model.Sharpness = sharpness

    def on_brightness_slider_changed(self, value):
        brightness = self.slider_to_brightness(value)
        self.brightness_slider.setToolTip(f"Brightness: {brightness:.2f}")
        QtWidgets.QToolTip.showText(
            self.brightness_slider.mapToGlobal(self.brightness_slider.rect().center()),
            f"Brightness: {brightness:.2f}",
            self.brightness_slider
        )
        self.controls_model.Brightness = brightness

    def on_saturation_slider_changed(self, value):
        saturation = self.slider_to_saturation(value)
        self.saturation_slider.setToolTip(f"Saturation: {saturation:.2f}")
        QtWidgets.QToolTip.showText(
            self.saturation_slider.mapToGlobal(self.saturation_slider.rect().center()),
            f"Saturation: {saturation:.2f}",
            self.saturation_slider
        )
        self.controls_model.Saturation = saturation

    # --- Reset buttons ---
    def reset_contrast(self):
        default = self.defaults["contrast"]
        self.contrast_slider.setValue(self.contrast_to_slider(default))
    def reset_sharpness(self):
        default = self.defaults["sharpness"]
        self.sharpness_slider.setValue(self.sharpness_to_slider(default))
    def reset_brightness(self):
        default = self.defaults["brightness"]
        self.brightness_slider.setValue(self.brightness_to_slider(default))
    def reset_saturation(self):
        default = self.defaults["saturation"]
        self.saturation_slider.setValue(self.saturation_to_slider(default))

    # --- Slots for model changes ---
    def on_model_contrast_changed(self, value):
        self.contrast_slider.blockSignals(True)
        self.contrast_slider.setValue(self.contrast_to_slider(value))
        self.contrast_slider.blockSignals(False)
    def on_model_sharpness_changed(self, value):
        self.sharpness_slider.blockSignals(True)
        self.sharpness_slider.setValue(self.sharpness_to_slider(value))
        self.sharpness_slider.blockSignals(False)
    def on_model_brightness_changed(self, value):
        self.brightness_slider.blockSignals(True)
        self.brightness_slider.setValue(self.brightness_to_slider(value))
        self.brightness_slider.blockSignals(False)
    def on_model_saturation_changed(self, value):
        self.saturation_slider.blockSignals(True)
        self.saturation_slider.setValue(self.saturation_to_slider(value))
        self.saturation_slider.blockSignals(False)

# Example usage:
if __name__ == "__main__":
    import sys
    from controls_model import ControlsModel

    app = QtWidgets.QApplication(sys.argv)
    controls_model = ControlsModel()
    w = AdjustmentsWidget(controls_model)
    w.show()
    sys.exit(app.exec())