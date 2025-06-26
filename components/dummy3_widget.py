from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QLabel, QWidget, QApplication
import random
import sys


def random_color():
    """
    Generate a random QColor object.

    Returns:
        QColor: A color with random RGB values.
    """
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return QColor(r, g, b)


class Color(QWidget):
    """
    A QWidget that displays a solid background color.
    """
    def __init__(self, color):
        """
        Initialize the Color widget.

        Args:
            color (QColor or str): The color to use for the background.
        """
        super().__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class Dummy3(QWidget):
    """
    A placeholder QWidget with a colored background and a text label.
    """
    def __init__(self, color=None, text="Dummy3"):
        """
        Initialize the Dummy widget.

        Args:
            color (QColor, str, or None): The background color. If None, a random color is used.
            text (str): The text to display on the label.
        """
        super().__init__()
        self.setAutoFillBackground(True)
        if color is None:
            color = random_color()
        else:
            color = QColor(color)
        palette = self.palette()
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)
        self.label = QLabel(self)
        self.label.setText(text)


if __name__ == "__main__":
    """
    Run a test window displaying a Dummy widget.
    """
    app = QApplication(sys.argv)
    dummy = Dummy3(text="Hello Dummy!")
    dummy.resize(200, 100)
    dummy.show()
    sys.exit(app.exec_())

