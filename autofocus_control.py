from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton, QSlider, QCheckBox, QComboBox
from PyQt6.QtCore import Qt
from base_control_widget import BaseControlWidget

class AutofocusControlWidget(BaseControlWidget):
    """
    A simple autofocus control widget with three radio buttons: Manual, Continuous, Auto,
    a diopter adjustment slider, two option checkboxes, and an AF range combo box.
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

        self.af_trigger = QPushButton("Trigger", self)
        self.af_trigger.clicked.connect(self.trigger_autofocus)
        select_af_mode.addWidget(self.af_trigger)  # Place trigger to the right of auto

        layout.addLayout(select_af_mode)

        # Row: Dioptes label and horizontal slider
        diopter_row = QHBoxLayout()
        diopter_label = QLabel("Dioptes", self)
        diopter_row.addWidget(diopter_label)
        self.diopter_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.diopter_slider.setMinimum(0)
        self.diopter_slider.setMaximum(100)
        self.diopter_slider.setValue(0)
        diopter_row.addWidget(self.diopter_slider)
        layout.addLayout(diopter_row)

        # Row: Fast Autofocus and Use Windows for Af checkboxes
        options_row = QHBoxLayout()
        self.fast_autofocus_checkbox = QCheckBox("Fast Autofocus", self)
        self.fast_autofocus_checkbox.setChecked(True)
        self.use_windows_checkbox = QCheckBox("Use Windows for Af", self)
        options_row.addWidget(self.fast_autofocus_checkbox)
        options_row.addWidget(self.use_windows_checkbox)
        layout.addLayout(options_row)

        # New row: Af Range label and combo box
        af_range_row = QHBoxLayout()
        af_range_label = QLabel("Af Range", self)
        af_range_row.addWidget(af_range_label)
        self.af_range_combo = QComboBox(self)
        self.af_range_combo.addItems(["Normal", "Macro", "Full"])
        af_range_row.addWidget(self.af_range_combo)
        layout.addLayout(af_range_row)
        self.af_range_combo.currentIndexChanged.connect(self.setAfRange)

        self.setLayout(layout)

    def setAfRange(self, index):
        # Example method to handle AF range change
        #print(f"AF Range set to index: {index}")
        # Here you would typically update the camera control model
        self.controls_model.AfRange = index

    def trigger_autofocus(self):
        # Example autofocus logic
        if self.cam and hasattr(self.cam, "autofocus"):
            self.cam.autofocus()
        else:
            print("Autofocus not available on this camera.")