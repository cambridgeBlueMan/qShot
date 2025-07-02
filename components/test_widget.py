import logging
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton
from ai_file_manager_base import AIFileManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='a'
)

"""
test_widget.py

This module defines the Test component for the application. The Test class inherits from AIFileManager
and is intended as a minimal, self-contained example for experimentation, documentation, and understanding
of how to build components that integrate with the application's file management infrastructure.

The Test widget demonstrates:
- How to inherit from AIFileManager to get dataset/class label management UI for free.
- How to add custom widgets (like labels and buttons) to the base layout.
- How to implement required abstract methods from the base class.
- How to use logging and simple event handling.

This file is intended as a living example and playground for gradually building up and documenting
component development best practices in this codebase.
"""

class Test(AIFileManager):
    """
    A simple test component that inherits from AIFileManager.
    Demonstrates adding custom UI elements to the base file manager interface.
    """

    def __init__(self, parent=None, settings_group=None, **kwargs):
        super().__init__(parent=parent, settings_group=settings_group)
        # Add a label and a button to the base layout
        self.label = QLabel("This is the Test widget.")
        self.base_layout.addWidget(self.label)

        self.button = QPushButton("Click Me")
        self.button.clicked.connect(self.on_button_clicked)
        self.base_layout.addWidget(self.button)

        self.setLayout(self.base_layout)

    def on_button_clicked(self):
        self.label.setText("Button clicked!")
        logging.info("Test widget button was clicked.")

    def get_new_file_path(self):
        # Implement the abstract method from AIFileManager
        return "test_file.txt"