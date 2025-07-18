from PyQt6.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout
import sys

class ControlCamera(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel("Hello everybody!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        layout.addWidget(label)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ControlCamera()
    window.show()
    sys.exit(app.exec_())