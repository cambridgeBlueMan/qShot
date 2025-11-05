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
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.setWindowTitle("CameraControlsModel Test GUI")
        layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel("Contrast: 1.00")
        layout.addWidget(self.label)

        self.slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 320)
        self.slider.setValue(160)  # Midpoint (should be contrast=1)
        layout.addWidget(self.slider)

        self.spin = QtWidgets.QDoubleSpinBox()
        self.spin.setRange(0.0, 32.0)
        self.spin.setSingleStep(0.1)
        self.spin.setValue(1.0)
        layout.addWidget(self.spin)

        self.slider.valueChanged.connect(self.on_slider_changed)
        self.spin.valueChanged.connect(self.on_spin_changed)

        self.setLayout(layout)

    def slider_to_contrast(self, slider_value):
        """Map slider value (0-320) to contrast (0-32), with 1 at midpoint (160)."""
        slider_min = 0
        slider_max = 320
        slider_mid = 160
        if slider_value <= slider_mid:
            # Map 0..160 to 0..1
            return (slider_value / slider_mid) * 1.0
        else:
            # Map 160..320 to 1..32
            return 1.0 + ((slider_value - slider_mid) / (slider_max - slider_mid)) * (32.0 - 1.0)

    def contrast_to_slider(self, contrast):
        """Map contrast (0-32) to slider value (0-320), with 1 at midpoint (160)."""
        slider_min = 0
        slider_max = 320
        slider_mid = 160
        if contrast <= 1.0:
            # Map 0..1 to 0..160
            return int((contrast / 1.0) * slider_mid)
        else:
            # Map 1..32 to 160..320
            return int(slider_mid + ((contrast - 1.0) / (32.0 - 1.0)) * (slider_max - slider_mid))

    def on_slider_changed(self, slider_value):
        contrast = self.slider_to_contrast(slider_value)
        self.label.setText(f"Contrast: {contrast:.2f}")
        self.spin.blockSignals(True)
        self.spin.setValue(contrast)
        self.spin.blockSignals(False)

    def on_spin_changed(self, contrast):
        slider_value = self.contrast_to_slider(contrast)
        self.slider.blockSignals(True)
        self.slider.setValue(slider_value)
        self.slider.blockSignals(False)
        self.label.setText(f"Contrast: {contrast:.2f}")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    win = ContrastSliderDemo()
    win.show()
    sys.exit(app.exec())