from qt import QtWidgets

class ResolutionsEditor(QtWidgets.QDialog):
    def __init__(self, resolutions_model):
        super().__init__()
        self.setWindowTitle("Resolutions Editor")
        self.resolutions_model = resolutions_model

        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Width", "Height"])
        layout.addWidget(self.table)

        self.load_resolutions()

        btn_row = QtWidgets.QHBoxLayout()
        add_btn = QtWidgets.QPushButton("Add")
        del_btn = QtWidgets.QPushButton("Delete")
        save_btn = QtWidgets.QPushButton("Save")
        btn_row.addWidget(add_btn)
        btn_row.addWidget(del_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

        add_btn.clicked.connect(self.add_row)
        del_btn.clicked.connect(self.delete_selected)
        save_btn.clicked.connect(self.save_resolutions)

        self.resize(400, 300)

    def load_resolutions(self):
        resolutions = self.resolutions_model.get_resolutions()
        self.table.setRowCount(len(resolutions))
        for row, (name, size) in enumerate(resolutions):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(name)))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(size[0])))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(size[1])))

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QtWidgets.QTableWidgetItem("New"))
        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem("640"))
        self.table.setItem(row, 2, QtWidgets.QTableWidgetItem("480"))

    def delete_selected(self):
        selected = self.table.selectionModel().selectedRows()
        for index in sorted(selected, key=lambda x: x.row(), reverse=True):
            self.table.removeRow(index.row())

    def save_resolutions(self):
        resolutions = []
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text()
            try:
                width = int(self.table.item(row, 1).text())
                height = int(self.table.item(row, 2).text())
                resolutions.append((name, (width, height)))
            except Exception:
                continue
        self.resolutions_model.set_resolutions(resolutions)
        self.accept()