"""
AudioModel and audio device discovery utilities.

This module provides:
- The AudioModel class, a Qt-based data model for audio device and format selection.
- Methods for discovering available audio input devices using PipeWire (wpctl) or PulseAudio (pactl).
"""

from PyQt5.QtCore import QObject, pyqtSignal
import subprocess
import re
from io import StringIO

class AudioModel(QObject):
    nameChanged = pyqtSignal(str)
    indexChanged = pyqtSignal(int)
    bitDepthChanged = pyqtSignal(int)
    bitRateChanged = pyqtSignal(int)
    sampleRateChanged = pyqtSignal(int)

    def __init__(self, name="", index=0, bit_depth=16, bit_rate=128, sample_rate=44100):
        super().__init__()
        self._name = name
        self._index = index
        self._bit_depth = bit_depth
        self._bit_rate = bit_rate
        self._sample_rate = sample_rate

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value != self._name:
            self._name = value
            self.nameChanged.emit(value)

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        if value != self._index:
            self._index = value
            self.indexChanged.emit(value)

    @property
    def bit_depth(self):
        return self._bit_depth

    @bit_depth.setter
    def bit_depth(self, value):
        if value != self._bit_depth:
            self._bit_depth = value
            self.bitDepthChanged.emit(value)

    @property
    def bit_rate(self):
        return self._bit_rate

    @bit_rate.setter
    def bit_rate(self, value):
        if value != self._bit_rate:
            self._bit_rate = value
            self.bitRateChanged.emit(value)

    @property
    def sample_rate(self):
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        if value != self._sample_rate:
            self._sample_rate = value
            self.sampleRateChanged.emit(value)

    def get_pipewire_devices(self):
        """
        Discover audio input devices using PipeWire (wpctl).
        Returns a list of (name, index) tuples from the Audio/Devices section.
        """
        devices = []
        try:
            result = subprocess.run(
                ["wpctl", "status"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2
            )
            lines = result.stdout.splitlines()
            in_audio = False
            in_devices = False
            for line in lines:
                line = line.rstrip()
                if line.startswith("Audio"):
                    in_audio = True
                    continue
                if in_audio and "Devices:" in line:
                    in_devices = True
                    continue
                if in_devices and (not line.startswith(" │") or "Clients" in line or "Sinks:" in line or "Sink endpoints:" in line or "Sources:" in line):
                    break
                if in_devices and line.startswith(" │"):
                    # Example: " │     108. Focusrite Scarlett 2i2 2nd Gen      [alsa]"
                    match = re.match(r"^\s*│\s*(\d+)\.\s*(.+?)\s*\[.*\]$", line)
                    if match:
                        index = int(match.group(1))
                        name = match.group(2).strip()
                        devices.append((name, index))
        except Exception as e:
            print(f"PipeWire (wpctl) error: {e}")
        return devices

    def get_pulseaudio_sources(self):
        """
        Return a list of user-friendly names for input devices (sources) using PulseAudio (pactl).
        """
        devices = []
        try:
            result = subprocess.run(
                ["pactl", "list", "sources"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                lines = result.stdout.splitlines()
                name, description = None, None
                for line in lines:
                    line = line.strip()
                    if line.startswith("Name:"):
                        name = line.split(":", 1)[1].strip()
                    elif line.startswith("Description:"):
                        description = line.split(":", 1)[1].strip()
                    elif line == "":
                        if name and description:
                            devices.append(description)
                        name, description = None, None
        except Exception as e:
            print(f"PulseAudio (pactl) error: {e}")
        return devices

    def get_usb_sound_devices(self):
        """
        Returns a list of [card_name, source_index] for USB audio sources found via pactl.
        Only sources with 'alsa.name = "USB Audio"' are included.
        """
        devices = []
        try:
            result = subprocess.run(
                ["pactl", "list", "sources"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2
            )
            lines = result.stdout.splitlines()
            current = {}
            for line in lines:
                line = line.strip()
                if line.startswith("Source #"):
                    # Save previous device if it's USB
                    if current.get("gotOne") and "cardName" in current and "source" in current:
                        devices.append([current["cardName"], current["source"]])
                    # Start new device
                    current = {"source": int(line.split("#")[1]), "gotOne": False}
                elif 'alsa.name = "USB Audio"' in line:
                    current["gotOne"] = True
                elif line.startswith("alsa.card_name ="):
                    # Remove quotes and whitespace
                    card_name = line.split("=", 1)[1].strip().replace('"', '').replace("'", "")
                    current["cardName"] = card_name
            # Check last device
            if current.get("gotOne") and "cardName" in current and "source" in current:
                devices.append([current["cardName"], current["source"]])
        except Exception as e:
            print(f"Error querying USB sound devices: {e}")
        return devices

    def get_pw_sources(self):
        """
        Discover audio input sources using PipeWire (wpctl).
        Returns a list of (name, index) tuples from the Audio/Sources section.
        """
        devices = []
        try:
            result = subprocess.run(
                ["wpctl", "status"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2
            )
            lines = result.stdout.splitlines()
            in_sources = False
            for line in lines:
                line = line.rstrip()
                if line.startswith("├─ Sources:"):
                    in_sources = True
                    continue
                if in_sources:
                    if not line.startswith(" │") or "Source endpoints:" in line or "Streams:" in line:
                        break
                    match = re.match(r"^\s*│\s*\*?\s*(\d+)\.\s*(.+?)\s*\[.*\]$", line)
                    if match:
                        index = int(match.group(1))
                        name = match.group(2).strip()
                        devices.append((name, index))
        except Exception as e:
            print(f"PipeWire (wpctl) error: {e}")
        return devices

    def get_pa_sources(self):
        """
        Discover PulseAudio input sources using pactl.
        Returns a list of (card_name, source_index) tuples for sources with 'alsa.card_name'.
        Only sources with 'alsa.name = "USB Audio"' are included.
        """
        devices = []
        try:
            result = subprocess.run(
                ["pactl", "list", "sources"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2
            )
            lines = result.stdout.splitlines()
            current = {}
            for line in lines:
                line = line.strip()
                if line.startswith("Source #"):
                    if current.get("gotOne") and "cardName" in current and "source" in current:
                        name = current["cardName"]
                        index = current["source"]
                        devices.append((name, index))
                    current = {"source": int(line.split("#")[1]), "gotOne": False}
                elif 'alsa.name = "USB Audio"' in line:
                    current["gotOne"] = True
                elif line.startswith("alsa.card_name ="):
                    card_name = line.split("=", 1)[1].strip().replace('"', '').replace("'", "")
                    current["cardName"] = card_name
            if current.get("gotOne") and "cardName" in current and "source" in current:
                name = current["cardName"]
                index = current["source"]
                devices.append((name, index))
        except Exception as e:
            print(f"PulseAudio (pactl) error: {e}")
        return devices