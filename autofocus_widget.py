from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton, QSlider, QCheckBox, QComboBox, QDial, QGroupBox
)
from PyQt6.QtCore import Qt
from base_control_widget import BaseControlWidget

MINIMUM_SLIDER_VALUE = 0
MAXIMUM_SLIDER_VALUE = 100
DIAL_SIZE = 60

class AutofocusWidget(BaseControlWidget):
    """
    AutofocusWidget provides a user interface for controlling camera autofocus and manual focus.

    Layout & Features
    -----------------
    - **Autofocus Mode group box** (bold title): 
        - Three radio buttons: Manual, Continuous, Auto
        - "Trigger" button for autofocus
        - When not in Manual mode, the manual focus controls are disabled.
    - **Manual Focus Control group box** (bold title):
        - Row 1: "Dioptres" label and a horizontal slider for fine manual focus adjustment
        - Row 2: QDial for manual focus, right-aligned, fixed size (DIAL_SIZE)
        - Both controls are enabled only in Manual mode.
    - **Other group box** (bold title):
        - Row 1: "Fast Autofocus" and "Use Windows for Af" checkboxes
        - Row 2: "Af Range" label and combo box (Normal, Macro, Full)
    - A stretch at the end keeps the layout compact when resized.

    Signal/Slot Logic
    -----------------
    - Changing the AF mode enables/disables the manual focus controls.
    - Slider and dial are kept in sync and mapped to a float value (0-100) for the model.
    - Model changes to LensPosition update the slider and dial.
    - All controls are connected to the appropriate model properties.

    Usage
    -----
    Instantiate with a controls_model and cam object. The widget will automatically enable/disable
    manual focus controls based on the selected autofocus mode.
    """

    def init_ui(self):
        layout = QVBoxLayout(self)

        # --- Autofocus Mode group box ---
        af_mode_group = QGroupBox("Autofocus Mode")
        af_mode_group.setStyleSheet("QGroupBox { font-weight: bold; }")
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

        af_mode_group.setLayout(select_af_mode)
        layout.addWidget(af_mode_group)

        # --- Manual Focus Control group box ---
        self.manual_focus_group = QGroupBox("Manual Focus Control")
        #: QGroupBox for manual focus controls.
        #: This is an instance attribute so it can be enabled/disabled
        #: (and have its style changed) in response to autofocus mode changes.
        self.manual_focus_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        manual_focus_layout = QVBoxLayout()

        # Row 1: Dioptres label and horizontal slider
        dioptres_row = QHBoxLayout()
        dioptres_label = QLabel("Dioptres", self)
        dioptres_row.addWidget(dioptres_label)
        self.dioptres_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.dioptres_slider.setMinimum(MINIMUM_SLIDER_VALUE)
        self.dioptres_slider.setMaximum(MAXIMUM_SLIDER_VALUE)
        self.dioptres_slider.setValue(MINIMUM_SLIDER_VALUE)
        self.dioptres_slider.valueChanged.connect(self.setDioptres)
        dioptres_row.addWidget(self.dioptres_slider)
        manual_focus_layout.addLayout(dioptres_row)

        # Row 2: QDial only (right aligned), fixed size from DIAL_SIZE
        dial_row = QHBoxLayout()
        dial_row.addStretch(1)  # Add stretch to push dial to the right
        self.dioptres_dial = QDial(self)
        self.dioptres_dial.setMinimum(MINIMUM_SLIDER_VALUE)
        self.dioptres_dial.setMaximum(MAXIMUM_SLIDER_VALUE)
        self.dioptres_dial.setValue(MINIMUM_SLIDER_VALUE)
        self.dioptres_dial.setFixedSize(DIAL_SIZE, DIAL_SIZE)
        self.dioptres_dial.setWrapping(False)
        self.dioptres_dial.valueChanged.connect(self.setDioptres)
        dial_row.addWidget(self.dioptres_dial)
        manual_focus_layout.addLayout(dial_row)

        self.manual_focus_group.setLayout(manual_focus_layout)
        layout.addWidget(self.manual_focus_group)

        # --- Other controls group box ---
        other_group = QGroupBox("Other")
        other_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        other_layout = QVBoxLayout()

        # Row: Fast Autofocus and Use Windows for Af checkboxes
        options_row = QHBoxLayout()
        self.fast_autofocus_checkbox = QCheckBox("Fast Autofocus", self)
        self.fast_autofocus_checkbox.setChecked(True)
        self.use_windows_checkbox = QCheckBox("Use Windows for Af", self)
        options_row.addWidget(self.fast_autofocus_checkbox)
        options_row.addWidget(self.use_windows_checkbox)
        self.use_windows_checkbox.toggled.connect(self.setAfMetering)
        self.fast_autofocus_checkbox.toggled.connect(self.setAfSpeed)
        other_layout.addLayout(options_row)

        # Row: Af Range label and combo box
        af_range_row = QHBoxLayout()
        af_range_label = QLabel("Af Range", self)
        af_range_row.addWidget(af_range_label)
        self.af_range_combo = QComboBox(self)
        self.af_range_combo.addItems(["Normal", "Macro", "Full"])
        af_range_row.addWidget(self.af_range_combo)
        self.af_range_combo.currentIndexChanged.connect(self.setAfRange)
        other_layout.addLayout(af_range_row)

        other_group.setLayout(other_layout)
        layout.addWidget(other_group)

        # Add stretch at the end to keep group boxes compact on resize
        layout.addStretch(1)

        self.controls_model.LensPositionChanged.connect(self.onLensPositionChanged)
        self.setLayout(layout)

    def setAfRange(self, index):
        """Handle AF range combo box changes."""
        self.controls_model.AfRange = index

    def trigger_autofocus(self):
        """Trigger an autofocus cycle on the camera."""
        self.cam.autofocus_cycle(signal_function=self.on_af_done)

    def on_af_done(self, job):
        """Callback for autofocus completion."""
        success = self.cam.wait(job)
        if success:
            print("Autofocus successful")
        else:
            print("Autofocus failed")

    def on_camera_job_done(self, job):
        """Handle completion of a camera job."""
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
        """
        Handle AF mode changes.
        Disables manual focus controls unless in manual mode (mode == 0).
        Also updates group box title style to be bold only when enabled.
        """
        print(f"AF Mode set to {mode}")
        self.controls_model.AfMode = mode
        manual_enabled = (mode == 0)
        self.manual_focus_group.setEnabled(manual_enabled)
        if manual_enabled:
            self.manual_focus_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        else:
            self.manual_focus_group.setStyleSheet("QGroupBox { font-weight: normal; }")

    def setAfMetering(self, checked):
        """Set AF metering mode based on checkbox."""
        self.controls_model.AfMetering = 1 if checked else 0

    def setAfSpeed(self, checked):
        """Set AF speed based on checkbox."""
        self.controls_model.AfSpeed = 1 if checked else 0

    def setDialValue(self, value):
        """(Placeholder) Set dial value if needed."""
        pass  # Replace with actual logic as needed

    def setDioptres(self, value):
        """
        Map slider/dial value (MINIMUM_SLIDER_VALUE to MAXIMUM_SLIDER_VALUE) to float 0.0 - 100.0,
        and update the model.
        """
        mapped = (
            (value - MINIMUM_SLIDER_VALUE)
            / (MAXIMUM_SLIDER_VALUE - MINIMUM_SLIDER_VALUE)
        ) * 100.0
        self.controls_model.LensPosition = mapped

    def onLensPositionChanged(self, value):
        """
        Update the slider and dial if LensPosition changes elsewhere.
        Expects value in 0-100 range.
        """
        slider_value = int(
            (value / 100.0) * (MAXIMUM_SLIDER_VALUE - MINIMUM_SLIDER_VALUE) + MINIMUM_SLIDER_VALUE
        )
        self.dioptres_slider.blockSignals(True)
        self.dioptres_dial.blockSignals(True)
        self.dioptres_slider.setValue(slider_value)
        self.dioptres_dial.setValue(slider_value)
        self.dioptres_slider.blockSignals(False)
        self.dioptres_dial.blockSignals(False)
