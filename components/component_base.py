from PyQt5.QtWidgets import QWidget

class ComponentBase(QWidget):
    """
    Base class for all component widgets.
    Ensures a cleanup method is available for housekeeping.
    """
    def cleanup(self):
        """
        Cleanup resources, disconnect signals, stop timers, etc.
        Should be implemented by all subclasses.
        """
        raise NotImplementedError("cleanup() must be implemented by subclasses.")