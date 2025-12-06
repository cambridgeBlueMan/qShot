import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from paths_widget import PathsWidget
from qt import QtCore, Key_Return

class DummySignal:
    def connect(self, *args, **kwargs): pass

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

@pytest.fixture
def paths_widget(qtbot):
    widget = PathsWidget(paths_model=DummyPathsModel())
    qtbot.addWidget(widget)
    return widget

def test_img_root_editing_updates_paths_model(paths_widget, qtbot):
    edit = paths_widget.img_root
    edit.setText("new_root")
    qtbot.keyClick(edit, Key_Return)
    assert paths_widget.paths_model.rootnames["img"] == "new_root"

def test_strategy_combo_updates_paths_model(paths_widget, qtbot):
    combo = paths_widget.strategy
    combo.setCurrentIndex(1)  # "sequence"
    assert paths_widget.paths_model.strategy == "sequence"