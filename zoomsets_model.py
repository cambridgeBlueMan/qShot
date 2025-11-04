from qt import QtCore
import csv

DEFAULT_DURATION = 8.0
DEFAULT_PAUSE = 1.0

class ZoomsetsModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._headers = ["X", "Y", "width", "height", "duration", "pause"]
        self.dirty = False
        self._data = []
        self.filename = "zoomsets.csv"  # Default filename, can be changed

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._headers)

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        value = self._data[index.row()][index.column()]
        if role in (QtCore.Qt.ItemDataRole.DisplayRole, QtCore.Qt.ItemDataRole.EditRole):
            col = index.column()
            if col == 4:  # duration
                try:
                    return f"{float(value):.2f}"
                except Exception:
                    return value
            if col == 5:  # pause
                try:
                    return f"{float(value):.2f}"
                except Exception:
                    return value
            return value
        return None

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Orientation.Horizontal and role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self._headers[section]
        return super().headerData(section, orientation, role)

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags
        return super().flags(index) | QtCore.Qt.ItemFlag.ItemIsEditable | QtCore.Qt.ItemFlag.ItemIsSelectable

    def setData(self, index, value, role=QtCore.Qt.ItemDataRole.EditRole):
        if not index.isValid() or role != QtCore.Qt.ItemDataRole.EditRole:
            return False

        col = index.column()
        if col == 4:
            try:
                val = float(value)
            except Exception:
                val = DEFAULT_DURATION
            val = max(0.01, min(val, 3600.0))
            self._data[index.row()][col] = val
        elif col == 5:
            try:
                val = float(value)
            except Exception:
                val = DEFAULT_PAUSE
            val = max(0.0, min(val, 600.0))
            self._data[index.row()][col] = val
        else:
            try:
                if isinstance(self._data[index.row()][col], int):
                    self._data[index.row()][col] = int(value)
                else:
                    self._data[index.row()][col] = value
            except Exception:
                self._data[index.row()][col] = value

        self.dataChanged.emit(index, index, [role])
        self.dirty = True
        return True

    def insertRows(self, position, rows, parent=QtCore.QModelIndex(), zdata=None):
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):
            if zdata is not None:
                row = list(zdata)
                if len(row) > 4:
                    try:
                        row[4] = float(row[4])
                    except Exception:
                        row[4] = DEFAULT_DURATION
                if len(row) > 5:
                    try:
                        row[5] = float(row[5])
                    except Exception:
                        row[5] = DEFAULT_PAUSE
                while len(row) < len(self._headers):
                    row.append('')
                self._data.insert(position, row)
            else:
                default_row = ['', '', '', '', DEFAULT_DURATION, DEFAULT_PAUSE]
                self._data.insert(position, default_row)
        self.endInsertRows()
        self.dirty = True
        return True

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)
        for i in range(rows):
            if 0 <= position < len(self._data):
                del self._data[position]
        self.endRemoveRows()
        self.dirty = True
        return True

    def zoomData(self, row, startOnly=False):
        if not (0 <= row < len(self._data)):
            return ()
        this = self._data[row]
        result = []
        for n in range(min(6, len(this))):
            result.append(this[n])
        if not startOnly and row + 1 < len(self._data):
            nxt = self._data[row + 1]
            for n in range(0, min(4, len(nxt))):
                result.append(nxt[n])
        return tuple(result)

    def save_data(self):
        try:
            with open(self.filename, 'w', newline='', encoding='utf-8') as fh:
                writer = csv.writer(fh)
                writer.writerow(self._headers)
                for row in self._data:
                    out = list(row)
                    if len(out) > 4:
                        try:
                            out[4] = float(out[4])
                        except Exception:
                            out[4] = DEFAULT_DURATION
                    if len(out) > 5:
                        try:
                            out[5] = float(out[5])
                        except Exception:
                            out[5] = DEFAULT_PAUSE
                    writer.writerow(out)
        except Exception:
            pass