from components.component_base import ComponentBase
from qt import QtWidgets

class SimpleStill(ComponentBase):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        # Create a horizontal layout for the buttons
        button_row = QtWidgets.QHBoxLayout()
        self.capture_button = QtWidgets.QPushButton("Capture")
        button_row.addWidget(self.capture_button)
        self.capture_button.clicked.connect(self.capture_image)

        self.more_button = QtWidgets.QPushButton("more...")
        button_row.addWidget(self.more_button)
        self.more_button.clicked.connect(self.show_more)

        # Add the button row to the main layout
        self.base_layout.addLayout(button_row)
        self.base_layout.addStretch()  # Add stretch to force buttons to the top

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

    def show_more(self):
        print("More... button pressed")
        # Implement additional functionality here