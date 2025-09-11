# ai_capture

A PyQt6-based camera capture and control application inspired by the NVIDIA C++ camera capture program, but implemented in Python for flexibility and rapid development.

## Features

- **Live Camera Preview:** View real-time camera output using Picamera2 and Qt-based preview widgets.
- **Comprehensive Camera Controls:** Adjust contrast, brightness, sharpness, exposure, HDR, and more through an intuitive GUI.
- **Two-Way Data Binding:** All controls are connected to a shared `ControlsModel` for robust, reactive updates between the GUI and camera hardware.
- **Modular GUI:** Components such as file management, zoom, and camera controls are organized into reusable widgets.
- **Global Signal Management:** Uses a central `app_signals.py` for application-wide events (e.g., camera mode changes).
- **Dark Theme:** Modern, visually comfortable dark palette by default.
- **Logging:** All actions and errors are logged to `app.log` for easy debugging.

## Structure

- `main.py` — Application entry point, sets up the main window and camera.
- `main_window.py` — Main application window with dockable widgets.
- `controls_model.py` — Central model for all camera controls (singleton instance).
- `controls_gui.py` — Test GUI for interactively adjusting camera controls.
- `dragbutton.py` — Draggable button widget for zoom and viewport selection.
- `zoomer.py` — Zoom control widget, integrates with camera and preview.
- `app_signals.py` — Centralized signal manager for global events.
- `dummy.py` — Dummy camera class for testing without hardware.

## Usage

1. **Install dependencies:**
    ```bash
    pip install pyqt6 picamera2
    ```

2. **Run the application:**
    ```bash
    python main.py
    ```

3. **(Optional) Run the controls test GUI:**
    ```bash
    python controls_gui.py
    ```

## Notes

- Designed for Raspberry Pi and compatible with Picamera2.
- All camera controls and GUI widgets are fully extensible.
- For development or testing without a camera, use the `Dummy` class.

## License

MIT License

---

**Inspired by NVIDIA's C++ camera capture tool, reimagined for Python and PyQt6.**
