from picamera2 import Picamera2
import pprint

def get_camera_info(camera_index):
    try:
        picam2 = Picamera2(camera_index)
        modes = [str(mode) for mode in picam2.sensor_modes]
        pixel_array_active_areas = picam2.camera_properties.get("PixelArrayActiveAreas")
        pixel_array_size = picam2.camera_properties.get("PixelArraySize")
        return {
            "modes": modes,
            "PixelArrayActiveAreas": pixel_array_active_areas,
            "PixelArraySize": pixel_array_size
        }
    except Exception as e:
        print(f"Could not open camera {camera_index}: {e}")
        return None

if __name__ == "__main__":
    camera_info = {}
    for cam_index in range(2):  # Check up to 2 cameras
        info = get_camera_info(cam_index)
        if info:
            camera_info[f"Camera {cam_index}"] = info

    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(camera_info)