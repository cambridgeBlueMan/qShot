import sys
import logging
import os

# Remove problematic Qt environment variables
os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)
os.environ.pop("QT_PLUGIN_PATH", None)

from qt import QtWidgets, QtGui, QtCore, Qt  # Unified import

from picamera2 import Picamera2
from main_window import MainWindow  # Adjust the import path as needed
from dummy import Dummy
from config_model import ConfigModel
from controls_model import ControlsModel
from zoomer import ZoomsetsTableModel
from path_model import PathModel  # Add this import

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)

def set_dark_palette(app):
    """
    Set a dark color palette for the given QtWidgets.QApplication instance.

    Args:
        app: The QtWidgets.QApplication instance to apply the palette to.
    """
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

if __name__ == "__main__":
    """
    Entry point for the application.
    Initializes QtWidgets.QApplication, configures the dark palette, loads the camera,
    creates and shows the main window, and starts the QtCore.Qt event loop.
    """
    app = QtWidgets.QApplication.instance()
    if not app:
        logging.info("Creating new QtWidgets.QApplication instance.")
        app = QtWidgets.QApplication(sys.argv)
    else:
        logging.info("Using existing QtWidgets.QApplication instance.")

    set_dark_palette(app)  # Set the dark palette for the application

    try:
        # Get csi argument from command line if provided, else default to 0
        if len(sys.argv) > 1:
            csi_arg = int(sys.argv[1])
            logging.info(f"CSI argument provided via command line: {csi_arg}")
        else:
            csi_arg = 0
            logging.info("No CSI argument provided, defaulting to 0.")

        logging.info("About to create Picamera2 instance...")
        camera = Picamera2(csi_arg)
        logging.info(f"Camera successfully loaded with csi_arg={csi_arg}")

        # Create the initial config model using the camera's video configuration
        config_model = ConfigModel(camera.create_video_configuration())
        logging.info("ConfigModel instance created with video configuration.")

        # Create the controls model using the camera's controls configuration
        controls_model = ControlsModel(cam=camera)
        logging.info("ControlsModel instance created with controls configuration.")

        # Create the zoomsets model
        zoomsets_model = ZoomsetsTableModel()
        logging.info("ZoomsetsModel instance created.")

        # Create the path model
        path_model = PathModel()
        logging.info("PathModel instance created.")

        # Pass config_model to MainWindow if needed, or set it as a global/shared object
        window = MainWindow(
            cam=camera,
            config_model=config_model,
            controls_model=controls_model,
            zoomsets_model=zoomsets_model,
            path_model=path_model  # Pass as argument
        )

        # Set window size to available screen geometry (excluding system bars)
        screen = app.primaryScreen()
        available_geometry = screen.availableGeometry()
        # window.setGeometry(available_geometry)

        # Optionally set a default size
        window.resize(1200, 800)
        window.show()

        logging.info("Starting QtCore.Qt event loop.")
        sys.exit(app.exec())  # Start the QtCore.Qt event loop and keep the app running
    except ValueError as e:
        logging.error(f"ValueError: {e}")
        print(f"Error: {e}")
    except ImportError as e:
        logging.error(f"ImportError: {e}")
        print(f"ImportError: {e}")
    except Exception as e:
        logging.exception("Exception occurred while loading the camera")
        print(f"Exception: {e}")

"""
main.py — Application Entry Point

This file is the main entry point for the AI Capture application.
It initializes the QtCore.Qt application, sets up logging, configures the application's appearance,
loads the camera, and launches the main window.

Key Features:
-------------
- Removes problematic QtCore.Qt environment variables to avoid plugin issues.
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
QtCore.Qt event loop.
"""

logging.info("Detecting available cameras...")
camera_info_list = Picamera2.global_camera_info()
for idx, info in enumerate(camera_info_list):
    logging.info(f"Camera {idx}: {info}")

