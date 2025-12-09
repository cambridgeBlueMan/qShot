"""
main.py — Application Entry Point

This file is the main entry point for the AI Capture application.
It initializes the Qt application, sets up logging, configures the application's appearance,
loads the camera, and launches the main window.

Key Features:
-------------
- Removes problematic Qt environment variables to avoid plugin issues.
- Configures logging to write detailed logs to 'app.log'.
- Sets a dark color palette for a modern, visually comfortable UI.
- Handles command-line arguments for camera selection (CSI index).
- Initializes the camera using Picamera2 and loads available sensor modes.
- Instantiates and displays the main window (MainWindow), passing the camera and modes.
- Handles errors gracefully with logging and user feedback.

Usage:
------
Run this file directly to start the application:

    python main.py [CSI_INDEX]

    CSI_INDEX (optional): The index of the camera to use (default is 0).

Customization:
--------------
- To change the default window size, modify 'window.resize(1200, 800)'.
- To use a different camera backend or main window, adjust the relevant import and instantiation lines.
- To change the color palette, edit the 'set_dark_palette' function.

Error Handling:
---------------
- ValueError: If an invalid CSI index is provided.
- ImportError: If required modules are missing.
- Exception: Any other errors during initialization or camera loading.

All errors are logged to 'app.log' and printed to the console.

Summary:
--------
This file is the central launcher for your AI Capture application, handling all startup,
configuration, and error management tasks before handing control to the main window and the
Qt event loop.
"""

import sys
import logging
import os

# Remove problematic Qt environment variables
os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)
os.environ.pop("QT_PLUGIN_PATH", None)

from qt import QtWidgets, QtGui, QtCore, Qt
from picamera2 import Picamera2
from resolutions_model import ResolutionsModel
from main_window import MainWindow
from dummy import Dummy
from config_model import ConfigModel
from controls_model import ControlsModel
from zoomsets_model import ZoomsetsModel
from paths_model import PathsModel
from audio_model import AudioModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)

def set_dark_palette(app):
    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(35, 35, 35))
    dark_palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(255, 255, 255))
    dark_palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtGui.QColor(255, 0, 0))
    dark_palette.setColor(QtGui.QPalette.ColorRole.Link, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(0, 0, 0))
    app.setPalette(dark_palette)
    app.setStyle("Fusion")

