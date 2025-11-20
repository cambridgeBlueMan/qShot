import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from components.simple_still_widget import SimpleStill

try:
    from PyQt6 import QtCore
except ImportError:
    from PyQt5 import QtCore

class DummySignal:
    def connect(self, *args, **kwargs): pass

class DummyConfigModel:
    def __init__(self):
        self._config = {"main": {"size": (1920, 1080)}}
        self._control_ranges = {"JpegQuality": (1, 100)}
        self.JpegQuality = 75
        self.AeEnable = True
        self.JpegQualityChanged = DummySignal()
        self.AeEnableChanged = DummySignal()
        self.configChanged = DummySignal()
    def set_nested(self, *args, **kwargs):
        if args[-2] == "size":
            self._config["main"]["size"] = args[-1]
        elif args[-2] == "output_size":
            self._config["main"]["size"] = args[-1]
    def to_dict(self):
        return self._config

class DummyControlsModel:
    _control_ranges = {"JpegQuality": (1, 100)}
    JpegQuality = 75
    AeEnable = True
    JpegQualityChanged = DummySignal()
    AeEnableChanged = DummySignal()

class DummyPathsModel:
    still_folder = "/tmp/stills"
    video_folder = "/tmp/videos"
    rootnames = {"img": "img_"}
    strategy = "date"
    def set_rootname(self, kind, name):
        self.rootnames[kind] = name
    def set_strategy(self, strategy):
        self.strategy = strategy
    def generate_filename(self, kind):
        return f"{self.rootnames.get(kind, 'img_')}_test.jpg"
    def set_still_folder(self, folder):
        self.still_folder = folder
    def set_video_folder(self, folder):
        self.video_folder = folder
    pathsChanged = DummySignal()

class DummyCam:
    sensor_modes = [
        {"size": (1920, 1080), "format": "RGB", "bit_depth": 8, "fps": 30},
        {"size": (1280, 720), "format": "YUV", "bit_depth": 10, "fps": 60}
    ]
    camera_name = "DummyCam"
    started = False
    options = {}
    def stop(self): pass
    def configure(self, cfg): pass
    def start(self): pass

@pytest.fixture
def simple_still_widget(qtbot):
    widget = SimpleStill(
        cam=DummyCam(),
        config_model=DummyConfigModel(),
        controls_model=DummyControlsModel(),
        paths_model=DummyPathsModel()
    )
    qtbot.addWidget(widget)
    return widget

def test_jpeg_slider_changes_value(simple_still_widget, qtbot):
    slider = simple_still_widget.jpeg_slider
    slider.setValue(85)
    assert simple_still_widget.controls_model.JpegQuality == 85
    assert simple_still_widget.jpeg_value_label.text() == "85"

def test_res_combo_changes_config_model(simple_still_widget, qtbot):
    combo = simple_still_widget.res_combo
    combo.setCurrentIndex(0)
    size = combo.itemData(0)
    assert simple_still_widget.config_model._config["main"]["size"] == size

def test_img_root_editing_updates_paths_model(paths_widget, qtbot):
    edit = paths_widget.img_root
    edit.setText("new_root")
    qtbot.keyClick(edit, Qt.Key_Return)
    assert paths_widget.paths_model.rootnames["img"] == "new_root"