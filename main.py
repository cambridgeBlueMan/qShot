import sys
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from picamera2 import Picamera2
from main_window import MainWindow  # Adjust the import path as needed
from dummy import Dummy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)

def set_dark_palette(app):
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(dark_palette)
    app.setStyle("Fusion")

if __name__ == "__main__":
    app = QApplication.instance()
    if not app:
        logging.info("Creating new QApplication instance.")
        app = QApplication(sys.argv)
    else:
        logging.info("Using existing QApplication instance.")

    set_dark_palette(app)  # Set the dark palette for the application

    try:
        # Get csi argument from command line if provided, else default to 0
        if len(sys.argv) > 1:
            csi_arg = int(sys.argv[1])
            logging.info(f"CSI argument provided via command line: {csi_arg}")
        else:
            csi_arg = 0
            logging.info("No CSI argument provided, defaulting to 0.")

        camera = Picamera2(csi_arg)
        logging.info(f"Camera successfully loaded with csi_arg={csi_arg}")

        # Get sensor_modes and make available globally
        modes = camera.sensor_modes
        logging.info(f"Sensor modes loaded: {modes}")

        # Load and show the main window after camera is loaded
        window = MainWindow(csi_arg, camera, modes)  # Pass the camera instance to MainWindow
        logging.info("Main window instantiated and about to be shown.")

        # Set window size to available screen geometry (excluding system bars)
        screen = app.primaryScreen()
        available_geometry = screen.availableGeometry()
        # window.setGeometry(available_geometry)

        # Optionally set a default size
        window.resize(1200, 800)
        window.show()

        logging.info("Starting Qt event loop.")
        sys.exit(app.exec_())  # Start the Qt event loop and keep the app running
    except ValueError as e:
        logging.error(f"ValueError: {e}")
        print(f"Error: {e}")
    except ImportError as e:
        logging.error(f"ImportError: {e}")
        print(f"ImportError: {e}")
    except Exception as e:
        logging.exception("Exception occurred while loading the camera")
        print(f"Exception: {e}")

