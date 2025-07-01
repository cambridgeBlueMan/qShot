import sys
import logging
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QMenu, QFileDialog, QMessageBox, QDockWidget, QWidget, QVBoxLayout, QStackedWidget
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from ai_file_manager import FileManagerWidget
from dummy import Dummy
from picamera2 import Picamera2
from picamera2.previews.qt import QGlPicamera2
from components.classifier_widget import Classifier
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w' 
)

class MainWindow(QMainWindow):
    """
    Main application window that holds the central widget, toolbars, docks, and menus.
    Provides the main interface for the application, including camera preview, file management,
    and user controls.
    """
    def __init__(self, csi=0, cam=None, modes=None):
        """
        Initialize the MainWindow and set its central widget, toolbars, docks, and menus.

        Args:
            csi: Camera serial interface index.
            cam: Camera object (Picamera2 instance). If None, a new camera is instantiated.
            modes: List of camera modes. If None, loaded from the camera.
        """
        super().__init__()
        self.setWindowTitle("Camera Capture App")
        logging.info("MainWindow initialized.")

        # Store arguments as instance attributes
        self.csi = csi
        self.cam = cam if cam is not None else Picamera2(csi)
        self.modes = modes if modes is not None else self.cam.sensor_modes

        # Central stacked widget
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)

        # Create QGlPicamera2 preview widget
        self.preview = QGlPicamera2(
            self.cam,
            width=640,
            height=480,
            keep_ar=True,
            parent=self
        )
        self.central_stack.addWidget(self.preview)
        self.central_stack.setCurrentWidget(self.preview)
        self._captured_image_label = None  # For later use
        self.cam.start()
        logging.info("Camera started and QGlPicamera2 preview created.")

        # Add a toolbar
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        logging.info("Toolbar added.")

        # Add a save action with an icon to the toolbar
        save_action = toolbar.addAction(QIcon.fromTheme("document-save"), "Save")
        save_action.setStatusTip("Save the current document")
        save_action.triggered.connect(self.save_file_dialog)  # Connect to save dialog
        logging.info("Save action added to toolbar.")

        # Add a status bar
        self.statusBar().showMessage("Ready")
        logging.info("Status bar initialized.")

        # Set the default widget name (without _widget.py)
        self.default_widget_name = "detector"

        # Add dock widgets
        self.left_dock = QDockWidget("Left Dock", self)
        self.left_dock.setWidget(Dummy(text="Left Dummy"))
        self.left_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)
        self.left_dock.hide()  # Hide left dock on launch

        self.right_dock = QDockWidget("Component", self)
        # Dynamically load the default widget
        default_widget = self.load_component_widget_by_name(self.default_widget_name)
        self.right_dock.setWidget(default_widget)
        self.right_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

        self.bottom_dock = QDockWidget("Bottom Dock", self)
        self.bottom_dock.setWidget(Dummy(text="Bottom Dummy"))
        self.bottom_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bottom_dock)
        self.bottom_dock.hide()  # Hide bottom dock on launch

        logging.info("Left, right, and bottom docks added.")

        # Add a menu bar with a "Controls" menu and three checkable items
        menubar = self.menuBar()
        controls_menu = menubar.addMenu("Controls")
        logging.info("Controls menu added to menu bar.")

        # Add a "Components" menu
        components_menu = menubar.addMenu("Components")
        logging.info("Components menu added to menu bar.")

        # Dynamically add items for each <name>_widget.py in components/
        components_dir = os.path.join(os.path.dirname(__file__), "components")
        if os.path.isdir(components_dir):
            for fname in os.listdir(components_dir):
                if fname.endswith("_widget.py") and not fname.startswith("__"):
                    name = fname[:-10]  # Remove '_widget.py'
                    action = QAction(name, self)
                    action.setData(name)
                    components_menu.addAction(action)
                    action.triggered.connect(self.load_component_widget)
                    logging.info(f"Added '{name}' to Components menu.")
            logging.info(f"Files in components: {os.listdir(components_dir)}")
        else:
            logging.warning(f"Components directory not found: {components_dir}")

        self.action_tom = QAction("tom", self, checkable=True)
        self.action_dick = QAction("dick", self, checkable=True)
        self.action_harry = QAction("harry", self, checkable=True)

        controls_menu.addAction(self.action_tom)
        controls_menu.addAction(self.action_dick)
        controls_menu.addAction(self.action_harry)
        logging.info("Checkable actions (tom, dick, harry) added to Controls menu.")

        # Connect actions to a reporting function
        self.action_tom.triggered.connect(self.report_menu_status)
        self.action_dick.triggered.connect(self.report_menu_status)
        self.action_harry.triggered.connect(self.report_menu_status)

        # Add a "View" menu to toggle dock widgets using toggleViewAction
        view_menu = menubar.addMenu("View")
        view_menu.addAction(self.left_dock.toggleViewAction())
        view_menu.addAction(self.right_dock.toggleViewAction())
        view_menu.addAction(self.bottom_dock.toggleViewAction())
        logging.info("View menu with dock toggle actions added.")

    def report_menu_status(self):
        """
        Report the current status of the checkable menu actions (tom, dick, harry)
        by updating the status bar and logging the status.
        """
        status = (
            f"tom: {'active' if self.action_tom.isChecked() else 'inactive'}, "
            f"dick: {'active' if self.action_dick.isChecked() else 'inactive'}, "
            f"harry: {'active' if self.action_harry.isChecked() else 'inactive'}"
        )
        self.statusBar().showMessage(status)
        logging.info(f"Menu status updated: {status}")

    def save_file_dialog(self):
        """
        Open a dialog box suitable for saving a text file.
        If a file is selected, writes a default line to it and shows a confirmation or error.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Text File",
            "",
            "Text Files (*.txt);;All Files (*)",
            options=options
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write("Your text goes here.\n")
                QMessageBox.information(self, "File Saved", f"File saved to:\n{file_path}")
                logging.info(f"File saved to: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")
                logging.error(f"Could not save file: {e}")

    def load_component_widget(self):
        """
        Slot for menu actions: dynamically load and insert a component widget into the right dock
        when a user selects a component from the Components menu.
        Ensures proper cleanup of the outgoing widget.
        """
        action = self.sender()
        name = action.data()
        module_name = f"{name}_widget"
        module_path = os.path.join(os.path.dirname(__file__), "components", f"{module_name}.py")
        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            class_name = name.capitalize()
            widget_class = getattr(module, class_name)
            widget_instance = widget_class(**self.get_settings(name))
            widget_instance.setWindowTitle(class_name)
            old_widget = self.right_dock.widget()
            if old_widget is not None:
                if hasattr(old_widget, "cleanup"):
                    old_widget.cleanup()
                old_widget.deleteLater()
            self.right_dock.setWidget(widget_instance)
            self.right_dock.show()
            logging.info(f"Instantiated and inserted widget: {class_name} into right dock (previous content cleaned up)")
        except Exception as e:
            logging.error(f"Failed to load or instantiate {class_name} from {module_name}: {e}")
            QMessageBox.critical(self, "Error", f"Could not load component '{class_name}':\n{e}")

    def load_component_widget_by_name(self, name):
        """
        Programmatically load and insert a component widget into the right dock by name.
        Used for loading the default widget at startup or when switching components in code.
        Ensures proper cleanup of the outgoing widget.
        """
        try:
            module_name = f"{name}_widget"
            module_path = os.path.join(os.path.dirname(__file__), "components", f"{module_name}.py")
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            class_name = name.capitalize()
            widget_class = getattr(module, class_name)
            widget_instance = widget_class(**self.get_settings(name))
            widget_instance.setWindowTitle(class_name)
            old_widget = self.right_dock.widget()
            if old_widget is not None:
                if hasattr(old_widget, "cleanup"):
                    try:
                        old_widget.cleanup()
                    except Exception as e:
                        logging.error(f"Error during cleanup of {type(old_widget).__name__}: {e}")
                old_widget.deleteLater()
            self.right_dock.setWidget(widget_instance)
            self.right_dock.show()
            logging.info(f"Instantiated and inserted widget: {class_name} into right dock (previous content cleaned up)")
            return widget_instance
        except Exception as e:
            logging.error(f"Failed to load or instantiate {class_name} from {module_name}: {e}")
            return Dummy(text="Failed to load default widget")

    def get_settings(self, name=None):
        """
        Prepare a dictionary of settings to pass to component widgets.
        """
        settings = {
            "cam": self.cam,
            "csi": self.csi,
            "modes": self.modes,
            "preview": self.preview,
        }
        if name is not None:
            settings["settings_group"] = name
            logging.info(f"Settings prepared for component: {name}")
        return settings

if __name__ == "__main__":
    """
    Entry point for the application. Initializes QApplication, shows the main window,
    and enters the Qt event loop.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    logging.info("MainWindow shown. Entering Qt event loop.")
    sys.exit(app.exec_())