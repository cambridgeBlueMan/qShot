from components.component_base import ComponentBase
from qt import QtWidgets

class SimpleStill(ComponentBase):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        # Add specific UI and logic for still image capture here
        label = QtWidgets.QLabel("Simple Still Capture Component")
        self.base_layout.addWidget(label)