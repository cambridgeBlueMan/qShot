# README: Global Mode Change Handling with `app_signals.py`

## Overview

This project uses a **central signal manager** (`app_signals.py`) to broadcast camera mode changes throughout the application.  
Any widget or component can emit a mode change, and any interested widget can listen for and respond to these changes.  
This approach keeps your code decoupled, maintainable, and ensures all relevant UI elements stay in sync.

---

## How It Works

### 1. `app_signals.py`

This file defines a singleton `AppSignals` object with a `mode_changed` signal:

```python
# app_signals.py
from PyQt6.QtCore import QObject, pyqtSignal

class AppSignals(QObject):
    mode_changed = pyqtSignal(object)  # Pass mode info (dict, index, etc.)

app_signals = AppSignals()
```

- **`mode_changed`**: Emitted whenever the camera mode changes anywhere in the app.

---

### 2. Emitting Mode Changes

Any widget can emit a mode change using:

```python
from app_signals import app_signals

# Emit a new mode (could be a dict, index, etc.)
app_signals.mode_changed.emit(new_mode)
```

Typically, this is done in the handler for a mode dropdown:

```python
def _on_mode_changed(self, index):
    mode = self.camera_mode_combo.itemData(index)
    app_signals.mode_changed.emit(mode)
```

---

### 3. Listening for Mode Changes

Any widget that needs to react to mode changes should **connect** to the signal in its `__init__`:

```python
from app_signals import app_signals

class MyWidget(QWidget):
    def __init__(self, ...):
        super().__init__(...)
        app_signals.mode_changed.connect(self.on_global_mode_changed)

    def on_global_mode_changed(self, mode):
        # Update UI or internal state based on new mode
        print(f"Mode changed to: {mode}")
```

---

## Functions to Add to Each File

### **1. Import and Connect in Each Widget**

- **Import the signal manager:**
  ```python
  from app_signals import app_signals
  ```

- **Connect the signal in `__init__`:**
  ```python
  app_signals.mode_changed.connect(self.on_global_mode_changed)
  ```

- **Define the handler:**
  ```python
  def on_global_mode_changed(self, mode):
      # Update UI or internal state
      pass
  ```

### **2. Emit the Signal When Mode Changes**

- In the widget that controls the mode (e.g., CameraManager):
  ```python
  def _on_mode_changed(self, index):
      mode = self.camera_mode_combo.itemData(index)
      app_signals.mode_changed.emit(mode)
  ```

---

## Example Integration

**CameraManager:**
```python
from app_signals import app_signals

class CameraManager(QWidget):
    def __init__(self, ...):
        # ...
        self.camera_mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        app_signals.mode_changed.connect(self._set_mode_from_signal)

    def _on_mode_changed(self, index):
        mode = self.camera_mode_combo.itemData(index)
        app_signals.mode_changed.emit(mode)

    def _set_mode_from_signal(self, mode):
        idx = self.camera_mode_combo.findData(mode)
        if idx != -1 and idx != self.camera_mode_combo.currentIndex():
            self.camera_mode_combo.setCurrentIndex(idx)
```

**Classifier:**
```python
from app_signals import app_signals

class Classifier(AIFileManager):
    def __init__(self, ...):
        # ...
        app_signals.mode_changed.connect(self.on_global_mode_changed)

    def on_global_mode_changed(self, mode):
        # React to mode change
        pass
```

**Zoomer:**
```python
from app_signals import app_signals

class Zoomer(qtw.QWidget):
    def __init__(self, ...):
        # ...
        app_signals.mode_changed.connect(self.on_global_mode_changed)

    def on_global_mode_changed(self, mode):
        # React to mode change
        pass
```

---

## Summary

- **`app_signals.py`** provides a global `mode_changed` signal.
- **Emit** the signal when the mode changes.
- **Connect** to the signal in any widget that needs to react.
- **Implement** a handler to update UI or state as needed.

This pattern ensures all parts of your app stay in sync with mode changes, no matter where