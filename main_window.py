"""
Main Window Module
------------------

This module implements the MainWindow class, which is the central GUI window for the AI Capture application.
It manages the camera preview, dynamic loading of component widgets, dock widgets, toolbars, menus, and
application-wide state such as configuration and controls models.

Classes and Responsibilities:
----------------------------

- MainWindow: The main application window (inherits from QMainWindow).
    - Holds the central camera preview widget (QGlPicamera2).
    - Manages left, right, and bottom dock widgets for additional tools and components.
    - Dynamically loads component widgets (such as classifier, detector, test, etc.) into the right dock.
    - Provides a toolbar with actions (e.g., save).
    - Manages a menu bar with "Controls", "Components", and "View" menus.
    - Handles application-wide state: camera instance, config_model, controls_model, and sensor modes.
    - Provides methods for reporting menu status, saving files, and loading components.
    - Ensures proper cleanup and replacement of widgets when switching components.

Class Interactions and Workflow:
-------------------------------

1. Initialization
   - MainWindow is created with references to the camera, config_model, and controls_model.
   - Sets up the central camera preview widget using QGlPicamera2.
   - Initializes left, right, and bottom dock widgets for tools and dynamically loaded components.
   - Populates the menu bar with controls, components, and view toggles.
   - Dynamically discovers and adds all *_widget.py components in the components/ directory to the Components menu.

2. Dynamic Component Loading
   - When a user selects a component from the Components menu, MainWindow dynamically loads the corresponding widget class from the components/ directory.
   - Uses get_component_args() to pass shared state (camera, config_model, controls_model, etc.) to the component.
   - Ensures the previous widget is properly cleaned up and deleted before inserting the new one.

3. Toolbar and Menu Actions
   - Provides a toolbar with a save action, which opens a file dialog and saves a text file.
   - Menu actions for toggling dock widgets and reporting the status of checkable menu items.

4. Application State Management
   - Maintains references to the camera, config_model, controls_model, and sensor modes.
   - Shares these objects with all dynamically loaded components for consistent state and configuration.

Summary Table
-------------

| Class      | Role/Responsibility                                   | Interacts With                |
|------------|------------------------------------------------------|-------------------------------|
| MainWindow | Main GUI window, manages preview, docks, menus, state| Camera, config_model, controls_model, all component widgets |
| QGlPicamera2 | Camera preview widget                              | MainWindow, camera            |
| Component Widgets | Dynamically loaded tools (classifier, detector, test, etc.) | MainWindow, receive shared state |

"""

import sys
import logging
import os
from qt import QtWidgets, QtGui, QtCore, Qt, QAction, QGlPicamera2

from adjustments import AdjustmentsWidget
from dummy import Dummy
from picamera2 import Picamera2
from components.classifier_widget import Classifier
from controls_gui import ControlsGui
from zoomer import Zoomer
import importlib.util
from autofocus_widget import AutofocusWidget
from paths_widget import PathsWidget
from audio_model import AudioModel
from audio_widget import AudioWidget
from resolutions_editor import ResolutionsEditor
from resolutions_model import ResolutionsModel

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w' 
)

DEFAULT_WIDGET = "simple_still"

