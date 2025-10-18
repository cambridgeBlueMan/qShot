from PyQt6 import QtCore as qtc
import time
import math

class Player(qtc.QThread):
    """
    Generic player: interpolate between two control states over time.
    - model: zoomsets_model (QAbstractTableModel or similar) OR direct data access function
    - apply_fn: callable(control_dict) -> applies controls (e.g., controls_model or cam)
    - start_row, end_row: indices in the model
    - fps: sample rate for interpolation
    """
    progress = qtc.pyqtSignal(float)   # 0.0..1.0
    finished = qtc.pyqtSignal()
    stopped = qtc.pyqtSignal()

    def __init__(self, model, apply_fn, start_row, end_row, *,
                 duration_getter=None, fps=30, parent=None):
        super().__init__(parent)
        self.model = model
        self.apply_fn = apply_fn
        self.start_row = int(start_row)
        self.end_row = int(end_row)
        self.fps = int(fps)
        self._running = True
        # duration_getter(row) -> float seconds (if None, attempt to read duration from model row index 4)
        self.duration_getter = duration_getter or (lambda r: float(self._row_value(r, 4) or 1.0))

    def stop(self):
        self._running = False

    def _row_value(self, row, col):
        try:
            idx = self.model.index(row, col)
            return self.model.data(idx, qtc.QModelIndex().DisplayRole)  # fallback
        except Exception:
            # try internal data access
            try:
                return self.model._data[row][col]
            except Exception:
                return None

    def _row_controls(self, row):
        """
        Return a flat dict of numeric controls for a given row.
        For zoom tables we expect x,y,width,height,duration,pause. Adapt as needed.
        """
        # Try to use zoomData if available (older zoomTab used zoomData to return start & end)
        if hasattr(self.model, "zoomData"):
            # zoomData(row, startOnly=True) should return (x,y,w,h,duration,pause)
            try:
                d = self.model.zoomData(row, startOnly=True)
                return {
                    "x": float(d[0]),
                    "y": float(d[1]),
                    "w": float(d[2]),
                    "h": float(d[3]),
                    "duration": float(d[4]) if len(d) > 4 else self.duration_getter(row),
                    "pause": float(d[5]) if len(d) > 5 else 0.0
                }
            except Exception:
                pass
        # Generic fallback to _data list structure [x,y,w,h,duration,pause]
        try:
            rowdata = list(self.model._data[row])
            return {
                "x": float(rowdata[0]),
                "y": float(rowdata[1]),
                "w": float(rowdata[2]),
                "h": float(rowdata[3]),
                "duration": float(rowdata[4]) if len(rowdata) > 4 else self.duration_getter(row),
                "pause": float(rowdata[5]) if len(rowdata) > 5 else 0.0
            }
        except Exception:
            return {}

    def _interp_dict(self, a, b, t):
        return {k: (a.get(k, 0.0) + (b.get(k, 0.0) - a.get(k, 0.0)) * t) for k in set(a) | set(b)}

    def run(self):
        self._running = True
        # load start/end control sets
        start = self._row_controls(self.start_row)
        end = self._row_controls(self.end_row)
        duration = start.get("duration", self.duration_getter(self.start_row))
        # if end row has own duration, you may prefer one or the other; use start by default
        if duration is None or duration <= 0:
            duration = 1.0
        steps = max(1, int(math.ceil(duration * self.fps)))
        interval = duration / steps

        for i in range(steps + 1):
            if not self._running:
                self.stopped.emit()
                return
            t = i / float(steps)
            current = self._interp_dict(start, end, t)
            # convert to camera control dict if needed (example ScalerCrop)
            # For zoom use ScalerCrop = [x, y, int(w), int(h)]
            try:
                # if apply_fn accepts dict of low-level camera controls, pass appropriate mapping
                self.apply_fn(current)
            except Exception:
                # swallow apply errors but continue
                pass
            self.progress.emit(t)
            # sleep using msleep to be cooperative in Qt
            qtc.QThread.msleep(int(interval * 1000))
        self.finished.emit()