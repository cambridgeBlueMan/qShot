"""
AudioWidget: Qt widget for ALSA audio device and format selection.

This widget provides a user interface for selecting ALSA hardware audio input devices and audio format parameters.
It displays a group box labeled "Audio" containing the following controls, each on its own row:
    - Name: Combo box populated with available ALSA audio input devices.
    - Bit Depth: Combo box for selecting supported bit depths (e.g., 8, 16, 24, 32) for the selected device.
    - Bit Rate: Combo box for selecting bit rate (static options, not ALSA-specific).
    - Sample Rate: Combo box for selecting supported sample rates for the selected device.
    - Audio Sync: Line edit for entering audio sync settings.

Device discovery:
    - The widget lists ALSA hardware capture devices using AudioModel.get_alsa_devices().
    - Bit depth and sample rate combos are populated based on the selected device's capabilities.

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
import logging
logger = logging.getLogger(__name__)

from qt import QtWidgets, QtGui, QtCore, Qt, QIntValidator
from audio_model import AUDIO_CODECS  # Make sure AUDIO_CODECS = ("aac", "mp3", "opus") is defined in audio_model.py


AVAILABL_BIT_RATES = ["64", "128", "192", "256", "320"]  # in kbps
DEFAULT_BIT_RATE = "128"  # in kbps
class AudioWidget(QtWidgets.QDialog):
    def __init__(self, audio_model=None, parent=None, **kwargs):
        super().__init__(parent)
        self.setWindowTitle("Audio Settings")
        if audio_model is None:
            audio_model = kwargs.get("audio_model")
        self.audio_model = audio_model

        group = QtWidgets.QGroupBox("Audio")
        layout = QtWidgets.QVBoxLayout()

        # Name
        name_row = QtWidgets.QHBoxLayout()
        self.name_label = QtWidgets.QLabel("Name")
        self.name_combo = QtWidgets.QComboBox()
        devices = self.audio_model.get_alsa_devices()
        if devices:
            for display_name, device_str in devices:
                self.name_combo.addItem(display_name, device_str)
        else:
            self.name_combo.addItem("No devices found", "")
        name_row.addWidget(self.name_label)
        name_row.addWidget(self.name_combo)
        layout.addLayout(name_row)

        # Bit Depth
        bit_depth_row = QtWidgets.QHBoxLayout()
        self.bit_depth_label = QtWidgets.QLabel("Bit Depth")
        self.bit_depth_combo = QtWidgets.QComboBox()
        bit_depth_row.addWidget(self.bit_depth_label)
        bit_depth_row.addWidget(self.bit_depth_combo)
        layout.addLayout(bit_depth_row)

        # Bit Rate (static, not ALSA-specific)
        bit_rate_row = QtWidgets.QHBoxLayout()
        self.bit_rate_label = QtWidgets.QLabel("Bit Rate")
        self.bit_rate_combo = QtWidgets.QComboBox()
        self.bit_rate_combo.addItems(AVAILABL_BIT_RATES)
        idx = self.bit_rate_combo.findText(DEFAULT_BIT_RATE)
        if idx >= 0:
            self.bit_rate_combo.setCurrentIndex(idx)            
        bit_rate_row.addWidget(self.bit_rate_label)
        bit_rate_row.addWidget(self.bit_rate_combo)
        layout.addLayout(bit_rate_row)

        # Sample Rate
        sample_rate_row = QtWidgets.QHBoxLayout()
        self.sample_rate_label = QtWidgets.QLabel("Sample Rate")
        self.sample_rate_combo = QtWidgets.QComboBox()
        sample_rate_row.addWidget(self.sample_rate_label)
        sample_rate_row.addWidget(self.sample_rate_combo)
        layout.addLayout(sample_rate_row)

        # Audio Sync
        audio_sync_row = QtWidgets.QHBoxLayout()
        self.audio_sync_label = QtWidgets.QLabel("Audio Sync")
        self.audio_sync_edit = QtWidgets.QLineEdit()
        self.audio_sync_edit.setText(self.audio_model.audio_sync)
        self.audio_sync_edit.setValidator(QIntValidator(-1000, 1000, self))
        audio_sync_row.addWidget(self.audio_sync_label)
        audio_sync_row.addWidget(self.audio_sync_edit)
        layout.addLayout(audio_sync_row)

        # --- Audio Codec Row ---
        audio_codec_row = QtWidgets.QHBoxLayout()
        self.audio_codec_label = QtWidgets.QLabel("Audio Codec")
        self.audio_codec_combo = QtWidgets.QComboBox()
        self.audio_codec_combo.addItems(AUDIO_CODECS)
        # Set current index to model's codec if present
        if hasattr(self.audio_model, "audio_codec"):
            idx = self.audio_codec_combo.findText(self.audio_model.audio_codec)
            if idx >= 0:
                self.audio_codec_combo.setCurrentIndex(idx)
        audio_codec_row.addWidget(self.audio_codec_label)
        audio_codec_row.addWidget(self.audio_codec_combo)
        layout.addLayout(audio_codec_row)
        # --- End Audio Codec Row ---

        # Audio is active and mux after record (as checkboxes, before rescan button)
        audio_options_row = QtWidgets.QHBoxLayout()
        self.audio_active = QtWidgets.QCheckBox("Audio is active")
        self.mux_after_record = QtWidgets.QCheckBox("Mux after record")
        audio_options_row.addWidget(self.audio_active)
        audio_options_row.addWidget(self.mux_after_record)
        layout.addLayout(audio_options_row)

        # Rescan Audio button
        rescan_row = QtWidgets.QHBoxLayout()
        self.rescan_audio_button = QtWidgets.QPushButton("Rescan Audio")
        rescan_row.addWidget(self.rescan_audio_button)
        layout.addLayout(rescan_row)

        # Add stretch after all rows
        layout.addStretch()
        group.setLayout(layout)

        # Dialog buttons
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(group)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        # Connect combo box selection to info methods
        self.name_combo.currentIndexChanged.connect(self.on_device_selected)
        self.bit_depth_combo.currentIndexChanged.connect(self.on_bit_depth_selected)
        self.sample_rate_combo.currentIndexChanged.connect(self.on_sample_rate_selected)
        self.rescan_audio_button.clicked.connect(self.on_rescan_audio)
        self.audio_codec_combo.currentIndexChanged.connect(self.on_audio_codec_selected)  # <-- Add this line

        # Optionally connect checkboxes to model
        self.audio_active.stateChanged.connect(self.on_audio_active_changed)
        self.mux_after_record.stateChanged.connect(self.on_mux_after_record_changed)

        # Connect audio sync edit text change to model
        self.audio_sync_edit.textChanged.connect(self.on_audio_sync_changed)
        self.audio_active.setChecked(bool(self.audio_model.audio_active))
        self.mux_after_record.setChecked(self.audio_model.mux_after_record)

        # Populate bit depth and sample rate for initial selection
        self.on_device_selected(self.name_combo.currentIndex())

        # Set default device selection if available
        if self.name_combo.count() > 0:
            self.name_combo.setCurrentIndex(0)
            self.audio_model.name = self.name_combo.itemData(0)

    def accept(self):
        super().accept()

    def reject(self):
        super().reject()

    def on_audio_active_changed(self, state):
        self.audio_model.audio_active = bool(state)
        self.audio_active.setChecked(bool(self.audio_model.audio_active))  # Ensure checkbox reflects model state

    def on_mux_after_record_changed(self, state):
        self.audio_model.mux_after_record = bool(state)

    def on_device_selected(self, idx):
        device_str = self.name_combo.itemData(idx)
        
        print("[AudioWidget] on_device_selected called", device_str)
        self.bit_depth_combo.clear()
        self.sample_rate_combo.clear()
        # --- Update model with selected device ---
        self.audio_model.name = device_str  # <-- Set device_str as the model's name
        self.audio_model.index = idx
        if not device_str:
            return
        bit_depths, sample_rates = self.audio_model.get_alsa_hw_params(device_str)
        self.bit_depth_combo.addItems([str(bd) for bd in bit_depths])
        self.sample_rate_combo.addItems([str(sr) for sr in sample_rates])
        # Optionally, set initial values in the model
        if bit_depths:
            self.audio_model.bit_depth = int(bit_depths[-1])
        if sample_rates:
            self.audio_model.sample_rate = int(sample_rates[-1])
        # Set combo to model's value (which should be the highest)
        if bit_depths:
            idx = self.bit_depth_combo.findText(str(self.audio_model.bit_depth))
            if idx >= 0:
                self.bit_depth_combo.setCurrentIndex(idx)
        if sample_rates:
            idx = self.sample_rate_combo.findText(str(self.audio_model.sample_rate))
            if idx >= 0:
                self.sample_rate_combo.setCurrentIndex(idx)

    def on_bit_depth_selected(self, idx):
        value = self.bit_depth_combo.itemText(idx)
        if value.isdigit():
            self.audio_model.bit_depth = int(value)

    def on_bit_rate_selected(self, idx):
        value = self.bit_rate_combo.itemText(idx)
        if value.isdigit():
            self.audio_model.bit_rate = int(value) * 1000  # Convert to bits/s

    def on_sample_rate_selected(self, idx):
        value = self.sample_rate_combo.itemText(idx)
        if value.isdigit():
            self.audio_model.sample_rate = int(value)

    def on_rescan_audio(self):
        """Rescan ALSA devices and repopulate the device combo box."""
        self.name_combo.clear()
        devices = self.audio_model.get_alsa_devices()
        if devices:
            for display_name, device_str in devices:
                self.name_combo.addItem(display_name, device_str)
            self.audio_active.setChecked(True)
            self.audio_model.audio_active = True
        else:
            self.name_combo.addItem("No devices found", "")
            self.audio_active.setChecked(False)
            self.audio_model.audio_active = False
        # Trigger update for bit depth and sample rate combos
        self.on_device_selected(self.name_combo.currentIndex())

    def on_audio_sync_changed(self, text):
        self.audio_model.audio_sync = text

    def set_audio_active(self, value: bool):
        """Set the model's audio_active property from the checkbox, with diagnostic log."""
        logger.info(f"[AudioWidget] Setting audio_active to {value}")
        self.audio_model.audio_active = value
        self.audio_active.setChecked(value)

    def set_mux_after_record(self, value: bool):
        """Set the model's mux_after_record property from the checkbox, with diagnostic log."""
        logger.info(f"[AudioWidget] Setting mux_after_record to {value}")
        self.audio_model.mux_after_record = value
        self.mux_after_record.setChecked(value)

    def closeEvent(self, event):
        print("AudioWidget closeEvent called")
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"AudioWidget closed. AudioModel: name={self.audio_model.name}, sample_rate={self.audio_model.sample_rate}, bit_rate={self.audio_model.bit_rate}")
        super().closeEvent(event)

    def __del__(self):
        print("AudioWidget __del__ called")

    def on_audio_codec_selected(self, idx):
        value = self.audio_codec_combo.itemText(idx)
        self.audio_model.audio_codec = value
        logger.info(f"[AudioWidget] audio_codec set to {value}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = AudioWidget()
    widget.show()
    sys.exit(app.exec_())