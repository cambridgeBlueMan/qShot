import random
import sys


from qt import QtWidgets, QtGui, QtCore, Qt
def random_color():
    """
    Generate a random QtGui.QColor object.

    Returns:
        QtGui.QColor: A color with random RGB values.
    """
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return QtGui.QColor(r, g, b)


class Color(QtWidgets.QWidget):
    """
    A QtWidgets.QWidget that displays a solid background color.
    """
    def __init__(self, color):
        """
        Initialize the Color widget.

        Args:
            color (QtGui.QColor or str): The color to use for the background.
        """
        super().__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QtGuiQPalette.ColorRole.Window, QtGui.QColor(color))
        self.setPalette(palette)


class Dummy(QtWidgets.QWidget):
    """
    A placeholder QtWidgets.QWidget with a colored background and a text label.
    """
    def __init__(self, color=None, text="Dummy"):
        """
        Initialize the Dummy widget.

        Args:
            color (QtGui.QColor, str, or None): The background color. If None, a random color is used.
            text (str): The text to display on the label.
        """
        super().__init__()
        self.setAutoFillBackground(True)
        if color is None:
            color = random_color()
        else:
            color = QtGui.QColor(color)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, color)
        self.setPalette(palette)
        self.label = QtWidgets.QLabel(self)
        self.label.setText(text)


if __name__ == "__main__":
    """
    Run a test window displaying a Dummy widget.
    """
    app = QtWidgets.QApplication(sys.argv)
    dummy = Dummy(text="Hello Dummy!")
    dummy.resize(200, 100)
    dummy.show()
    sys.exit(app.exec_())

