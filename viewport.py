from qt import QtCore as qtc, QtWidgets as qtw, QtGui, Qt

# Compatibility for mouse button enum
try:
    LeftButton = qtc.Qt.MouseButton.LeftButton
except AttributeError:
    LeftButton = Qt.LeftButton

class Viewport(qtw.QPushButton):
    """
    Example Viewport button widget for use with Zoomer.
    """
    posChanged = qtc.pyqtSignal(int, int)
    doubleClicked = qtc.pyqtSignal()
    scrolled = qtc.pyqtSignal(int)

    def __init__(self, win, bWidth=40, bHeight=40):
        super().__init__(win)
        self.setMinimumSize(40, 40)
        self.bWidth = bWidth
        self.bHeight = bHeight
        self.setFixedSize(self.bWidth, self.bHeight)
        self.setText("")  # No text by default
        self.move(0, 0)
        self.containerWidth = win.size().width()
        self.containerHeight = win.size().height()
        qtc.QMetaObject.connectSlotsByName(self)

    def setContainerSize(self, x, y):
        self.containerWidth = x
        self.containerHeight = y

    def setCamera(self, cam):
        self.cam = cam

    def setSize(self, w, h):
        self.setFixedSize(int(w), int(h))
        self.bWidth = w
        self.bHeight = h

    def wheelEvent(self, event):
        self.scrolled.emit(event.angleDelta().y())

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == LeftButton:
            pos = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
            self.__mousePressPos = pos
            self.__mouseMovePos = pos
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == LeftButton:
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            if hasattr(self, "cam") and hasattr(self.cam, "camera_properties"):
                self.scm = [int(self.cam.camera_properties['ScalerCropMaximum'][0] / 8),
                            int(self.cam.camera_properties['ScalerCropMaximum'][1] / 8)]
            else:
                self.scm = [0, 0]
            x = max(self.scm[0], min(newPos.x(), self.containerWidth - self.bWidth))
            y = max(self.scm[1], min(newPos.y(), self.containerHeight - self.bHeight))
            x = int(x)
            y = int(y)
            self.sendPos((x, y))
            self.move(x, y)
            self.__mouseMovePos = globalPos
        super().mouseMoveEvent(event)

    def moveButtonToOrigin(self):
        self.move(0, 0)

    def sendPos(self, pos):
        self.posChanged.emit(pos[0], pos[1])

    def mouseReleaseEvent(self, event):
        if hasattr(self, '__mousePressPos') and self.__mousePressPos is not None:
            releasePos = event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()
            moved = releasePos - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)

class DummyCam:
    camera_properties = {'ScalerCropMaximum': [176, 144]}

if __name__ == "__main__":
    app = qtw.QApplication([])
    w = qtw.QWidget()
    w.resize(800, 600)
    button = Viewport(w)
    button.setCamera(DummyCam())
    button.raise_()  # Ensure it's on top
    # Update container size on parent resize
    def on_resize(event):
        button.setContainerSize(w.size().width(), w.size().height())
    w.resizeEvent = on_resize
    w.show()
    app.exec()