class MainWindow(QtWidgets.QMainWindow):
    """
    Main application window that holds the central widget, toolbars, docks, and menus.
    Provides the main interface for the application, including camera preview, file management,
    and user controls.

    Responsibilities:
    - Holds the central camera preview widget (QGlPicamera2).
    - Manages left, right, and bottom dock widgets for additional tools and components.
    - Dynamically loads component widgets (such as classifier, detector, test, etc.) into the right dock.
    - Provides a toolbar with actions (e.g., save).
    - Manages a menu bar with "Controls", "Components", and "View" menus.
    - Handles application-wide state: camera instance, config_model, controls_model, and sensor modes.
    - Provides methods for reporting menu status, saving files, and loading components.
    - Ensures proper cleanup and replacement of widgets when switching components.

    Interactions:
    - Receives camera, config_model, and controls_model from the main application.
    - Shares these objects with all dynamically loaded components for consistent state and configuration.
    - Interacts with QGlPicamera2 for camera preview, and with all component widgets via dynamic loading.
    """

    def __init__(
        self,
        cam=None,
        config_model=None,
        controls_model=None,
        zoomsets_model=None,
        paths_model=None,
        audio_model=None,  # Add this argument
        resolutions_model=None,  # Add this argument
        *args, **kwargs
    ):
        """
        Initialize the MainWindow and set its central widget, toolbars, docks, and menus.

        Args:
            cam: Camera object (Picamera2 instance). Must not be None.
            config_model: Configuration model object. Must not be None.
            controls_model: Controls model object. Optional.
            zoomsets_model: Zoom sets model object. Optional.
            paths_model: Path model object for file/folder management. Optional.
        """
        if cam is None:
            raise ValueError("A valid camera instance must be provided to MainWindow.")
        if config_model is None:
            raise ValueError("A valid config_model must be provided to MainWindow.")
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Camera Capture App")
        logging.info("MainWindow initialized.")

        # Store arguments as instance attributes (one per line for clarity)
        self.cam = cam
        self.config_model = config_model
        self.controls_model = controls_model
        self.zoomsets_model = zoomsets_model
        self.paths_model = paths_model
        self.audio_model = audio_model or AudioModel()  # <-- Add this line
        self.resolutions_model = resolutions_model  # <-- Add this line
        self.modes = self.cam.sensor_modes

        # Central stacked widget
        self.central_stack = QtWidgets.QStackedWidget()
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
        save_action = toolbar.addAction(QtGui.QIcon.fromTheme("document-save"), "Save")
        save_action.setStatusTip("Save the current document")
        save_action.triggered.connect(self.save_file_dialog)  # Connect to save dialog
        logging.info("Save action added to toolbar.")

        # Add a status bar
        self.statusBar().showMessage("Ready")
        logging.info("Status bar initialized.")

        # Set the default widget name (without _widget.py)
        self.default_widget_name = DEFAULT_WIDGET

        # Add dock widgets
        self.left_dock = QtWidgets.QDockWidget("Left Dock", self)
        self.left_dock.visibilityChanged.connect(self.on_left_dock_visibility_changed)
        self.left_dock.setWidget(Zoomer(self, **self.get_component_args()))
        self.left_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.left_dock)
        self.left_dock.hide()  # Hide left dock on launch

        self.right_dock = QtWidgets.QDockWidget("Component", self)
        # Dynamically load the default widget
        default_widget = self.load_component_widget_by_name(self.default_widget_name)
        self.right_dock.setWidget(default_widget)
        self.right_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.right_dock)

        # Add a bottom dock with 3 equally sized columns, one is ControlsGui
        self.bottom_dock = QtWidgets.QDockWidget("Bottom Dock", self)
        bottom_widget = QtWidgets.QWidget(self.bottom_dock)
        bottom_layout = QtWidgets.QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)

        # First column: placeholder widget
        bottom_col1 = self.create_autofocus_widget()
        # Second column: instantiate AdjustmentsWidget with kwargs
        bottom_col2 = AdjustmentsWidget(**self.get_component_args())
        # Third column: placeholder widget
        bottom_col3 = PathsWidget(**self.get_component_args())

        bottom_layout.addWidget(bottom_col1, 1)
        bottom_layout.addWidget(bottom_col2, 1)
        bottom_layout.addWidget(bottom_col3, 1)
        bottom_widget.setLayout(bottom_layout)
        self.bottom_dock.setWidget(bottom_widget)
        
        self.bottom_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.bottom_dock)
        self.bottom_dock.hide()  # Hide bottom dock on launch

        logging.info("Left, right, and bottom docks added.")

        # --- Menu Bar ---
        menubar = self.menuBar()
        # Add Edit menu if not present
        edit_menu = menubar.findChild(QtWidgets.QMenu, "editMenu")
        if edit_menu is None:
            edit_menu = menubar.addMenu("Edit")
            edit_menu.setObjectName("editMenu")

        # Add Resolutions Editor action
        self.res_editor_action = QtWidgets.QAction("Resolutions Editor", self)
        self.res_editor_action.triggered.connect(self.open_resolutions_editor)
        edit_menu.addAction(self.res_editor_action)

        # Add a "Controls" menu and three checkable items
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

        self.left_dock.visibilityChanged.connect(self.on_left_dock_visibility_changed)

        # Initialize AudioModel
        self.audio_model = AudioModel()

        # Add an "Audio" menu with an action to show AudioWidget
        audio_menu = menubar.addMenu("Audio")
        show_audio_action = QAction("Show Audio Widget", self)
        audio_menu.addAction(show_audio_action)
        show_audio_action.triggered.connect(self.show_audio_widget)
        logging.info("Audio menu and Show Audio Widget action added.")

        # --- File menu ---
        file_menu = menubar.findChild(QtWidgets.QMenu, "fileMenu")
        if file_menu is None:
            file_menu = QtWidgets.QMenu("File", self)
            file_menu.setObjectName("fileMenu")
            menubar.insertMenu(menubar.actions()[0] if menubar.actions() else None, file_menu)

        quit_action = QtWidgets.QAction("Quit", self)
        quit_action.triggered.connect(QtWidgets.QApplication.instance().quit)
        file_menu.addAction(quit_action)

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
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
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
                QtWidgets.QMessageBox.information(self, "File Saved", f"File saved to:\n{file_path}")
                logging.info(f"File saved to: {file_path}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")
                logging.error(f"Could not save file: {e}")

    def load_component_widget(self):
        """
        Slot for menu actions: dynamically load and insert a component widget into the right dock
        when a user selects a component from the Components menu.
        Ensures proper cleanup of the outgoing widget.
        """
        action = self.sender()
        name = action.data()
        class_name = None
        module_name = None
        try:
            module_name = f"{name}_widget"
            module_path = os.path.join(os.path.dirname(__file__), "components", f"{module_name}.py")
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Use CamelCase for class name
            class_name = ''.join(part.capitalize() for part in name.split('_'))
            widget_class = getattr(module, class_name)
            widget_instance = widget_class(**self.get_component_args(name))
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
            QtWidgets.QMessageBox.critical(self, "Error", f"Could not load component '{class_name}':\n{e}")

    def load_component_widget_by_name(self, name):
        """
        Programmatically load and insert a component widget into the right dock by name.
        Used for loading the default widget at startup or when switching components in code.
        Ensures proper cleanup of the outgoing widget.
        """
        class_name = None
        module_name = None
        try:
            module_name = f"{name}_widget"
            module_path = os.path.join(os.path.dirname(__file__), "components", f"{module_name}.py")
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Use CamelCase for class name
            class_name = ''.join(part.capitalize() for part in name.split('_'))
            widget_class = getattr(module, class_name)
            widget_instance = widget_class(**self.get_component_args(name))
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

    def create_autofocus_widget(self):
        """Return an AutofocusWidget if AF is supported, else a placeholder label."""
        if 'AfMode' in self.cam.camera_controls:
            return AutofocusWidget(**self.get_component_args())
        else:
            return QtWidgets.QLabel("Autofocus not available for this camera.", self)

    def get_component_args(self, name=None):
        """
        Prepare a dictionary of arguments to pass to component widgets.
        Includes camera, config_model, controls_model, and optionally a settings_group name.
        """
        args = {
            "cam": self.cam,
            "preview": self.preview,
            "config_model": self.config_model,
            "controls_model": self.controls_model,
            "zoomsets_model": self.zoomsets_model,
            "paths_model": self.paths_model,
            "audio_model": self.audio_model,  # <-- Add this line
        }
        if name is not None:
            args["settings_group"] = name
        return args

    def on_left_dock_visibility_changed(self, visible):
        if visible:
            self.showMaximized()  # Maximize, but keep window decorations
        else:
            self.showNormal()

    def show_audio_widget(self):
        """Instantiate AudioWidget and show it in a dialog window."""
        print("[MainWindow] show_audio_widget called")
        audio_widget = AudioWidget(**self.get_component_args())
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Audio Widget")
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.addWidget(audio_widget)
        dialog.setLayout(layout)
        dialog.resize(400, 300)
        dialog.exec()

    def open_resolutions_editor(self):
        """Open the resolutions editor dialog."""
        dialog = ResolutionsEditor(self.resolutions_model)
        dialog.exec()

if __name__ == "__main__":
    """
    Entry point for the application. Initializes QApplication, shows the main window,
    and enters the Qt event loop.
    """
    from controls_model import ControlsModel
    from config_model import ConfigModel

    app = QtWidgets.QApplication(sys.argv)
    # Dummy camera and models for testing
    class DummyCam:
        sensor_modes = ["mode1", "mode2"]
        def start(self): pass

    cam = DummyCam()
    config_model = ConfigModel()
    controls_model = ControlsModel()
    audio_model = AudioModel()
    resolutions_model = ResolutionsModel([
        ('CGA', (320, 200)),
        ('VGA', (640, 480)),
        ('HD 720', (1280, 720)),
        ('HD 1080', (1920, 1080)),
        ('4K UHD', (3840, 2160)),
    ])
    window = MainWindow(
        cam=cam,
        config_model=config_model,
        controls_model=controls_model,
        audio_model=audio_model,
        resolutions_model=resolutions_model  # <-- Pass here
    )
    window.show()
    logging.info("MainWindow shown. Entering Qt event loop.")
    sys.exit(app.exec())