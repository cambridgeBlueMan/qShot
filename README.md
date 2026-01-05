# qShot

**qShot** is a modern, flexible, and extensible camera capture and control application built with Python and PyQt6. It provides a powerful graphical interface for live camera preview, advanced camera controls, and streamlined file management, designed especially for Raspberry Pi and Picamera2.

---

## Features

- **Live Camera Preview:** Real-time video stream from your camera using Picamera2 and Qt-based preview widgets.
- **Advanced Camera Controls:** Easily adjust contrast, brightness, sharpness, exposure, HDR, and more through an intuitive GUI.
- **Two-Way Data Binding:** All controls are connected to a shared `ControlsModel` for robust, reactive updates between the GUI and camera hardware.
- **Modular, Dockable GUI:** All major features (file management, zoom, camera controls, adjustments, etc.) are organized into reusable, dockable widgets for a customizable workspace.
- **Global Signal Management:** Uses a central `app_signals.py` for application-wide events (e.g., camera mode changes, autofocus, etc.).
- **Dark Theme:** Modern, visually comfortable dark palette by default.
- **Logging:** All actions and errors are logged to `app.log` for easy debugging.
- **Extensible Architecture:** Easily add new widgets, camera features, or file management tools.
- **Test Mode:** Includes a dummy camera class for development and testing without hardware.

---

## Application Structure

- `main.py` — Application entry point, sets up the main window and camera.
- `main_window.py` — Main application window with dockable widgets and menu actions.
- `controls_model.py` — Central model for all camera controls (singleton instance).
- `controls_gui.py` — Standalone GUI for interactively adjusting camera controls.
- `dragbutton.py` — Draggable button widget for zoom and viewport selection.
- `zoomer.py` — Zoom control widget, integrates with camera and preview.
- `app_signals.py` — Centralized signal manager for global events.
- `dummy.py` — Dummy camera class for testing without hardware.
- `paths_model.py` / `paths_widget.py` — File naming, path management, and related UI.
- `components/` — Modular widgets for still capture, video capture, adjustments, etc.

---

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

---

## Notes

- Designed for Raspberry Pi and compatible with Picamera2.
- All camera controls and GUI widgets are fully extensible.
- For development or testing without a camera, use the `Dummy` class.
- The application is modular and can be extended with new widgets or camera features as needed.

---

## License

MIT License

---

**qShot — A modern, Python-powered camera capture and control tool for Raspberry Pi and beyond.**
