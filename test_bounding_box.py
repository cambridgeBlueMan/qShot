# Minimal PyQt5 bounding box annotation example

import sys
import csv
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap, QPainter, QPen, QImage
from PyQt6.QtCore import Qt, QRect

class BBoxLabel(QLabel):
    def __init__(self, image_path):
        super().__init__()
        self.pixmap_orig = QPixmap(image_path)
        self.setPixmap(self.pixmap_orig)
        self.start = None
        self.end = None
        self.rect = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start = event.pos()
            self.end = self.start
            self.update()

    def mouseMoveEvent(self, event):
        if self.start:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.start:
            self.end = event.pos()
            self.rect = QRect(self.start, self.end).normalized()
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.start and self.end:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 1, Qt.SolidLine))
            rect = QRect(self.start, self.end).normalized()
            painter.drawRect(rect)

    def get_bbox(self):
        if self.rect:
            return self.rect.getRect()  # returns (x, y, w, h)
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bounding Box Annotation Example")
        self.label = BBoxLabel("test.jpg")  # Use your image path here
        self.button = QPushButton("Save Bounding Box")
        self.button.clicked.connect(self.save_bbox)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def save_bbox(self):
        bbox = self.label.get_bbox()
        if bbox:
            x, y, w, h = bbox
            x2, y2 = x + w, y + h
            with open("annotations.csv", "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["test.jpg", x, y, x2, y2, "object"])
            print(f"Saved bbox: {x},{y},{x2},{y2}")
        else:
            print("No bounding box drawn.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())