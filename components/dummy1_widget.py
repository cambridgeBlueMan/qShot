from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QLabel, QWidget, QApplication, QMessageBox
import random
import sys
import os
import importlib.util
import logging


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


class Dummy1(QWidget):
    """
    A placeholder QWidget with a colored background and a text label.
    """
    def __init__(self, color=None, text="Dummy1"):
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


class ComponentLoader(QWidget):
    """
    A QWidget that can load and display other components/widgets dynamically.
    """
    def __init__(self):
        super().__init__()

    def load_component_widget(self):
        action = self.sender()
        name = action.data()
        module_name = f"{name}_widget"
        module_path = os.path.join(os.path.dirname(__file__), "components", f"{module_name}.py")
        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            class_name = name.capitalize()
            widget_class = getattr(module, class_name)
            widget_instance = widget_class()
            widget_instance.setWindowTitle(class_name)
            widget_instance.show()  # Explicitly show the widget
            logging.info(f"Instantiated and showed widget: {class_name}")
        except Exception as e:
            logging.error(f"Failed to load or instantiate {class_name} from {module_name}: {e}")
            QMessageBox.critical(self, "Error", f"Could not load component '{class_name}':\n{e}")


if __name__ == "__main__":
    """
    Run a test window displaying a Dummy widget.
    """
    app = QApplication(sys.argv)
    dummy = Dummy1(text="Hello Dummy!")
    dummy.resize(200, 100)
    dummy.show()
    sys.exit(app.exec_())

