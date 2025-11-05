from picamera2 import Picamera2

picam2 = Picamera2()
picam2.start()  # Start the camera to ensure controls are available

print("Camera Controls:")
for name, info in picam2.camera_controls.items():
    print(f"{name}: {info}")

picam2.close()