from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton
from base_control_widget import BaseControlWidget

class AutofocusControlWidget(BaseControlWidget):
    """
    A simple autofocus control widget with three radio buttons: Manual, Continuous, Auto.
    """
    def init_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("Autofocus Control", self)
        layout.addWidget(label)

        # Horizontal group of radio buttons
        radio_layout = QHBoxLayout()
        self.manual_radio = QRadioButton("Manual", self)
        self.continuous_radio = QRadioButton("Continuous", self)
        self.auto_radio = QRadioButton("Auto", self)
        radio_layout.addWidget(self.manual_radio)
        radio_layout.addWidget(self.continuous_radio)
        radio_layout.addWidget(self.auto_radio)
        layout.addLayout(radio_layout)

        self.af_button = QPushButton("Trigger Autofocus", self)
        self.af_button.clicked.connect(self.trigger_autofocus)
        layout.addWidget(self.af_button)
        self.setLayout(layout)

    def trigger_autofocus(self):
        # Example autofocus logic
        if self.cam and hasattr(self.cam, "autofocus"):
            self.cam.autofocus()
        else:
            print("Autofocus not available on this camera.")