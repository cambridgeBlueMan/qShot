from picamera2 import Picamera2

try:
    cam = Picamera2(0)
    print("Camera 0 is present and can be opened.")
    cam.close()
except Exception as e:
    print("Camera 0 is NOT available:", e)