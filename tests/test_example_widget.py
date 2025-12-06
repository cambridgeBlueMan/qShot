# test_example_widget.py

"""
Automated UI tests for the Example widget using pytest-qt.

This test file verifies:
- That the Example widget's button, when clicked, changes the label text as expected.
- That the camera mode combo box is populated with the correct number of items and expected text
  based on the dummy camera's sensor_modes.

These tests use dummy objects for all dependencies, ensuring the widget can be tested in isolation
without requiring the full application or hardware. The tests are compatible with both PyQt5 and PyQt6.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from components.example_widget import Example
from qt import QtCore, Qt

# Dummy dependencies as in your __main__ block
class DummySignal:
    def connect(self, *args, **kwargs): pass

class DummyConfigModel:
    configChanged = DummySignal()
    def set_nested(self, *args, **kwargs): pass
    def to_dict(self): return {"main": {}}

class DummyControlsModel:
    FrameDurationLimits = (0, 0)

class DummyCam:
    sensor_modes = [
        {"size": (1920, 1080), "format": "RGB", "bit_depth": 8, "fps": 30},
        {"size": (1280, 720), "format": "YUV", "bit_depth": 10, "fps": 60}
    ]
    camera_name = "DummyCam"
    started = False
    def stop(self): pass
    def configure(self, cfg): pass
    def start(self): pass

@pytest.fixture
def test_widget(qtbot):
    widget = Example(
        cam=DummyCam(),
        config_model=DummyConfigModel(),
        controls_model=DummyControlsModel()
    )
    qtbot.addWidget(widget)
    return widget

def test_button_click_changes_label(test_widget, qtbot):
    button = test_widget.button
    label = test_widget.label
    assert label.text() == "This is the Test widget."
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    assert label.text() == "Button clicked!"

def test_camera_mode_combo_populated(test_widget):
    combo = test_widget.camera_mode_combo
    assert combo.count() == 2
    assert "1920" in combo.itemText(0)
    assert "1280" in combo.itemText(1)