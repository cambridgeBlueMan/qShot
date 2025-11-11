"""
AudioWidget: Qt widget for audio device and format selection.

This widget provides a user interface for selecting audio input devices and audio format parameters.
It displays a group box labeled "Audio" containing the following controls, each on its own row:
    - Name: Combo box populated with available audio input devices (using PipeWire or PulseAudio discovery).
    - Bit Depth: Combo box for selecting bit depth (e.g., 8, 16, 24, 32).
    - Bit Rate: Combo box for selecting bit rate (e.g., 64, 128, 192, 256, 320).
    - Sample Rate: Combo box for selecting sample rate (e.g., 22050, 44100, 48000, 96000).

Device discovery:
    - The widget attempts to discover audio input devices using PipeWire (wpctl) first.
    - If PipeWire discovery fails or finds no devices, it falls back to PulseAudio (pactl).
    - If no devices are found, default options are provided.

Standalone usage:
    - The widget can be run as a standalone application for testing and demonstration.
    - Example: python audio_widget.py

Intended usage:
    - Integrate into larger Qt applications for audio device and format selection.
    - Connect to an AudioModel instance for data binding and signal handling.

Example:
    app = QtWidgets.QApplication(sys.argv)
    widget = AudioWidget()
    widget.show()
    sys.exit(app.exec_())
"""

import sys
from PyQt5 import QtWidgets
from audio_model import AudioModel
import re
import subprocess

class AudioWidget(QtWidgets.QWidget):
    def __init__(self, audio_model=None, parent=None, use_pipewire=True):
        super().__init__(parent)
        self.audio_model = audio_model or AudioModel()
        self.use_pipewire = use_pipewire

        group = QtWidgets.QGroupBox("Audio")
        layout = QtWidgets.QVBoxLayout()

        # Name
        name_row = QtWidgets.QHBoxLayout()
        self.name_label = QtWidgets.QLabel("Name")
        self.name_combo = QtWidgets.QComboBox()
        if use_pipewire:
            devices = self.audio_model.get_pw_sources()
        else:
            devices = self.audio_model.get_pa_sources()
        if devices:
            for name, index in devices:
                display = f"{name} (index {index})"
                self.name_combo.addItem(display, index)
        else:
            self.name_combo.addItem("Default", 0)
        name_row.addWidget(self.name_label)
        name_row.addWidget(self.name_combo)
        layout.addLayout(name_row)

        # Bit Depth
        bit_depth_row = QtWidgets.QHBoxLayout()
        self.bit_depth_label = QtWidgets.QLabel("Bit Depth")
        self.bit_depth_combo = QtWidgets.QComboBox()
        self.bit_depth_combo.addItems(["8", "16", "24", "32"])
        bit_depth_row.addWidget(self.bit_depth_label)
        bit_depth_row.addWidget(self.bit_depth_combo)
        layout.addLayout(bit_depth_row)

        # Bit Rate
        bit_rate_row = QtWidgets.QHBoxLayout()
        self.bit_rate_label = QtWidgets.QLabel("Bit Rate")
        self.bit_rate_combo = QtWidgets.QComboBox()
        self.bit_rate_combo.addItems(["64", "128", "192", "256", "320"])
        bit_rate_row.addWidget(self.bit_rate_label)
        bit_rate_row.addWidget(self.bit_rate_combo)
        layout.addLayout(bit_rate_row)

        # Sample Rate
        sample_rate_row = QtWidgets.QHBoxLayout()
        self.sample_rate_label = QtWidgets.QLabel("Sample Rate")
        self.sample_rate_combo = QtWidgets.QComboBox()
        self.sample_rate_combo.addItems(["22050", "44100", "48000", "96000"])
        sample_rate_row.addWidget(self.sample_rate_label)
        sample_rate_row.addWidget(self.sample_rate_combo)
        layout.addLayout(sample_rate_row)

        group.setLayout(layout)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(group)
        self.setLayout(main_layout)

        # --- Connect combo box selection to info methods ---
        self.name_combo.currentIndexChanged.connect(self.on_device_selected)

    def on_device_selected(self, idx):
        # Get the index stored as user data
        device_index = self.name_combo.itemData(idx)
        if device_index is None:
            return
        if self.use_pipewire:
            info = self.audio_model.get_pw_device_info(device_index)
            print(f"PipeWire device info for index {device_index}:\n{info}")
        else:
            # For PulseAudio/ALSA, you may need to map index to device name
            # Here we just print the index, but you could call get_alsa_hw_params if you store device names
            print(f"PulseAudio/ALSA device index selected: {device_index}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # Pass use_pipewire=False to test PulseAudio logic
    widget = AudioWidget(use_pipewire=False)
    widget.show()
    sys.exit(app.exec_())