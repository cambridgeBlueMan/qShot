from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from generate_color import generate_color
import random

class BBoxLabel(QLabel):
    """
    QLabel subclass for drawing bounding boxes on an image.
    Stores boxes in original image coordinates so they persist and scale on resize.
    """
    box_completed = pyqtSignal(int, int, int, int, int)  # x, y, w, h, class_index

    def __init__(self, pixmap=None, parent=None):
        super().__init__(parent)
        if pixmap is not None:
            self.setPixmap(pixmap)
        self.boxes = []  # List of QRect in original image coordinates
        self.box_colors = []  # List of class indices for each box
        self.start = None  # In widget coords while drawing
        self.end = None    # In widget coords while drawing
        self.drawing = False
        self.annotation_enabled = True
        self._original_pixmap_size = None

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        if pixmap:
            super().setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            super().setPixmap(pixmap)
        self._original_pixmap_size = pixmap.size() if pixmap else None
        self.update()

    def enable_annotation(self, enabled=True):
        self.annotation_enabled = enabled

    def _to_image_coords(self, point):
        """Convert widget coordinates to original image coordinates."""
        if not self._original_pixmap_size:
            return point
        label_rect = self.rect()
        scale_x = self._original_pixmap_size.width() / label_rect.width()
        scale_y = self._original_pixmap_size.height() / label_rect.height()
        return QPoint(int(point.x() * scale_x), int(point.y() * scale_y))

    def _to_widget_coords(self, point):
        """Convert original image coordinates to widget coordinates."""
        if not self._original_pixmap_size:
            return point
        label_rect = self.rect()
        scale_x = label_rect.width() / self._original_pixmap_size.width()
        scale_y = label_rect.height() / self._original_pixmap_size.height()
        return QPoint(int(point.x() * scale_x), int(point.y() * scale_y))

    def mousePressEvent(self, event):
        if self.annotation_enabled and event.button() == Qt.LeftButton:
            self.start = event.pos()
            self.end = self.start
            self.drawing = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.annotation_enabled and self.drawing:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.annotation_enabled and event.button() == Qt.LeftButton and self.drawing:
            self.end = event.pos()
            # Store box in original image coordinates
            p1 = self._to_image_coords(self.start)
            p2 = self._to_image_coords(self.end)
            rect = QRect(p1, p2).normalized()
            self.boxes.append(rect)
            # Use default class index (e.g., 0) instead of random
            class_index = 0
            self.box_colors.append(class_index)
            self.drawing = False
            self.start = None
            self.end = None
            self.update()
            # Emit signal with box info
            x, y, w, h = rect.getRect()
            self.box_completed.emit(x, y, w, h, class_index)

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.pixmap() or not self._original_pixmap_size:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for i, rect in enumerate(self.boxes):
            p1 = self._to_widget_coords(rect.topLeft())
            p2 = self._to_widget_coords(rect.bottomRight())
            scaled_rect = QRect(p1, p2)
            class_index = self.box_colors[i] if i < len(self.box_colors) else 0
            r, g, b, a = generate_color(class_index)
            color = QColor(r, g, b, a)
            painter.setPen(QPen(color, 2, Qt.SolidLine))
            painter.drawRect(scaled_rect)

        # Draw current box, scaled
        if self.drawing and self.start and self.end:
            painter.setPen(QPen(Qt.green, 2, Qt.DashLine))
            # Convert current start/end to image coords, then back to widget coords for scaling
            p1_img = self._to_image_coords(self.start)
            p2_img = self._to_image_coords(self.end)
            p1 = self._to_widget_coords(p1_img)
            p2 = self._to_widget_coords(p2_img)
            rect = QRect(p1, p2).normalized()
            painter.drawRect(rect)

    def get_bboxes(self):
        """Return bounding boxes as (x, y, w, h) in original image coordinates."""
        return [rect.getRect() for rect in self.boxes]

    def resizeEvent(self, event):
        if hasattr(self, "_pixmap") and self._pixmap:
            super().setPixmap(self._pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        super().resizeEvent(event)