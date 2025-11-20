import os
import hashlib
from datetime import datetime

from qt import QtWidgets, QtGui, QtCore, Qt
class PathsModel(QtCore.QObject):
    """
    Centralised path and filename model.
    Persisted with QSettings under group 'paths'.
    """
    pathsChanged = QtCore.pyqtSignal()
    sequenceChanged = QtCore.pyqtSignal(str, int)  # kind, new_sequence

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QtCore.QSettings("lea", "ai_capture")
        self._load_defaults()

    def _load_defaults(self):
        self.settings.beginGroup("paths")
        self.video_folder = self.settings.value("video_folder", os.path.expanduser("~/Videos"))
        self.still_folder = self.settings.value("still_folder", os.path.expanduser("~/Pictures"))
        self.rootnames = {
            "img": self.settings.value("img_root", "img_"),
            "vid": self.settings.value("vid_root", "vid_"),
        }
        # allowed extensions lists
        self.image_extensions = self.settings.value("image_extensions", ["jpg", "png"])
        self.video_extensions = self.settings.value("video_extensions", ["mp4", "h264"])
        # naming strategy: 'date' | 'sequence' | 'hash'
        self.strategy = self.settings.value("naming_strategy", "date")
        # per-kind sequence index
        self.sequences = {
            "img": int(self.settings.value("seq_img", 1)),
            "vid": int(self.settings.value("seq_vid", 1)),
        }
        self.settings.endGroup()

    def save(self):
        self.settings.beginGroup("paths")
        self.settings.setValue("video_folder", self.video_folder)
        self.settings.setValue("still_folder", self.still_folder)
        self.settings.setValue("img_root", self.rootnames["img"])
        self.settings.setValue("vid_root", self.rootnames["vid"])
        self.settings.setValue("image_extensions", self.image_extensions)
        self.settings.setValue("video_extensions", self.video_extensions)
        self.settings.setValue("naming_strategy", self.strategy)
        self.settings.setValue("seq_img", self.sequences["img"])
        self.settings.setValue("seq_vid", self.sequences["vid"])
        self.settings.endGroup()
        self.pathsChanged.emit()

    # folder setters
    def set_video_folder(self, path: str):
        self.video_folder = os.path.abspath(path)
        os.makedirs(self.video_folder, exist_ok=True)
        self.pathsChanged.emit()
        self.save()

    def set_still_folder(self, path: str):
        self.still_folder = os.path.abspath(path)
        os.makedirs(self.still_folder, exist_ok=True)
        self.pathsChanged.emit()
        self.save()

    # root name setters
    def set_rootname(self, kind: str, root: str):
        if kind in self.rootnames:
            self.rootnames[kind] = root
            self.pathsChanged.emit()
            self.save()

    def set_strategy(self, strategy: str):
        if strategy in ("date", "sequence", "hash"):
            self.strategy = strategy
            self.pathsChanged.emit()
            self.save()

    def set_extensions(self, kind: str, ext_list):
        if kind == "img":
            self.image_extensions = list(ext_list)
        elif kind == "vid":
            self.video_extensions = list(ext_list)
        self.pathsChanged.emit()
        self.save()

    def _next_sequence(self, kind: str) -> int:
        seq = self.sequences.get(kind, 1)
        self.sequences[kind] = seq + 1
        self.sequenceChanged.emit(kind, self.sequences[kind])
        self.save()
        return seq

    def _hash_name(self, base: str) -> str:
        h = hashlib.sha1(base.encode("utf-8")).hexdigest()[:10]
        return h

    def generate_filename(self, kind: str = "img", ext: str | None = None, use_root_override: str | None = None) -> str:
        """
        Generate a filename (without path) for kind 'img' or 'vid'.
        - ext: optional extension (e.g. 'jpg'). If None, picks first allowed ext.
        - naming strategies: 'date', 'sequence', 'hash'
        Returns: filename string (e.g. img_20251023-123001.jpg)
        Side-effect: increments sequence counter when strategy=='sequence'
        """
        kind = "img" if kind not in ("img", "vid") else kind
        if ext is None:
            ext = (self.image_extensions if kind == "img" else self.video_extensions)[0]
        ext = ext.lstrip(".")
        root = use_root_override if use_root_override is not None else self.rootnames.get(kind, f"{kind}_")

        if self.strategy == "date":
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            name = f"{root}{ts}"
        elif self.strategy == "sequence":
            seq = self._next_sequence(kind)
            name = f"{root}{seq:06d}"
        else:  # hash
            base = f"{root}{datetime.now().isoformat()}"
            name = f"{root}{self._hash_name(base)}"

        return f"{name}.{ext}"

    def get_folder_for_kind(self, kind: str) -> str:
        return self.still_folder if kind == "img" else self.video_folder

    def full_path(self, kind: str = "img", ext: str | None = None, use_root_override: str | None = None) -> str:
        fname = self.generate_filename(kind=kind, ext=ext, use_root_override=use_root_override)
        return os.path.join(self.get_folder_for_kind(kind), fname)

    # validation helpers
    def ensure_folders_exist(self):
        os.makedirs(self.video_folder, exist_ok=True)
        os.makedirs(self.still_folder, exist_ok=True)

    def to_dict(self):
        return {
            "video_folder": self.video_folder,
            "still_folder": self.still_folder,
            "rootnames": self.rootnames.copy(),
            "image_extensions": list(self.image_extensions),
            "video_extensions": list(self.video_extensions),
            "strategy": self.strategy,
            "sequences": dict(self.sequences),
        }