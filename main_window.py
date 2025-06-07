import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QMenu, QFileDialog, QMessageBox, QDockWidget, QWidget, QVBoxLayout
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from ai_file_manager import FileManagerWidget
from dummy import Dummy
from picamera2 import Picamera2
from picamera2.previews.qt import QGlPicamera2
from right_dock import RightDock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w'
)

class MainWindow(QMainWindow):
    """
    Main application window that holds the MainWidget.
    """
    def __init__(self, csi=0, cam=None, modes=None):
        """
        Initialize the MainWindow and set its central widget.
        """
        super().__init__()
        self.setWindowTitle("My App")
        logging.info("MainWindow initialized.")

        # Instantiate camera if not provided
        if cam is None:
            cam = Picamera2(csi)
            modes = cam.sensor_modes
            logging.info(f"Camera instantiated with csi={csi} and sensor modes loaded: {modes}")

        # Create QGlPicamera2 preview widget
        self.preview = QGlPicamera2(
            cam,
            width=640,
            height=480,
            keep_ar=True,
            parent=self
        )
        
        cam.start()
        logging.info("Camera started and QGlPicamera2 preview created.")

        self.setCentralWidget(self.preview)
        logging.info("QGlPicamera2 set as central widget.")

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

        # Add dock widgets
        self.left_dock = QDockWidget("Left Dock", self)
        self.left_dock.setWidget(Dummy(text="Left Dummy"))
        self.left_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)
        self.left_dock.hide()  # Hide left dock on launch

        self.right_dock = QDockWidget("File Manager", self)
        self.right_dock.setWidget(RightDock(cam=cam, csi=csi, modes=modes, preview=self.preview))
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

if __name__ == "__main__":
    """
    Entry point for the application.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    logging.info("MainWindow shown. Entering Qt event loop.")
    sys.exit(app.exec_())