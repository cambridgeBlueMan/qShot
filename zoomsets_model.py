from PyQt6 import QtCore
import csv

class ZoomsetsModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._headers = ["X", "Y", "width", "height", "speed", "pause"]
        self.dirty = False
        self._data = []
        self.filename = "zoomsets.csv"  # Default filename, can be changed

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._headers)

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if role in (QtCore.Qt.ItemDataRole.DisplayRole, QtCore.Qt.ItemDataRole.EditRole):
            value = self._data[index.row()][index.column()]
            if isinstance(value, float):
                return "%.6f" % value
            else:
                return value

    def zoomData(self, row, startOnly=False):
        thisLoop = []
        for n in range(0, 6):
            thisLoop.append(self._data[row][n])
        if not startOnly and row + 1 < len(self._data):
            for n in range(0, 4):
                thisLoop.append(self._data[row + 1][n])
        return tuple(thisLoop)

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Orientation.Horizontal and role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self._headers[section]
        else:
            return super().headerData(section, orientation, role)

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        self._data.sort(key=lambda x: x[column])
        if order == QtCore.Qt.SortOrder.DescendingOrder:
            self._data.reverse()
        self.layoutChanged.emit()

    def flags(self, index):
        return super().flags(index) | QtCore.Qt.ItemFlag.ItemIsEditable

    def setData(self, index, value, role=QtCore.Qt.ItemDataRole.EditRole):
        if index.isValid() and role == QtCore.Qt.ItemDataRole.EditRole:
            if index.column() == 4:  # speed
                try:
                    value = int(value)
                except Exception:
                    value = 1
                value = max(1, min(value, 100))
            if index.column() == 5:  # pause
                try:
                    value = float(value)
                except Exception:
                    value = 1.0
                value = min(value, 10)
                value = "%.2f" % value
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [role])
            self.dirty = True
            return True
        else:
            return False

    def insertRows(self, position, rows, parent=QtCore.QModelIndex(), zdata=None):
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):
            if zdata is not None:
                self._data.insert(position, zdata)
            else:
                self._data.insert(position, [''] * len(self._headers))
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)
        for i in range(rows):
            del self._data[position]
        self.endRemoveRows()
        return True

    def save_data(self):
        with open(self.filename, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            writer.writerow(self._headers)
            writer.writerows(self._data)