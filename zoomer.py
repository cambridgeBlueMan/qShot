from PyQt6 import QtWidgets as qtw
from PyQt6 import QtCore as qtc
from PyQt6 import QtGui as qtg
from viewport import Viewport
from app_signals import app_signals
# from config_model import config_model

class Zoomer(qtw.QWidget):
    """A widget for controlling zoom using a DragButton."""

    def __init__(self, parent=None, cam=None, preview=None):
        super().__init__(parent)
        layout = qtw.QVBoxLayout(self)

        # Checkbox to enable zoom
        self.enable_zoom_checkbox = qtw.QCheckBox("Enable zoom")
        layout.addWidget(self.enable_zoom_checkbox)

        # QFrame for zoom area
        self.zoom_frame = qtw.QFrame(self)
        self.zoom_frame.setFrameShape(qtw.QFrame.Shape.Box)
        self.zoom_frame.setFixedSize(507, 380)
        frame_layout = qtw.QVBoxLayout(self.zoom_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)

        # DragButton inside the frame 
        
        self.viewport = Viewport(self.zoom_frame)
        self.viewport.scrolled['int'].connect(self.setViewportSize) # type: ignore

        if cam is not None:
            self.viewport.setCamera(cam)
        frame_layout.addWidget(self.viewport)

        layout.addWidget(self.zoom_frame)

        # Add preview widget if provided
        if preview is not None:
            layout.addWidget(preview)

        self.setLayout(layout)
        app_signals.mode_changed.connect(self.on_global_mode_changed) 

    def on_global_mode_changed(self, mode):
        # Handle mode change here (update UI, internal state, etc.)
        print(f"Zoomer received global mode change: {mode}")
        # Add any logic you need for reacting to mode changes



    def eventFilter(self, obj, event):
        if event.type() == qtc.QEvent.Type.Close:
            self.zoomer.close()
        return super().eventFilter(obj, event)

    def setViewportSize(self, delta):
        """
        Adjust the viewport (DragButton) size in response to mouse wheel events.

        Parameters:
            delta (int): The vertical scroll amount from the wheel event.
                         Positive for zoom in, negative for zoom out.
        """
        # Example logic: increase/decrease size by 5 pixels per wheel step
        step = 5
        new_width = max(10, min(self.viewport.bWidth + (step if delta > 0 else -step), self.zoom_frame.width()))
        new_height = max(10, min(self.viewport.bHeight + (step if delta > 0 else -step), self.zoom_frame.height()))
        self.viewport.setSize(new_width, new_height)

if __name__ == "__main__":
    import sys
    from picamera2 import Picamera2
    from picamera2.previews.qt import QGl6Picamera2 as QGlPicamera2

    app = qtw.QApplication(sys.argv)
    camera = Picamera2()
    preview = QGlPicamera2(camera)
    camera.start()
    zoomer = Zoomer(cam=camera)

    # Create a container widget and layout
    container = qtw.QWidget()
    layout = qtw.QHBoxLayout(container)
    layout.addWidget(zoomer)
    layout.addWidget(preview)
    container.setWindowTitle("Zoomer & Preview")
    container.resize(1100, 400)
    container.show()

    sys.exit(app.exec())