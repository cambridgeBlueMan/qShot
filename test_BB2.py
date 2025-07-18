import sys
import os
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap, QPainter, QPen, QImage
from PyQt6.QtCore import Qt, QRect
import cv2

# Remove the QT_QPA_PLATFORM_PLUGIN_PATH environment variable if set.
# This prevents conflicts between OpenCV's and PyQt5's Qt plugin paths,
# which can cause errors like "Could not load the Qt platform plugin 'xcb'".
os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)

def cvimg_to_qpixmap(cv_img):
    """Convert OpenCV image (BGR) to QPixmap."""
    height, width, channel = cv_img.shape
    bytes_per_line = 3 * width
    qimg = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
    return QPixmap.fromImage(qimg)

class BBoxLabel(QLabel):
    def __init__(self, pixmap): 
        super().__init__()
        self.setPixmap(pixmap)
        self.boxes = []  # List of QRect
        self.start = None
        self.end = None
        self.drawing = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start = event.pos()
            self.end = self.start
            self.drawing = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.end = event.pos()
            rect = QRect(self.start, self.end).normalized()
            self.boxes.append(rect)
            self.drawing = False
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        # Draw all saved boxes
        for rect in self.boxes:
            painter.drawRect(rect)
        # Draw current box
        if self.drawing and self.start and self.end:
            painter.setPen(QPen(Qt.green, 2, Qt.DashLine))
            rect = QRect(self.start, self.end).normalized()
            painter.drawRect(rect)

    def get_bboxes(self):
        return [rect.getRect() for rect in self.boxes]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bounding Box Annotation Example")

        # --- Freeze a frame from video ---
        cap = cv2.VideoCapture("test.mp4")  # Use your video file
        ret, frame = cap.read()
        cap.release()
        if not ret:
            raise RuntimeError("Failed to read frame from video.")
        pixmap = cvimg_to_qpixmap(frame)

        self.label = BBoxLabel(pixmap)
        self.button = QPushButton("Save Bounding Boxes")
        self.button.clicked.connect(self.save_bboxes)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def save_bboxes(self):
        bboxes = self.label.get_bboxes()
        for bbox in bboxes:
            print("Bounding box:", bbox)
        # You can save to CSV or elsewhere as needed

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())