def initialize_camera(csi_arg=None):
    """
    Initialize and return a Picamera2 camera instance.
    
    Parameters
    ----------
    csi_arg : int, optional
        Camera index to use. If None, will be read from sys.argv[1] or prompt user if multiple cameras.
    
    Returns
    -------
    Picamera2
        Initialized camera instance
    
    Raises
    ------
    SystemExit
        If no cameras are detected or requested camera index is invalid
    """
    # Detect available cameras
    logging.info("Detecting available cameras...")
    camera_info_list = Picamera2.global_camera_info()
    num_cameras = len(camera_info_list)
    
    for idx, info in enumerate(camera_info_list):
        logging.info(f"Camera {idx}: {info}")
    
    # Handle no cameras attached
    if num_cameras == 0:
        error_msg = "No cameras detected. Please connect a camera and try again."
        logging.error(error_msg)
        QtWidgets.QMessageBox.critical(None, "No Camera Found", error_msg)
        sys.exit(1)
    
    logging.info(f"Found {num_cameras} camera(s)")
    
    # Parse CSI argument if not provided
    if csi_arg is None:
        if len(sys.argv) > 1:
            try:
                csi_arg = int(sys.argv[1])
                if csi_arg not in [0, 1]:
                    logging.warning(f"Invalid CSI argument '{csi_arg}'. Must be 0 or 1. Defaulting to 0.")
                    csi_arg = 0
                else:
                    logging.info(f"CSI argument provided via command line: {csi_arg}")
            except ValueError:
                logging.warning(f"Invalid CSI argument '{sys.argv[1]}'. Must be an integer (0 or 1). Defaulting to 0.")
                csi_arg = 0
        elif num_cameras > 1:
            # Multiple cameras and no argument - show selection dialog
            logging.info("Multiple cameras detected, prompting user for selection...")
            items = []
            for idx, info in enumerate(camera_info_list):
                # Extract camera name/model from info dict
                cam_name = info.get('Model', f'Camera {idx}')
                items.append(f"Camera {idx}: {cam_name}")
            
            item, ok = QtWidgets.QInputDialog.getItem(
                None,
                "Select Camera",
                "Multiple cameras detected. Please select one:",
                items,
                0,
                False
            )
            
            if ok and item:
                # Extract index from selection
                csi_arg = int(item.split(':')[0].split()[-1])
                logging.info(f"User selected camera {csi_arg}")
            else:
                logging.info("User cancelled camera selection, defaulting to camera 0.")
                csi_arg = 0
        else:
            # Single camera, no argument needed
            logging.info("Single camera detected, using camera 0.")
            csi_arg = 0
    
    # Validate that requested camera index exists
    if csi_arg >= num_cameras:
        error_msg = f"Camera index {csi_arg} requested, but only {num_cameras} camera(s) available."
        error_msg += f"\nValid indices: {', '.join(str(i) for i in range(num_cameras))}"
        logging.error(error_msg)
        QtWidgets.QMessageBox.critical(None, "Invalid Camera Index", error_msg)
        sys.exit(1)
    
    logging.info(f"Attempting to initialize camera at index {csi_arg}...")
    camera = Picamera2(csi_arg)
    logging.info(f"Camera successfully loaded: {camera_info_list[csi_arg]}")
    
    return camera


if __name__ == "__main__":
    app = QtWidgets.QApplication.instance()
    if not app:
        logging.info("Creating new QApplication instance.")
        app = QtWidgets.QApplication(sys.argv)
    else:
        logging.info("Using existing QApplication instance.")

    set_dark_palette(app)
    app.setStyleSheet("""
    QToolTip {
        color: black;
        background-color: #ffffdd;
        border: 1px solid black;
    }
""")
    try:
        # Initialize camera
        camera = initialize_camera()

        # Create the initial config model using the camera's video configuration
        config_model = ConfigModel(camera.create_video_configuration())
        logging.info("ConfigModel instance created with video configuration.")

        # Create the controls model using the camera's controls configuration
        controls_model = ControlsModel(cam=camera)
        logging.info("ControlsModel instance created with controls configuration.")
        app.aboutToQuit.connect(controls_model.save_settings)

        # Create the zoomsets model
        zoomsets_model = ZoomsetsModel()
        logging.info("ZoomsetsModel instance created.")

        # Create the path model
        paths_model = PathsModel()
        logging.info("PathModel instance created.")

        # Create the audio model
        audio_model = AudioModel()
        logging.info("AudioModel instance created.")

        # Create the resolutions model
        resolutions_model = ResolutionsModel([
            ('CGA', (320, 200)),
            ('VGA', (640, 480)),
            ('HD 720', (1280, 720)),
            ('HD 1080', (1920, 1080)),
            ('4K UHD', (3840, 2160)),
        ])
        logging.info("ResolutionsModel instance created.")

        window = MainWindow(
            cam=camera,
            config_model=config_model,
            controls_model=controls_model,
            zoomsets_model=zoomsets_model,
            paths_model=paths_model,
            audio_model=audio_model,
            resolutions_model=resolutions_model
        )

        # Optionally set a default size
        window.resize(1200, 800)
        window.show()
        controls_model.load_settings()
        logging.info("Starting Qt event loop.")
        sys.exit(app.exec())
    except ValueError as e:
        logging.error(f"ValueError: {e}")
        print(f"Error: {e}")
    except ImportError as e:
        logging.error(f"ImportError: {e}")
        print(f"ImportError: {e}")
    except Exception as e:
        logging.exception("Exception occurred during application startup")
        print(f"Exception: {e}")

