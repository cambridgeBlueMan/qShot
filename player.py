from PyQt6 import QtCore as qtc
import math
from typing import Any, Callable, Dict, Optional

DEFAULT_STEPS_PER_SECOND = 30

class Player(qtc.QThread):
    """
    Player: interpolate numeric control state between two model rows over time.

    High-level purpose
    - Interpolates numeric control values (e.g. ScalerCrop x,y,w,h) between a START row
      and an END row in a table model over a configured duration.
    - Emits `state` signal each step with the interpolated numeric values (floats).
    - Emits `progress` (0.0..1.0), `finished` and `stopped` to indicate lifecycle.
    - Designed to run in its own QThread; heavy work kept here, but all camera/control
      writes should be performed on the main thread by connecting to `state`.

    Signals
    - state(dict): emitted each step with numeric control values (floats). Connect in GUI thread.
    - progress(float): emitted with progress fraction 0.0 -> 1.0.
    - finished(): emitted when run completes normally.
    - stopped(): emitted when stopped early via stop().

    Constructor parameters
    - model: QAbstractTableModel-like object exposing index(row,col), data(index,...),
             and optionally ._data or .zoomData(row, startOnly=True).
    - apply_fn: optional callable(state:dict) kept for convenience; DO NOT rely on it
                to run in main thread (prefer connecting to state).
    - start_row, end_row: integers indices in model.
    - duration_getter: optional callable(row)->float seconds; used as fallback for duration.
    - steps_per_second: target number of interpolation steps per second (int >= 1, default DEFAULT_STEPS_PER_SECOND).
    """

    # Signals
    progress = qtc.pyqtSignal(float)
    finished = qtc.pyqtSignal()
    stopped = qtc.pyqtSignal()
    state = qtc.pyqtSignal(dict)

    def __init__(
        self,
        model: Any,
        apply_fn: Optional[Callable[[Dict[str, float]], None]],
        start_row: int,
        end_row: int,
        *,
        duration_getter: Optional[Callable[[int], float]] = None,
        steps_per_second: int = DEFAULT_STEPS_PER_SECOND,
        parent: Optional[qtc.QObject] = None
    ):
        super().__init__(parent)
        self.model = model
        self.apply_fn = apply_fn
        self.start_row = int(start_row)
        self.end_row = int(end_row)
        self.steps_per_second = max(1, int(steps_per_second))
        self._running = True
        # duration_getter(row) -> seconds; fallback tries to read column 4
        self.duration_getter = duration_getter or (lambda r: float(self._row_value(r, 4) or 1.0))

    def stop(self) -> None:
        """Request the player to stop as soon as possible."""
        self._running = False

    def _row_value(self, row: int, col: int):
        """
        Best-effort helper to read a model value.
        - tries model.data(index, DisplayRole)
        - falls back to model._data[row][col] if available
        """
        try:
            idx = self.model.index(row, col)
            # Use DisplayRole for stable textual/numeric retrieval from model.data()
            return self.model.data(idx, qtc.QModelIndex().DisplayRole)
        except Exception:
            try:
                return self.model._data[row][col]
            except Exception:
                return None

    def _row_controls(self, row: int) -> Dict[str, float]:
        """
        Return a numeric control dictionary for the given row.
        Expected layout for zoom rows: [x, y, w, h, duration, pause]
        Returns floats for x,y,w,h,duration,pause (missing keys omitted).
        """
        try:
            if hasattr(self.model, "zoomData"):
                d = self.model.zoomData(row, startOnly=True)
                return {
                    "x": float(d[0]), "y": float(d[1]),
                    "w": float(d[2]), "h": float(d[3]),
                    "duration": float(d[4]) if len(d) > 4 else self.duration_getter(row),
                    "pause": float(d[5]) if len(d) > 5 else 0.0
                }
        except Exception:
            pass

        # Generic fallback to _data layout
        try:
            rowdata = list(self.model._data[row])
            return {
                "x": float(rowdata[0]), "y": float(rowdata[1]),
                "w": float(rowdata[2]), "h": float(rowdata[3]),
                "duration": float(rowdata[4]) if len(rowdata) > 4 else self.duration_getter(row),
                "pause": float(rowdata[5]) if len(rowdata) > 5 else 0.0
            }
        except Exception:
            return {}

    @staticmethod
    def _interp_dict(a: Dict[str, float], b: Dict[str, float], t: float) -> Dict[str, float]:
        """
        Linear interpolation between two dicts a and b at fraction t in [0,1].
        Missing keys treated as 0.0.
        """
        keys = set(a) | set(b)
        return {k: (a.get(k, 0.0) + (b.get(k, 0.0) - a.get(k, 0.0)) * t) for k in keys}

    def run(self) -> None:
        """
        Thread entrypoint.
        - measures elapsed time with QElapsedTimer to avoid drift.
        - computes t = elapsed / duration and emits intermediate states at target steps_per_second.
        - emits final state and finished() unless stopped.
        """
        self._running = True
        start = self._row_controls(self.start_row)
        end = self._row_controls(self.end_row)
        duration = start.get("duration", self.duration_getter(self.start_row) or 1.0)
        if not duration or duration <= 0:
            duration = 1.0

        # High resolution elapsed timer
        timer = qtc.QElapsedTimer()
        timer.start()
        step_ms = int(1000 / self.steps_per_second)

        while self._running:
            elapsed_ms = timer.elapsed()
            t = min(1.0, elapsed_ms / (duration * 1000.0))
            current = self._interp_dict(start, end, t)

            # Emit interpolated state for main-thread application
            try:
                self.state.emit(current)
            except Exception:
                pass

            # Optional convenience: call apply_fn (but callers should prefer state signal)
            try:
                if self.apply_fn is not None:
                    self.apply_fn(current)
            except Exception:
                pass

            try:
                self.progress.emit(t)
            except Exception:
                pass

            if t >= 1.0:
                break

            qtc.QThread.msleep(step_ms)

        if not self._running:
            self.stopped.emit()
            return

        # Ensure final state and signals
        try:
            self.state.emit(end)
        except Exception:
            pass
        try:
            self.progress.emit(1.0)
        except Exception:
            pass
        self.finished.emit()