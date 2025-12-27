"""
AudioModel for ALSA hardware audio device discovery and format interrogation.

This model provides:
- Listing of ALSA hardware capture devices.
- Querying supported sample rates and bit depths for a selected device.
- Probing for supported sample rates using common values.
- Property setters with signal emission and print diagnostics.
"""

from qt import QObject, pyqtSignal
import subprocess
import re
import logging

logger = logging.getLogger("audio_model")

DEFAULT_AUDIO_SYNC = "0"  # in milliseconds
AUDIO_CODECS = ("aac", "mp3", "libopus")

class AudioModel(QObject):
    """
    Qt-based model for audio device and format selection using ALSA.
    Provides properties for device name, index, bit depth, bit rate, and sample rate,
    with signals emitted on change and print diagnostics for debugging.
    """

    nameChanged = pyqtSignal(str)
    indexChanged = pyqtSignal(int)
    bitDepthChanged = pyqtSignal(int)
    bitRateChanged = pyqtSignal(int)
    sampleRateChanged = pyqtSignal(int)
    audioActiveChanged = pyqtSignal(bool)
    muxAfterRecordChanged = pyqtSignal(bool)
    audioSyncChanged = pyqtSignal(str)

    def __init__(self, name="", index=0, bit_depth=16, bit_rate=128000, sample_rate=44100,
                 audio_sync=DEFAULT_AUDIO_SYNC, audio_active=False, mux_after_record=False, audio_codec="aac"):
        """
        Initialize the AudioModel with default or provided values.
        If ALSA devices are available, populate model properties from the first device.
        """
        super().__init__()
        self._name = name
        self._index = index
        self._bit_depth = bit_depth
        self._bit_rate = bit_rate
        self._sample_rate = sample_rate
        self._audio_sync = audio_sync
        self._audio_active = audio_active
        self._mux_after_record = mux_after_record
        self._audio_codec = audio_codec  # <-- Add this line

        self.init_from_first_device()  # <-- Initialize from first ALSA device if available

    def init_from_first_device(self):
        """Initialize model properties from the first available ALSA device."""
        devices = self.get_alsa_devices()
        if devices:
            display_name, device_str = devices[0]
            self.name = device_str
            self.index = 0
            bit_depths, sample_rates = self.get_alsa_hw_params(device_str)
            if bit_depths:
                self.bit_depth = int(bit_depths[-1])  # Highest
            if sample_rates:
                self.sample_rate = int(sample_rates[-1])  # Highest
            self.bit_rate = 128666  # Set to default or adjust as needed
            self.audio_active = True  # <-- Ensure audio is active if a device is found
            logger.info(f"[AudioModel] Initialized from device: {device_str}")
        else:
            self.audio_active = False  # <-- Set to False if no device found
            logger.warning("[AudioModel] No ALSA devices found during initialization.")

    @property
    def name(self):
        """Current device name."""
        return self._name

    @name.setter
    def name(self, value):
        """Set device name and emit signal if changed."""
        if value != self._name:
            self._name = value
            print(f"[AudioModel] name set to {value}")
            self.nameChanged.emit(value)

    @property
    def index(self):
        """Current device index."""
        return self._index

    @index.setter
    def index(self, value):
        """Set device index and emit signal if changed."""
        if value != self._index:
            self._index = value
            self.indexChanged.emit(value)

    @property
    def bit_depth(self):
        """Current bit depth."""
        return self._bit_depth

    @bit_depth.setter
    def bit_depth(self, value):
        """Set bit depth, emit signal, and print diagnostic if changed."""
        if value != self._bit_depth:
            logger.info(f"[AudioModel] bit_depth set to {value}")
            self._bit_depth = value
            self.bitDepthChanged.emit(value)

    @property
    def bit_rate(self):
        """Current bit rate."""
        return self._bit_rate

    @bit_rate.setter
    def bit_rate(self, value):
        """Set bit rate and emit signal if changed."""
        if value != self._bit_rate:
            self._bit_rate = value
            self.bitRateChanged.emit(value)

    @property
    def sample_rate(self):
        """Current sample rate."""
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        """Set sample rate, emit signal, and print diagnostic if changed."""
        if value != self._sample_rate:
            logger.info(f"[AudioModel] sample_rate set to {value}")
            self._sample_rate = value
            self.sampleRateChanged.emit(value)

    @property
    def audio_active(self):
        """Audio is active (checkbox)."""
        return self._audio_active

    @audio_active.setter
    def audio_active(self, value):
        """Set audio active state and emit signal if changed."""
        if value != self._audio_active:
            logger.info(f"[AudioModel] audio_active set to {value}")
            self._audio_active = value
            self.audioActiveChanged.emit(value)

    @property
    def mux_after_record(self):
        """Mux after record (checkbox)."""
        return self._mux_after_record

    @mux_after_record.setter
    def mux_after_record(self, value):
        """Set mux after record state and emit signal if changed."""
        if value != self._mux_after_record:
            logger.info(f"[AudioModel] mux_after_record set to {value}")
            self._mux_after_record = value
            self.muxAfterRecordChanged.emit(value)

    @property
    def audio_sync(self):
        """Audio sync value from line edit."""
        return self._audio_sync

    @audio_sync.setter
    def audio_sync(self, value):
        """Set audio sync value and emit signal if changed. Constrain to -1000..1000."""
        try:
            int_value = int(value)
            if -1000 <= int_value <= 1000:
                if value != self._audio_sync:
                    self._audio_sync = str(int_value)
                    self.audioSyncChanged.emit(self._audio_sync)
            else:
                logger.warning(f"[AudioModel] audio_sync value {value} out of range (-1000 to 1000)")
        except ValueError:
            logger.warning(f"[AudioModel] audio_sync value {value} is not an integer")

    @property
    def audio_codec(self):
        """Current audio codec (default: 'aac')."""
        return self._audio_codec

    @audio_codec.setter
    def audio_codec(self, value):
        """Set audio codec."""
        if value != self._audio_codec:
            self._audio_codec = value
            logger.info(f"[AudioModel] audio_codec set to {value}")

    def get_alsa_devices(self):
        """
        List ALSA hardware capture devices.

        Returns:
            List of (display_name, device_string) tuples for available devices.
        """
        devices = []
        try:
            result = subprocess.run(
                ["arecord", "-l"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2
            )
            for line in result.stdout.splitlines():
                # Updated regex: allow spaces in card/device IDs and names
                match = re.match(r"card (\d+): ([^\[]+) \[([^\]]+)\], device (\d+): ([^\[]+) \[([^\]]+)\]", line)
                if match:
                    card_num = match.group(1)
                    card_id = match.group(2).strip()
                    card_name = match.group(3).strip()
                    device_num = match.group(4)
                    device_id = match.group(5).strip()
                    device_name = match.group(6).strip()
                    device_str = f"hw:{card_num},{device_num}"
                    display_name = f"{device_str} - {card_name} {device_name}"
                    devices.append((display_name, device_str))
        except Exception as e:
            logger.error(f"ALSA device listing error: {e}")
        return devices

    def probe_supported_sample_rates(self, device_str):
        """
        Probe the ALSA device for supported sample rates by attempting to open it at each common rate.

        Args:
            device_str: ALSA device string (e.g., 'hw:0,0')

        Returns:
            List of supported sample rates as strings.
        """
        common_rates = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 176400, 192000]
        supported = []
        for rate in common_rates:
            try:
                result = subprocess.run(
                    ["arecord", "-D", device_str, "-r", str(rate), "-d", "1", "-f", "S16_LE", "--dump-hw-params"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=2
                )
                # Check if the device accepted the rate
                output = result.stdout + "\n" + result.stderr
                if f"RATE: [{rate} {rate}]" in output or f"RATE: [{rate}]" in output:
                    supported.append(str(rate))
            except Exception:
                continue
        return supported

    def get_alsa_hw_params(self, device_str):
        """
        Query supported bit depths and sample rates for the given ALSA device string.

        Args:
            device_str: ALSA device string (e.g., 'hw:0,0')

        Returns:
            Tuple (bit_depths, sample_rates):
                bit_depths: sorted list of supported bit depths as strings
                sample_rates: sorted list of supported sample rates as strings
        """
        bit_depths = set()
        sample_rates = set()
        try:
            result = subprocess.run(
                ["arecord", "--dump-hw-params", "-D", device_str],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2
            )
            output = result.stdout + "\n" + result.stderr
            rate_min, rate_max = None, None
            for line in output.splitlines():
                if line.startswith("FORMAT:"):
                    logger.debug(f"DIAGNOSTIC: FORMAT line: {line}")
                    # Split formats and map to bit depths
                    formats = line.replace("FORMAT:", "").strip().split()
                    for fmt in formats:
                        if fmt == "S8":
                            bit_depths.add("8")
                        elif fmt == "S16_LE":
                            bit_depths.add("16")
                        elif fmt == "S24_LE":
                            bit_depths.add("24")
                        elif fmt == "S32_LE":
                            bit_depths.add("32")
                elif line.startswith("SAMPLE_BITS:"):
                    bits = re.findall(r"\d+", line)
                    for b in bits:
                        bit_depths.add(b)
                elif line.startswith("RATE:"):
                    rates = re.findall(r"\[(\d+)\s+(\d+)\]", line)
                    if rates:
                        rate_min, rate_max = map(int, rates[0])
            # Offer common rates within the reported rate
            common_rates = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 176400, 192000]
            if rate_min and rate_max:
                for r in common_rates:
                    if rate_min <= r <= rate_max:
                        sample_rates.add(r)
        except Exception as e:
            logger.error(f"ALSA hw params error: {e}")
        return sorted(bit_depths, key=int), [str(sr) for sr in sorted(sample_rates)]