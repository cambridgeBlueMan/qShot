from PyQt6 import QtCore as qtc
from PyQt6 import QtGui as qtg
from PyQt6 import QtWidgets as qtw

class Viewport(qtw.QPushButton):
    """A draggable pushbutton used to set zoom and view position within the camera sensor."""
    posChanged = qtc.pyqtSignal(int, int)
    doubleClicked = qtc.pyqtSignal()
    scrolled = qtc.pyqtSignal(int)

    global newPos

    def __init__(self, win, bWidth=22, bHeight=22):
        self.bWidth = bWidth
        self.bHeight = bHeight
        super().__init__(win)
        self.setFixedSize(self.bWidth, self.bHeight)
        self.containerWidth = win.frameGeometry().width()
        self.containerHeight = win.frameGeometry().height()
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
        if event.button() == qtc.Qt.MouseButton.LeftButton:
            self.__mousePressPos = event.globalPosition().toPoint()
            self.__mouseMovePos = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        global newPos
        if event.buttons() == qtc.Qt.MouseButton.LeftButton:
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPosition().toPoint()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.scm = [int(self.cam.camera_properties['ScalerCropMaximum'][0] / 8),
                        int(self.cam.camera_properties['ScalerCropMaximum'][1] / 8)]
            if newPos.x() > (self.containerWidth - self.bWidth):
                x = (self.containerWidth - self.bWidth)
            elif newPos.x() < self.scm[0]:
                x = self.scm[0]
            else:
                x = newPos.x()
            if newPos.y() > (self.containerHeight - self.bHeight):
                y = (self.containerHeight - self.bHeight)
            elif newPos.y() < self.scm[1]:
                y = self.scm[1]
            else:
                y = newPos.y()
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
        if self.__mousePressPos is not None:
            moved = event.globalPosition().toPoint() - self.__mousePressPos
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
    w.show()
    app.exec()