# PathsWidget Design and Usage

## Overview

`PathsWidget` is a PyQt6 widget for viewing and editing application path and filename settings. It is designed for use in the `ai_capture` project, but can be adapted for other projects with similar needs.

## Layout

- **Two main group boxes:**
  - **Paths:**  
    - "Still folder" (QLineEdit + Browse button)
    - "Video folder" (QLineEdit + Browse button)
  - **File name:**  
    - "Image root" (QLineEdit)
    - "Strategy" (QComboBox: date, sequence, hash)
    - "Generate sample" (QLabel + button)
    - "Save" (button)

- **Grid layouts** are used within each group box for compact, form-like alignment.
- The main layout is a vertical box (`QVBoxLayout`), with a stretch at the end to prevent the group boxes from stretching vertically when the window is resized.

## Functionality

- **Folder fields:**  
  Users can view and edit the still and video folder paths. Clicking "Browse" opens a folder selection dialog.
- **Filename controls:**  
  Users can set the root for generated filenames and choose a naming strategy. A sample filename is shown and can be regenerated.
- **Save:**  
  Applies changes to the underlying `PathModel` and persists them.
- **Model synchronization:**  
  The widget listens for changes in the model and updates the UI accordingly.

## Usage

- **In code:**
  ```python
  from paths_widget import PathsWidget
  from path_model import PathModel

  path_model = PathModel()
  widget = PathsWidget(path_model=path_model)
  ```
- **Standalone test:**
  Run `python paths_widget.py` to launch the widget in a test window.

## Design Notes

- **Group boxes** provide clear separation of concerns.
- **Grid layouts** ensure compact and aligned controls.
- **Stretch** at the end of the main layout keeps the UI compact on resize.
- The widget is suitable for embedding in a larger application or for standalone use.

---