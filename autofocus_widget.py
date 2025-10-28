from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton, QSlider, QCheckBox, QComboBox, QDial
from PyQt6.QtCore import Qt
from base_control_widget import BaseControlWidget

MINIMUM_SLIDER_VALUE = 0
MAXIMUM_SLIDER_VALUE = 100

class AutofocusWidget(BaseControlWidget):
    """
    A simple autofocus control widget with three radio buttons: Manual, Continuous, Auto,
    a dioptres adjustment slider, two option checkboxes, an AF range combo box, and a QDial.
    """
    def init_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("Autofocus Control", self)
        layout.addWidget(label)

        # Horizontal group of radio buttons and trigger button
        select_af_mode = QHBoxLayout()
        self.manual_radio = QRadioButton("Manual", self)
        self.continuous_radio = QRadioButton("Continuous", self)
        self.auto_radio = QRadioButton("Auto", self)
        
        select_af_mode.addWidget(self.manual_radio)
        select_af_mode.addWidget(self.continuous_radio)
        select_af_mode.addWidget(self.auto_radio)

        self.manual_radio.setChecked(True)
        self.manual_radio.toggled.connect(lambda checked: checked and self.setAfMode(0))
        self.continuous_radio.toggled.connect(lambda checked: checked and self.setAfMode(1))
        self.auto_radio.toggled.connect(lambda checked: checked and self.setAfMode(2))

        self.af_trigger = QPushButton("Trigger", self)
        self.af_trigger.clicked.connect(self.trigger_autofocus)
        select_af_mode.addWidget(self.af_trigger)

        layout.addLayout(select_af_mode)

        # Row: Dioptes label and horizontal slider
        dioptres_row = QHBoxLayout()
        dioptres_label = QLabel("Dioptes", self)
        dioptres_row.addWidget(dioptres_label)
        self.dioptres_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.dioptres_slider.setMinimum(MINIMUM_SLIDER_VALUE)
        self.dioptres_slider.setMaximum(MAXIMUM_SLIDER_VALUE)
        self.dioptres_slider.setValue(MINIMUM_SLIDER_VALUE)
        self.dioptres_slider.valueChanged.connect(self.setDioptres)
        dioptres_row.addWidget(self.dioptres_slider)

        layout.addLayout(dioptres_row)

        # Row: Fast Autofocus and Use Windows for Af checkboxes
        options_row = QHBoxLayout()
        self.fast_autofocus_checkbox = QCheckBox("Fast Autofocus", self)
        self.fast_autofocus_checkbox.setChecked(True)
        self.use_windows_checkbox = QCheckBox("Use Windows for Af", self)
        options_row.addWidget(self.fast_autofocus_checkbox)
        options_row.addWidget(self.use_windows_checkbox)
        self.use_windows_checkbox.toggled.connect(self.setAfMetering)
        self.fast_autofocus_checkbox.toggled.connect(self.setAfSpeed)
        layout.addLayout(options_row)

        # Row: Af Range label and combo box
        af_range_row = QHBoxLayout()
        af_range_label = QLabel("Af Range", self)
        af_range_row.addWidget(af_range_label)
        self.af_range_combo = QComboBox(self)
        self.af_range_combo.addItems(["Normal", "Macro", "Full"])
        af_range_row.addWidget(self.af_range_combo)
        layout.addLayout(af_range_row)
        self.af_range_combo.currentIndexChanged.connect(self.setAfRange)

        # New row: QDial with dimensions 100x100
        dial_row = QHBoxLayout()
        dial_label = QLabel("Dial", self)
        dial_row.addWidget(dial_label)
        self.dioptres_dial = QDial(self)
        self.dioptres_dial.setMinimum(MINIMUM_SLIDER_VALUE)
        self.dioptres_dial.setMaximum(MAXIMUM_SLIDER_VALUE)
        self.dioptres_dial.setValue(MINIMUM_SLIDER_VALUE)
        self.dioptres_dial.valueChanged.connect(self.setDioptres)
        dial_row.addWidget(self.dioptres_dial)
        layout.addLayout(dial_row)

        self.controls_model.LensPositionChanged.connect(self.onLensPositionChanged)
        self.setLayout(layout)

    def setAfRange(self, index):
        # Example method to handle AF range change
        #print(f"AF Range set to index: {index}")
        # Here you would typically update the camera control model
        self.controls_model.AfRange = index

    def trigger_autofocus(self):
        self.cam.autofocus_cycle(signal_function=self.on_af_done)

    def on_af_done(self, job):
        success = self.cam.wait(job)
        if success:
            print("Autofocus successful")
        else:
            print("Autofocus failed")

    def on_camera_job_done(self, job):
        # Only handle the job we started
        if hasattr(self, "_af_job") and job == self._af_job:
            try:
                success = job.get_result()
                if success:
                    print("Autofocus successful")
                else:
                    print("Autofocus failed")
            except TimeoutError:
                print("Autofocus operation timed out")
            self._af_job = None  # Clear job reference

    def setAfMode(self, mode):
        # Example method to handle AF mode change
        print(f"AF Mode set to {mode}")
        self.controls_model.AfMode = mode

    def setAfMetering(self, checked):
        # Set AfMetering to 1 if checked (Windows), 0 if unchecked (Global)
        self.controls_model.AfMetering = 1 if checked else 0

    def setAfSpeed(self, checked):
        # Set AfSpeed to 1 if checked (Fast), 0 if unchecked (Slow)
        self.controls_model.AfSpeed = 1 if checked else 0

    def setDialValue(self, value):
        # Example: connect to a controls_model property if needed
        # self.controls_model.DialValue = value
        pass  # Replace with actual logic as needed

    def setDioptres(self, value):
        # Map slider value (MINIMUM_SLIDER_VALUE to MAXIMUM_SLIDER_VALUE) to float 0.0 - 100.0
        mapped = (
            (value - MINIMUM_SLIDER_VALUE)
            / (MAXIMUM_SLIDER_VALUE - MINIMUM_SLIDER_VALUE)
        ) * 100.0
        self.controls_model.LensPosition = mapped
        # print(f"dioptres/LensPosition set to {mapped}")

    def onLensPositionChanged(self, value):
        # Update the slider and dial if LensPosition changes elsewhere
        slider_value = int(
            (value / 100.0) * (MAXIMUM_SLIDER_VALUE - MINIMUM_SLIDER_VALUE) + MINIMUM_SLIDER_VALUE
        )
        self.dioptres_slider.blockSignals(True)
        self.dioptres_dial.blockSignals(True)
        self.dioptres_slider.setValue(slider_value)
        self.dioptres_dial.setValue(slider_value)
        self.dioptres_slider.blockSignals(False)
        self.dioptres_dial.blockSignals(False)
