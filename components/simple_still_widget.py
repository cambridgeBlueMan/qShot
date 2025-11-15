from components.component_base import ComponentBase
from qt import QtWidgets, Qt
from adjustments import AdjustmentsWidget

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

        # Add the button row to the main layout
        self.base_layout.addLayout(button_row)

        # Create the 'Common Controls' group box (invisible by default)
        self.common_controls_group = QtWidgets.QGroupBox("Common Controls")
        self.common_controls_group.setVisible(False)
        group_layout = QtWidgets.QVBoxLayout()

        # Add AdjustmentsWidget to the group box
        self.adjustments_widget = AdjustmentsWidget(self.controls_model, mode="dials")
        group_layout.addWidget(self.adjustments_widget)

        self.common_controls_group.setLayout(group_layout)
        self.base_layout.addWidget(self.common_controls_group)

        self.base_layout.addStretch()  # Add stretch to force buttons/group box to the top

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