"""
test_camera_controls_gui.py
--------------------------
A PyQt6 test GUI for CameraControlsModel, allowing interactive setting of many controls.
Each control is represented by a suitable widget (slider, spinbox, checkbox, etc.).
Some controls are duplicated in the UI to test two-way binding and signal propagation.
"""

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QSpinBox,
    QDoubleSpinBox, QCheckBox, QComboBox, QGroupBox
)
from PyQt6.QtCore import Qt
from controls_model import controls_model

class ControlsGui(QWidget):
    def __init__(self, cam, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CameraControlsModel Test GUI")
        self.cam = cam  # Store the passed camera instance
        self.config = controls_model
        layout = QVBoxLayout()

        # Contrast (float, 0.0-32.0) - slider and spinbox
        contrast_group = QGroupBox("Contrast")
        contrast_layout = QHBoxLayout()
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(0, 320)
        self.contrast_slider.setValue(int(self.config.Contrast * 10))
        self.contrast_spin = QDoubleSpinBox()
        self.contrast_spin.setRange(0.0, 32.0)
        self.contrast_spin.setSingleStep(0.1)
        self.contrast_spin.setValue(self.config.Contrast)
        contrast_layout.addWidget(QLabel("Slider:"))
        contrast_layout.addWidget(self.contrast_slider)
        contrast_layout.addWidget(QLabel("SpinBox:"))
        contrast_layout.addWidget(self.contrast_spin)
        contrast_group.setLayout(contrast_layout)
        layout.addWidget(contrast_group)

        # Brightness (float, -1.0 to 1.0) - slider and spinbox
        brightness_group = QGroupBox("Brightness")
        brightness_layout = QHBoxLayout()
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-10, 10)
        self.brightness_slider.setValue(int(self.config.Brightness * 10))
        self.brightness_spin = QDoubleSpinBox()
        self.brightness_spin.setRange(-1.0, 1.0)
        self.brightness_spin.setSingleStep(0.1)
        self.brightness_spin.setValue(self.config.Brightness)
        brightness_layout.addWidget(QLabel("Slider:"))
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(QLabel("SpinBox:"))
        brightness_layout.addWidget(self.brightness_spin)
        brightness_group.setLayout(brightness_layout)
        layout.addWidget(brightness_group)

        # AeEnable (bool) - checkbox and duplicate checkbox
        ae_enable_group = QGroupBox("AeEnable")
        ae_enable_layout = QHBoxLayout()
        self.ae_enable_checkbox = QCheckBox("Enable AE")
        self.ae_enable_checkbox.setChecked(self.config.AeEnable)
        self.ae_enable_checkbox_dup = QCheckBox("Enable AE (duplicate)")
        self.ae_enable_checkbox_dup.setChecked(self.config.AeEnable)
        ae_enable_layout.addWidget(self.ae_enable_checkbox)
        ae_enable_layout.addWidget(self.ae_enable_checkbox_dup)
        ae_enable_group.setLayout(ae_enable_layout)
        layout.addWidget(ae_enable_group)

        # HdrMode (int, 0-4) - combobox and spinbox
        hdr_group = QGroupBox("HdrMode")
        hdr_layout = QHBoxLayout()
        self.hdr_combo = QComboBox()
        self.hdr_combo.addItems([str(i) for i in range(5)])
        self.hdr_combo.setCurrentIndex(self.config.HdrMode)
        self.hdr_spin = QSpinBox()
        self.hdr_spin.setRange(0, 4)
        self.hdr_spin.setValue(self.config.HdrMode)
        hdr_layout.addWidget(QLabel("ComboBox:"))
        hdr_layout.addWidget(self.hdr_combo)
        hdr_layout.addWidget(QLabel("SpinBox:"))
        hdr_layout.addWidget(self.hdr_spin)
        hdr_group.setLayout(hdr_layout)
        layout.addWidget(hdr_group)

        # Sharpness (float, 0.0-16.0) - slider and spinbox
        sharpness_group = QGroupBox("Sharpness")
        sharpness_layout = QHBoxLayout()
        self.sharpness_slider = QSlider(Qt.Orientation.Horizontal)
        self.sharpness_slider.setRange(0, 160)
        self.sharpness_slider.setValue(int(self.config.Sharpness * 10))
        self.sharpness_spin = QDoubleSpinBox()
        self.sharpness_spin.setRange(0.0, 16.0)
        self.sharpness_spin.setSingleStep(0.1)
        self.sharpness_spin.setValue(self.config.Sharpness)
        sharpness_layout.addWidget(QLabel("Slider:"))
        sharpness_layout.addWidget(self.sharpness_slider)
        sharpness_layout.addWidget(QLabel("SpinBox:"))
        sharpness_layout.addWidget(self.sharpness_spin)
        sharpness_group.setLayout(sharpness_layout)
        layout.addWidget(sharpness_group)

        # Connect all CameraControlsModel signals to their slots
        self.config.ContrastChanged.connect(self.on_contrast_changed)
        self.config.BrightnessChanged.connect(self.on_brightness_changed)
        self.config.SharpnessChanged.connect(self.on_sharpness_changed)
        self.config.AeEnableChanged.connect(self.on_ae_enable_changed)
        self.config.HdrModeChanged.connect(self.on_hdr_mode_changed)
        self.config.AeExposureModeChanged.connect(self.on_ae_exposure_mode_changed)
        self.config.AeConstraintModeChanged.connect(self.on_ae_constraint_mode_changed)
        self.config.ExposureTimeModeChanged.connect(self.on_exposure_time_mode_changed)
        self.config.AeMeteringModeChanged.connect(self.on_ae_metering_mode_changed)
        self.config.AeFlickerPeriodChanged.connect(self.on_ae_flicker_period_changed)
        self.config.AnalogueGainModeChanged.connect(self.on_analogue_gain_mode_changed)
        self.config.AnalogueGainChanged.connect(self.on_analogue_gain_changed)
        self.config.StatsOutputEnableChanged.connect(self.on_stats_output_enable_changed)
        self.config.SyncFramesChanged.connect(self.on_sync_frames_changed)
        self.config.ExposureTimeChanged.connect(self.on_exposure_time_changed)
        self.config.AeFlickerModeChanged.connect(self.on_ae_flicker_mode_changed)
        self.config.SyncModeChanged.connect(self.on_sync_mode_changed)
        self.config.AwbEnableChanged.connect(self.on_awb_enable_changed)
        self.config.ColourGainsChanged.connect(self.on_colour_gains_changed)
        self.config.AwbModeChanged.connect(self.on_awb_mode_changed)
        self.config.ScalerCropsChanged.connect(self.on_scaler_crops_changed)
        self.config.ColourTemperatureChanged.connect(self.on_colour_temperature_changed)
        self.config.SaturationChanged.connect(self.on_saturation_changed)
        self.config.CnnEnableInputTensorChanged.connect(self.on_cnn_enable_input_tensor_changed)
        self.config.FrameDurationLimitsChanged.connect(self.on_frame_duration_limits_changed)
        self.config.ScalerCropChanged.connect(self.on_scaler_crop_changed)
        self.config.NoiseReductionModeChanged.connect(self.on_noise_reduction_mode_changed)
        self.config.ExposureValueChanged.connect(self.on_exposure_value_changed)
        self.config.resolutionChanged.connect(self.on_resolution_changed)
        self.config.formatChanged.connect(self.on_format_changed)

        # Coupling: update GUI widgets when model changes
        self.config.ContrastChanged.connect(lambda v: self.contrast_slider.setValue(int(v * 10)))
        self.config.ContrastChanged.connect(self.contrast_spin.setValue)
        self.config.BrightnessChanged.connect(lambda v: self.brightness_slider.setValue(int(v * 10)))
        self.config.BrightnessChanged.connect(self.brightness_spin.setValue)
        self.config.AeEnableChanged.connect(self.ae_enable_checkbox.setChecked)
        self.config.AeEnableChanged.connect(self.ae_enable_checkbox_dup.setChecked)
        self.config.HdrModeChanged.connect(self.hdr_combo.setCurrentIndex)
        self.config.HdrModeChanged.connect(self.hdr_spin.setValue)
        self.config.SharpnessChanged.connect(lambda v: self.sharpness_slider.setValue(int(v * 10)))
        self.config.SharpnessChanged.connect(self.sharpness_spin.setValue)

        # Coupling: update model when GUI widgets change
        def set_contrast_in_model_slider(v):
            self.config.Contrast = v / 10.0
        def set_contrast_in_model_spin(v):
            self.config.Contrast = v
        def set_brightness_in_model_slider(v):
            self.config.Brightness = v / 10.0
        def set_brightness_in_model_spin(v):
            self.config.Brightness = v
        def set_ae_enable_in_model_checkbox(state):
            self.config.AeEnable = bool(state)
        def set_hdr_in_model_combo(v):
            self.config.HdrMode = v
        def set_hdr_in_model_spin(v):
            self.config.HdrMode = v
        def set_sharpness_in_model_slider(v):
            self.config.Sharpness = v / 10.0
        def set_sharpness_in_model_spin(v):
            self.config.Sharpness = v

        self.contrast_slider.valueChanged.connect(set_contrast_in_model_slider)
        self.contrast_spin.valueChanged.connect(set_contrast_in_model_spin)
        self.brightness_slider.valueChanged.connect(set_brightness_in_model_slider)
        self.brightness_spin.valueChanged.connect(set_brightness_in_model_spin)
        self.ae_enable_checkbox.stateChanged.connect(set_ae_enable_in_model_checkbox)
        self.ae_enable_checkbox_dup.stateChanged.connect(set_ae_enable_in_model_checkbox)
        self.hdr_combo.currentIndexChanged.connect(set_hdr_in_model_combo)
        self.hdr_spin.valueChanged.connect(set_hdr_in_model_spin)
        self.sharpness_slider.valueChanged.connect(set_sharpness_in_model_slider)
        self.sharpness_spin.valueChanged.connect(set_sharpness_in_model_spin)

        self.setLayout(layout)

    # --- Camera control slots ---
    def on_contrast_changed(self, value):
        print(f"[Camera] Contrast changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"Contrast": value})

    def on_brightness_changed(self, value):
        print(f"[Camera] Brightness changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"Brightness": value})

    def on_sharpness_changed(self, value):
        print(f"[Camera] Sharpness changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"Sharpness": value})

    def on_ae_enable_changed(self, value):
        print(f"[Camera] AE Enable changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"AeEnable": value})

    def on_hdr_mode_changed(self, value):
        print(f"[Camera] HDR Mode changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"HdrMode": value})

    def on_ae_exposure_mode_changed(self, value):
        print(f"[Camera] AE Exposure Mode changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"AeExposureMode": value})

    def on_ae_constraint_mode_changed(self, value):
        print(f"[Camera] AE Constraint Mode changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"AeConstraintMode": value})

    def on_exposure_time_mode_changed(self, value):
        print(f"[Camera] Exposure Time Mode changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"ExposureTimeMode": value})

    def on_ae_metering_mode_changed(self, value):
        print(f"[Camera] AE Metering Mode changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"AeMeteringMode": value})

    def on_ae_flicker_period_changed(self, value):
        print(f"[Camera] AE Flicker Period changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"AeFlickerPeriod": value})

    def on_analogue_gain_mode_changed(self, value):
        print(f"[Camera] Analogue Gain Mode changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"AnalogueGainMode": value})

    def on_analogue_gain_changed(self, value):
        print(f"[Camera] Analogue Gain changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"AnalogueGain": value})

    def on_stats_output_enable_changed(self, value):
        print(f"[Camera] Stats Output Enable changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"StatsOutputEnable": value})

    def on_sync_frames_changed(self, value):
        print(f"[Camera] Sync Frames changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"SyncFrames": value})

    def on_exposure_time_changed(self, value):
        print(f"[Camera] Exposure Time changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"ExposureTime": value})

    def on_ae_flicker_mode_changed(self, value):
        print(f"[Camera] AE Flicker Mode changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"AeFlickerMode": value})

    def on_sync_mode_changed(self, value):
        print(f"[Camera] Sync Mode changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"SyncMode": value})

    def on_awb_enable_changed(self, value):
        print(f"[Camera] AWB Enable changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"AwbEnable": value})

    def on_colour_gains_changed(self, value):
        print(f"[Camera] Colour Gains changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"ColourGains": value})

    def on_awb_mode_changed(self, value):
        print(f"[Camera] AWB Mode changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"AwbMode": value})

    def on_scaler_crops_changed(self, value):
        print(f"[Camera] Scaler Crops changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"ScalerCrops": value})

    def on_colour_temperature_changed(self, value):
        print(f"[Camera] Colour Temperature changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"ColourTemperature": value})

    def on_saturation_changed(self, value):
        print(f"[Camera] Saturation changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"Saturation": value})

    def on_cnn_enable_input_tensor_changed(self, value):
        print(f"[Camera] CNN Enable Input Tensor changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"CnnEnableInputTensor": value})

    def on_frame_duration_limits_changed(self, value):
        print(f"[Camera] Frame Duration Limits changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"FrameDurationLimits": value})

    def on_scaler_crop_changed(self, value):
        print(f"[Camera] Scaler Crop changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"ScalerCrop": value})

    def on_noise_reduction_mode_changed(self, value):
        print(f"[Camera] Noise Reduction Mode changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"NoiseReductionMode": value})

    def on_exposure_value_changed(self, value):
        print(f"[Camera] Exposure Value changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"ExposureValue": value})

    def on_resolution_changed(self, value):
        print(f"[Camera] Resolution changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"Resolution": value})

    def on_format_changed(self, value):
        print(f"[Camera] Format changed to {value}")
        if hasattr(self.cam, "set_controls"):
            self.cam.set_controls({"Format": value})

if __name__ == "__main__":
    from picamera2 import Picamera2
    app = QApplication([])
    cam = Picamera2()
    win = ControlsGui(cam)
    win.show()
    app.exec()
