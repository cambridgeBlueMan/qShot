import os
import re

# Map class/function names to their qualified Qt module
qt_class_map = {
    # QtWidgets
    "QWidget": "QtWidgets",
    "QMainWindow": "QtWidgets",
    "QPushButton": "QtWidgets",
    "QLabel": "QtWidgets",
    "QApplication": "QtWidgets",
    "QDialog": "QtWidgets",
    "QLineEdit": "QtWidgets",
    "QComboBox": "QtWidgets",
    "QCheckBox": "QtWidgets",
    "QRadioButton": "QtWidgets",
    "QGroupBox": "QtWidgets",
    "QVBoxLayout": "QtWidgets",
    "QHBoxLayout": "QtWidgets",
    "QGridLayout": "QtWidgets",
    "QFormLayout": "QtWidgets",
    "QTabWidget": "QtWidgets",
    "QTableWidget": "QtWidgets",
    "QTableWidgetItem": "QtWidgets",
    "QTreeWidget": "QtWidgets",
    "QTreeWidgetItem": "QtWidgets",
    "QListWidget": "QtWidgets",
    "QListWidgetItem": "QtWidgets",
    "QSpinBox": "QtWidgets",
    "QDoubleSpinBox": "QtWidgets",
    "QSlider": "QtWidgets",
    "QScrollBar": "QtWidgets",
    "QFrame": "QtWidgets",
    "QMessageBox": "QtWidgets",
    "QFileDialog": "QtWidgets",
    "QColorDialog": "QtWidgets",
    "QFontDialog": "QtWidgets",
    "QStatusBar": "QtWidgets",
    "QMenuBar": "QtWidgets",
    "QMenu": "QtWidgets",
    "QAction": "QtWidgets",
    "QToolBar": "QtWidgets",
    "QProgressBar": "QtWidgets",
    "QPlainTextEdit": "QtWidgets",
    "QTextEdit": "QtWidgets",
    "QCalendarWidget": "QtWidgets",
    "QSplitter": "QtWidgets",
    "QStackedWidget": "QtWidgets",
    "QSizePolicy": "QtWidgets",
    "QDesktopWidget": "QtWidgets",
    "QCompleter": "QtWidgets",
    "QScrollArea": "QtWidgets",
    # QtGui
    "QPalette": "QtGui",
    "QColor": "QtGui",
    "QFont": "QtGui",
    "QIcon": "QtGui",
    "QPixmap": "QtGui",
    "QImage": "QtGui",
    "QPainter": "QtGui",
    "QPen": "QtGui",
    "QBrush": "QtGui",
    "QCursor": "QtGui",
    "QKeySequence": "QtGui",
    # QtCore
    "Qt": "QtCore",
    "QTimer": "QtCore",
    "QThread": "QtCore",
    "QEvent": "QtCore",
    "QSize": "QtCore",
    "QPoint": "QtCore",
    "QRect": "QtCore",
    "QDate": "QtCore",
    "QTime": "QtCore",
    "QDateTime": "QtCore",
    "QUrl": "QtCore",
    "QObject": "QtCore",
    "pyqtSignal": "QtCore",
    "pyqtSlot": "QtCore",
    # Add more as needed
}

qt_import_pattern = re.compile(
    r'from\s+PyQt[56]\.(QtWidgets|QtGui|QtCore|QtSvg|QtNetwork|QtPrintSupport|QtOpenGL|QtMultimedia|QtMultimediaWidgets|QtWebEngineWidgets|QtWebSockets|QtPositioning|QtQml|QtQuick|QtSql|QtTest|QtXml|QtXmlPatterns|Qt)\s+import\s+([^\n]+)'
)
qt_module_pattern = re.compile(
    r'import\s+PyQt[56]\.(QtWidgets|QtGui|QtCore|QtSvg|QtNetwork|QtPrintSupport|QtOpenGL|QtMultimedia|QtMultimediaWidgets|QtWebEngineWidgets|QtWebSockets|QtPositioning|QtQml|QtQuick|QtSql|QtTest|QtXml|QtXmlPatterns|Qt)'
)

def qualify_usage(line):
    # Only replace if not already qualified (e.g., not QtWidgets.QWidget)
    for cls, mod in qt_class_map.items():
        # Avoid replacing in comments or strings
        # Replace only if it's a standalone word (not part of another word)
        pattern = r'(?<![\w.])' + re.escape(cls) + r'(?![\w.])'
        repl = f"{mod}.{cls}"
        # Don't double-qualify
        if f"{mod}.{cls}" not in line:
            line = re.sub(pattern, repl, line)
    return line

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    changed = False
    new_lines = []
    shim_imported = False

    for line in lines:
        # Remove direct PyQt5/PyQt6 imports
        if qt_import_pattern.match(line) or qt_module_pattern.match(line):
            changed = True
            continue
        # Detect if qt shim is already imported
        if re.match(r'from\s+qt\s+import', line):
            shim_imported = True
        new_lines.append(line)

    # If we removed any PyQt import, add the shim import at the top (after stdlib imports)
    if changed and not shim_imported:
        insert_at = 0
        for idx, line in enumerate(new_lines):
            if line.strip() and not line.startswith('import') and not line.startswith('from'):
                insert_at = idx
                break
        new_lines.insert(insert_at, 'from qt import QtWidgets, QtGui, QtCore, Qt\n')

    # Now, qualify usage throughout the file
    qualified_lines = []
    for line in new_lines:
        # Don't qualify import lines or comments
        if line.strip().startswith('import') or line.strip().startswith('from') or line.strip().startswith('#'):
            qualified_lines.append(line)
        else:
            qualified_lines.append(qualify_usage(line))

    if changed or qualified_lines != lines:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(qualified_lines)
        print(f"Updated: {filepath}")

def update_project(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py') and filename != 'qt.py' and filename != os.path.basename(__file__):
                update_file(os.path.join(dirpath, filename))

if __name__ == "__main__":
    # Change '.' to your project root if needed
    update_project('.')