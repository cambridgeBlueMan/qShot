"""
camera_controls_model.py
-----------------------
This module defines the CameraControlsModel class, which acts as the central data model for live camera controls in a PyQt6 GUI application using the Picamera2 library.

CameraControlsModel encapsulates all camera controls (brightness, contrast, sharpness, etc.) and provides methods to generate Picamera2 configuration objects for preview, still, and video capture scenarios. It is a QObject, emitting signals when properties change, enabling robust two-way data binding with the GUI.

Typical usage:
    controls = ControlsModel()
    controls.Contrast = 1.0
    preview_cfg = controls.to_preview_config(picam2)

Signals can be connected to GUI widgets to update the interface when the model changes, and vice versa.
"""

from picamera2 import Picamera2
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Tuple, Optional

class ControlsModel(QObject):
    resolutionChanged = pyqtSignal(tuple)
    formatChanged = pyqtSignal(str)
    AeExposureModeChanged = pyqtSignal(int)
    ContrastChanged = pyqtSignal(float)
    AeConstraintModeChanged = pyqtSignal(int)
    ExposureTimeModeChanged = pyqtSignal(int)
    HdrModeChanged = pyqtSignal(int)
    AeMeteringModeChanged = pyqtSignal(int)
    AeFlickerPeriodChanged = pyqtSignal(int)
    AnalogueGainModeChanged = pyqtSignal(int)
    AnalogueGainChanged = pyqtSignal(float)
    StatsOutputEnableChanged = pyqtSignal(bool)
    BrightnessChanged = pyqtSignal(float)
    SyncFramesChanged = pyqtSignal(int)
    ExposureTimeChanged = pyqtSignal(int)
    AeFlickerModeChanged = pyqtSignal(int)
    SyncModeChanged = pyqtSignal(int)
    AwbEnableChanged = pyqtSignal(bool)
    ColourGainsChanged = pyqtSignal(tuple)
    AwbModeChanged = pyqtSignal(int)
    ScalerCropsChanged = pyqtSignal(tuple)
    ColourTemperatureChanged = pyqtSignal(int)
    SaturationChanged = pyqtSignal(float)
    CnnEnableInputTensorChanged = pyqtSignal(bool)
    FrameDurationLimitsChanged = pyqtSignal(int)
    ScalerCropChanged = pyqtSignal(tuple)
    NoiseReductionModeChanged = pyqtSignal(int)
    SharpnessChanged = pyqtSignal(float)
    AeEnableChanged = pyqtSignal(bool)
    ExposureValueChanged = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self._AeExposureMode = 0
        self._Contrast = 1.0
        self._AeConstraintMode = 0
        self._ExposureTimeMode = 0
        self._HdrMode = 0
        self._AeMeteringMode = 0
        self._AeFlickerPeriod = None
        self._AnalogueGainMode = 0
        self._AnalogueGain = 1.0
        self._StatsOutputEnable = False
        self._Brightness = 0.0
        self._SyncFrames = 100
        self._ExposureTime = 20000
        self._AeFlickerMode = 0
        self._SyncMode = 0
        self._AwbEnable = None
        self._ColourGains = None
        self._AwbMode = 0
        self._ScalerCrops = None
        self._ColourTemperature = None
        self._Saturation = 1.0
        self._CnnEnableInputTensor = False
        self._FrameDurationLimits = 33333
        self._ScalerCrop = None
        self._NoiseReductionMode = 0
        self._Sharpness = 1.0
        self._AeEnable = True
        self._ExposureValue = 0.0

    @property
    def Resolution(self) -> Tuple[int, int]:
        """Get the camera resolution as a (width, height) tuple."""
        return self._ScalerCrop

    @Resolution.setter
    def Resolution(self, value: Tuple[int, int]):
        """Set the camera resolution, emitting the resolutionChanged signal."""
        if value != self._ScalerCrop:
            self._ScalerCrop = value
            self.resolutionChanged.emit(value)

    @property
    def Format(self) -> str:
        """Get the current image format."""
        return "RGB888"

    @Format.setter
    def Format(self, value: str):
        """Set the image format, emitting the formatChanged signal."""
        if value != "RGB888":
            self.formatChanged.emit(value)

    @property
    def AeExposureMode(self) -> int:
        """Get the auto exposure mode."""
        return self._AeExposureMode

    @AeExposureMode.setter
    def AeExposureMode(self, value: int):
        """Set the auto exposure mode, emitting the AeExposureModeChanged signal."""
        if value != self._AeExposureMode:
            self._AeExposureMode = value
            self.AeExposureModeChanged.emit(value)

    @property
    def Contrast(self) -> float:
        """Get the contrast value."""
        return self._Contrast

    @Contrast.setter
    def Contrast(self, value: float):
        """Set the contrast value, emitting the ContrastChanged signal."""
        if value != self._Contrast:
            self._Contrast = value
            self.ContrastChanged.emit(value)

    @property
    def AeConstraintMode(self) -> int:
        """Get the AE constraint mode."""
        return self._AeConstraintMode

    @AeConstraintMode.setter
    def AeConstraintMode(self, value: int):
        """Set the AE constraint mode, emitting the AeConstraintModeChanged signal."""
        if value != self._AeConstraintMode:
            self._AeConstraintMode = value
            self.AeConstraintModeChanged.emit(value)

    @property
    def ExposureTimeMode(self) -> int:
        """Get the exposure time mode."""
        return self._ExposureTimeMode

    @ExposureTimeMode.setter
    def ExposureTimeMode(self, value: int):
        """Set the exposure time mode, emitting the ExposureTimeModeChanged signal."""
        if value != self._ExposureTimeMode:
            self._ExposureTimeMode = value
            self.ExposureTimeModeChanged.emit(value)

    @property
    def HdrMode(self) -> int:
        """Get the HDR mode."""
        return self._HdrMode

    @HdrMode.setter
    def HdrMode(self, value: int):
        """Set the HDR mode, emitting the HdrModeChanged signal."""
        if value != self._HdrMode:
            self._HdrMode = value
            self.HdrModeChanged.emit(value)

    @property
    def AeMeteringMode(self) -> int:
        """Get the AE metering mode."""
        return self._AeMeteringMode

    @AeMeteringMode.setter
    def AeMeteringMode(self, value: int):
        """Set the AE metering mode, emitting the AeMeteringModeChanged signal."""
        if value != self._AeMeteringMode:
            self._AeMeteringMode = value
            self.AeMeteringModeChanged.emit(value)

    @property
    def AeFlickerPeriod(self) -> Optional[int]:
        """Get the AE flicker period in microseconds, or None if not set."""
        return self._AeFlickerPeriod

    @AeFlickerPeriod.setter
    def AeFlickerPeriod(self, value: Optional[int]):
        """Set the AE flicker period, emitting the AeFlickerPeriodChanged signal."""
        if value != self._AeFlickerPeriod:
            self._AeFlickerPeriod = value
            self.AeFlickerPeriodChanged.emit(value)

    @property
    def AnalogueGainMode(self) -> int:
        """Get the analogue gain mode."""
        return self._AnalogueGainMode

    @AnalogueGainMode.setter
    def AnalogueGainMode(self, value: int):
        """Set the analogue gain mode, emitting the AnalogueGainModeChanged signal."""
        if value != self._AnalogueGainMode:
            self._AnalogueGainMode = value
            self.AnalogueGainModeChanged.emit(value)

    @property
    def AnalogueGain(self) -> float:
        """Get the analogue gain value."""
        return self._AnalogueGain

    @AnalogueGain.setter
    def AnalogueGain(self, value: float):
        """Set the analogue gain value, emitting the AnalogueGainChanged signal."""
        if value != self._AnalogueGain:
            self._AnalogueGain = value
            self.AnalogueGainChanged.emit(value)

    @property
    def StatsOutputEnable(self) -> bool:
        """Check if stats output is enabled."""
        return self._StatsOutputEnable

    @StatsOutputEnable.setter
    def StatsOutputEnable(self, value: bool):
        """Enable or disable stats output, emitting the StatsOutputEnableChanged signal."""
        if value != self._StatsOutputEnable:
            self._StatsOutputEnable = value
            self.StatsOutputEnableChanged.emit(value)

    @property
    def Brightness(self) -> float:
        """Get the brightness value."""
        return self._Brightness

    @Brightness.setter
    def Brightness(self, value: float):
        """Set the brightness value, emitting the BrightnessChanged signal."""
        if value != self._Brightness:
            self._Brightness = value
            self.BrightnessChanged.emit(value)

    @property
    def SyncFrames(self) -> int:
        """Get the number of frames to sync."""
        return self._SyncFrames

    @SyncFrames.setter
    def SyncFrames(self, value: int):
        """Set the number of frames to sync, emitting the SyncFramesChanged signal."""
        if value != self._SyncFrames:
            self._SyncFrames = value
            self.SyncFramesChanged.emit(value)

    @property
    def ExposureTime(self) -> int:
        """Get the exposure time in microseconds."""
        return self._ExposureTime

    @ExposureTime.setter
    def ExposureTime(self, value: int):
        """Set the exposure time, emitting the ExposureTimeChanged signal."""
        if value != self._ExposureTime:
            self._ExposureTime = value
            self.ExposureTimeChanged.emit(value)

    @property
    def AeFlickerMode(self) -> int:
        """Get the AE flicker mode."""
        return self._AeFlickerMode

    @AeFlickerMode.setter
    def AeFlickerMode(self, value: int):
        """Set the AE flicker mode, emitting the AeFlickerModeChanged signal."""
        if value != self._AeFlickerMode:
            self._AeFlickerMode = value
            self.AeFlickerModeChanged.emit(value)

    @property
    def SyncMode(self) -> int:
        """Get the sync mode."""
        return self._SyncMode

    @SyncMode.setter
    def SyncMode(self, value: int):
        """Set the sync mode, emitting the SyncModeChanged signal."""
        if value != self._SyncMode:
            self._SyncMode = value
            self.SyncModeChanged.emit(value)

    @property
    def AwbEnable(self) -> Optional[bool]:
        """Check if AWB is enabled."""
        return self._AwbEnable

    @AwbEnable.setter
    def AwbEnable(self, value: Optional[bool]):
        """Enable or disable AWB, emitting the AwbEnableChanged signal."""
        if value != self._AwbEnable:
            self._AwbEnable = value
            self.AwbEnableChanged.emit(value)

    @property
    def ColourGains(self) -> Optional[Tuple[float, float]]:
        """Get the colour gains as a (r_gain, b_gain) tuple."""
        return self._ColourGains

    @ColourGains.setter
    def ColourGains(self, value: Optional[Tuple[float, float]]):
        """Set the colour gains, emitting the ColourGainsChanged signal."""
        if value != self._ColourGains:
            self._ColourGains = value
            self.ColourGainsChanged.emit(value)

    @property
    def AwbMode(self) -> int:
        """Get the AWB mode."""
        return self._AwbMode

    @AwbMode.setter
    def AwbMode(self, value: int):
        """Set the AWB mode, emitting the AwbModeChanged signal."""
        if value != self._AwbMode:
            self._AwbMode = value
            self.AwbModeChanged.emit(value)

    @property
    def ScalerCrops(self) -> Optional[Tuple[int, int, int, int]]:
        """Get the scaler crops as a (top, right, bottom, left) tuple."""
        return self._ScalerCrops

    @ScalerCrops.setter
    def ScalerCrops(self, value: Optional[Tuple[int, int, int, int]]):
        """Set the scaler crops, emitting the ScalerCropsChanged signal."""
        if value != self._ScalerCrops:
            self._ScalerCrops = value
            self.ScalerCropsChanged.emit(value)

    @property
    def ColourTemperature(self) -> Optional[int]:
        """Get the colour temperature in Kelvin, or None if not set."""
        return self._ColourTemperature

    @ColourTemperature.setter
    def ColourTemperature(self, value: Optional[int]):
        """Set the colour temperature, emitting the ColourTemperatureChanged signal."""
        if value != self._ColourTemperature:
            self._ColourTemperature = value
            self.ColourTemperatureChanged.emit(value)

    @property
    def Saturation(self) -> float:
        """Get the saturation value."""
        return self._Saturation

    @Saturation.setter
    def Saturation(self, value: float):
        """Set the saturation value, emitting the SaturationChanged signal."""
        if value != self._Saturation:
            self._Saturation = value
            self.SaturationChanged.emit(value)

    @property
    def CnnEnableInputTensor(self) -> bool:
        """Check if CNN input tensor is enabled."""
        return self._CnnEnableInputTensor

    @CnnEnableInputTensor.setter
    def CnnEnableInputTensor(self, value: bool):
        """Enable or disable CNN input tensor, emitting the CnnEnableInputTensorChanged signal."""
        if value != self._CnnEnableInputTensor:
            self._CnnEnableInputTensor = value
            self.CnnEnableInputTensorChanged.emit(value)

    @property
    def FrameDurationLimits(self) -> int:
        """Get the frame duration limits in microseconds."""
        return self._FrameDurationLimits

    @FrameDurationLimits.setter
    def FrameDurationLimits(self, value: int):
        """Set the frame duration limits, emitting the FrameDurationLimitsChanged signal."""
        if value != self._FrameDurationLimits:
            self._FrameDurationLimits = value
            self.FrameDurationLimitsChanged.emit(value)

    @property
    def ScalerCrop(self) -> Optional[Tuple[int, int, int, int]]:
        """Get the scaler crop as a (top, right, bottom, left) tuple, or None if not set."""
        return self._ScalerCrop

    @ScalerCrop.setter
    def ScalerCrop(self, value: Optional[Tuple[int, int, int, int]]):
        """Set the scaler crop, emitting the ScalerCropChanged signal."""
        if value != self._ScalerCrop:
            self._ScalerCrop = value
            self.ScalerCropChanged.emit(value)

    @property
    def NoiseReductionMode(self) -> int:
        """Get the noise reduction mode."""
        return self._NoiseReductionMode

    @NoiseReductionMode.setter
    def NoiseReductionMode(self, value: int):
        """Set the noise reduction mode, emitting the NoiseReductionModeChanged signal."""
        if value != self._NoiseReductionMode:
            self._NoiseReductionMode = value
            self.NoiseReductionModeChanged.emit(value)

    @property
    def Sharpness(self) -> float:
        """Get the sharpness value."""
        return self._Sharpness

    @Sharpness.setter
    def Sharpness(self, value: float):
        """Set the sharpness value, emitting the SharpnessChanged signal."""
        if value != self._Sharpness:
            self._Sharpness = value
            self.SharpnessChanged.emit(value)

    @property
    def AeEnable(self) -> bool:
        """Check if AE is enabled."""
        return self._AeEnable

    @AeEnable.setter
    def AeEnable(self, value: bool):
        """Enable or disable AE, emitting the AeEnableChanged signal."""
        if value != self._AeEnable:
            self._AeEnable = value
            self.AeEnableChanged.emit(value)

    @property
    def ExposureValue(self) -> float:
        """Get the exposure value."""
        return self._ExposureValue

    @ExposureValue.setter
    def ExposureValue(self, value: float):
        """Set the exposure value, emitting the ExposureValueChanged signal."""
        if value != self._ExposureValue:
            self._ExposureValue = value
            self.ExposureValueChanged.emit(value)

    def to_preview_config(self, picam2: Picamera2):
        """
        Generate Picamera2 configuration for preview mode based on current control settings.

        :param picam2: The Picamera2 instance being configured.
        :return: A dictionary containing the configuration for preview mode.
        """
        # ...existing code for to_preview_config...

    def to_still_config(self, picam2: Picamera2):
        """
        Generate Picamera2 configuration for still capture mode based on current control settings.

        :param picam2: The Picamera2 instance being configured.
        :return: A dictionary containing the configuration for still capture mode.
        """
        # ...existing code for to_still_config...

    def to_video_config(self, picam2: Picamera2):
        """
        Generate Picamera2 configuration for video capture mode based on current control settings.

        :param picam2: The Picamera2 instance being configured.
        :return: A dictionary containing the configuration for video capture mode.
        """
        # ...existing code for to_video_config...

# Create a single shared instance for the whole application
controls_model = ControlsModel()
