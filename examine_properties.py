"""
examine_properties.py
---------------------
This is a **scratch file** (not part of the main ai_capture application) for exploring how Picamera2 selects sensor modes and configures the camera.

The script iterates over a range of resolutions and framerates, configures the camera for each combination, and prints:
- The actual camera configuration used,
- The transform applied,
- The index and details of the selected sensor mode (if matched),
- The frame duration limits being set.

This tool is intended for experimentation and diagnostics, helping developers understand how requested settings map to sensor modes and internal configuration.

**Note:** This file is for testing and exploration only and is not used by the main application.
"""

from picamera2 import Picamera2
import pprint
import time

def main():
    picam2 = Picamera2(1)
    resolutions = [
        (640, 480),
        (1280, 720),
        (1920, 1080),
        (2592, 1944),
    ]
    framerates = [15, 30, 60]

    pp = pprint.PrettyPrinter(indent=2)

    print("Available sensor modes:")
    for i, mode in enumerate(picam2.sensor_modes):
        print(f"  [{i}] {mode}")

    for res in resolutions:
        for fps in framerates:
            print(f"\n--- Testing resolution {res} at {fps} fps ---")
            # Create a preview configuration with the desired resolution
            config = picam2.create_preview_configuration(main={"size": res})
            # Set framerate via FrameDurationLimits (in microseconds)
            frame_duration = int(1e6 / fps)
            print(f"Setting FrameDurationLimits to ({frame_duration}, {frame_duration})")
            config["controls"]["FrameDurationLimits"] = (frame_duration, frame_duration)
            try:
                picam2.stop()
            except Exception:
                pass
            picam2.configure(config)
            picam2.start()
            time.sleep(0.5)

            # Print actual camera configuration
            print("camera_config['main']:")
            pp.pprint(picam2.camera_config.get('main'))
            print("camera_config['transform']:")
            pp.pprint(picam2.camera_config.get('transform'))

            # Print PixelArraySize property
            print("PixelArraySize:", picam2.camera_properties.get("PixelArraySize"))

            # Try to match the current config to a sensor mode
            main_cfg = picam2.camera_config.get('main')
            selected_index = None
            for i, mode in enumerate(picam2.sensor_modes):
                if (mode.get('size') == main_cfg.get('size') and
                    mode.get('format') == main_cfg.get('format')):
                    selected_index = i
                    print(f"Selected sensor mode index: {i}")
                    print("Selected mode:")
                    pp.pprint(mode)
                    break
            if selected_index is None:
                print("No exact sensor mode match found for this config.")

            picam2.stop()
    print("\nDone.")

if __name__ == "__main__":
    main()