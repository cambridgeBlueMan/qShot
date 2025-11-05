try:
    from PyQt6 import QtWidgets, QtGui, QtCore
    Qt = QtCore.Qt
except ImportError:
    from PyQt5 import QtWidgets, QtGui, QtCore
    Qt = QtCore.Qt

"""
contrast_slider_demo.py
-----------------------
A minimal PyQt5/PyQt6 demo showing a single slider mapped to a contrast value (0-32),
with 1 at the midpoint. The mapping is piecewise linear, as in controls_gui.py.
"""

class ContrastSliderDemo(QtWidgets.QWidget):
    def __init__(self, controls_model=None, parent=None, **kwargs):
        super().__init__(parent)
        self.setWindowTitle("CameraControlsModel Test GUI")
        self.controls_model = controls_model
        layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel("Contrast: 1.00")
        layout.addWidget(self.label)

        self.slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 320)
        layout.addWidget(self.slider)

        self.spin = QtWidgets.QDoubleSpinBox()
        self.spin.setRange(0.0, 32.0)
        self.spin.setSingleStep(0.1)
        layout.addWidget(self.spin)

        self.slider.valueChanged.connect(self.on_slider_changed)
        self.spin.valueChanged.connect(self.on_spin_changed)

        self.setLayout(layout)

        # Initialize from model if available
        if self.controls_model and hasattr(self.controls_model, "Contrast"):
            contrast = self.controls_model.Contrast
        else:
            contrast = 1.0
        self.spin.setValue(contrast)
        self.slider.setValue(self.contrast_to_slider(contrast))
        self.label.setText(f"Contrast: {contrast:.2f}")

        # Connect to model signal if available
        if self.controls_model and hasattr(self.controls_model, "ContrastChanged"):
            self.controls_model.ContrastChanged.connect(self.on_model_contrast_changed)

    def slider_to_contrast(self, slider_value):
        slider_min = 0
        slider_max = 320
        slider_mid = 160
        if slider_value <= slider_mid:
            return (slider_value / slider_mid) * 1.0
        else:
            return 1.0 + ((slider_value - slider_mid) / (slider_max - slider_mid)) * (32.0 - 1.0)

    def contrast_to_slider(self, contrast):
        slider_min = 0
        slider_max = 320
        slider_mid = 160
        if contrast <= 1.0:
            return int((contrast / 1.0) * slider_mid)
        else:
            return int(slider_mid + ((contrast - 1.0) / (32.0 - 1.0)) * (slider_max - slider_mid))

    def on_slider_changed(self, slider_value):
        contrast = self.slider_to_contrast(slider_value)
        print(f"Slider changed: slider_value={slider_value}, mapped contrast={contrast:.2f}")
        if self.controls_model:
            self.controls_model.Contrast = contrast  # Only update the model

    def on_spin_changed(self, contrast):
        if self.controls_model:
            self.controls_model.Contrast = contrast  # Only update the model

    def on_model_contrast_changed(self, contrast):
        # Called when model emits ContrastChanged
        self.slider.blockSignals(True)
        self.spin.blockSignals(True)
        self.slider.setValue(self.contrast_to_slider(contrast))
        self.spin.setValue(contrast)
        self.label.setText(f"Contrast: {contrast:.2f}")
        self.slider.blockSignals(False)
        self.spin.blockSignals(False)

if __name__ == "__main__":
    import sys

    # Dummy controls_model for standalone testing
    class DummySignal:
        def __init__(self): self._funcs = []
        def connect(self, func): self._funcs.append(func)
        def emit(self, value): 
            for f in self._funcs:
                f(value)

    class DummyControlsModel:
        def __init__(self):
            self._contrast = 1.0
            self.ContrastChanged = DummySignal()
        @property
        def Contrast(self):
            return self._contrast
        @Contrast.setter
        def Contrast(self, value):
            if value != self._contrast:
                self._contrast = value
                self.ContrastChanged.emit(value)

    app = QtWidgets.QApplication(sys.argv)
    controls_model = DummyControlsModel()
    win = ContrastSliderDemo(controls_model=controls_model)
    win.show()
    sys.exit(app.exec())