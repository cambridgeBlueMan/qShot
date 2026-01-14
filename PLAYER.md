# Player (architecture and usage)

## Purpose
The Player is a reusable component that interpolates numeric control values between two rows of a table-model over a specified duration. It's intended to drive camera control changes (for example, moving a ScalerCrop rectangle over time) and is designed to be generic so other control streams can reuse it.

## Key points
- The Player runs in its own QThread.
- It computes an interpolated numeric dictionary each step and emits it via the `state` signal.
- Camera or ControlsModel updates must be performed on the main (GUI) thread — connect `state` to a slot in the Zoomer or ControlsModel that applies the values.
- Player also emits `progress` (0..1), `finished`, and `stopped`.

## Signals
- state(dict): emitted each step; contains numeric keys such as `x`, `y`, `w`, `h`, `duration`, `pause`.
- progress(float): interpolation fraction.
- finished(): emitted when interpolation completes.
- stopped(): emitted if stopped early.

## Interpolation behavior
- Linear interpolation per-key between start and end values.
- Timing driven by a high-resolution timer (QElapsedTimer) to reduce drift.
- Steps are emitted at a target rate (`steps_per_second`, default 30). You can increase to 60 for smoother motion but ensure control application can keep up.

## Thread-safety / application rules
- Do not perform UI updates or camera writes directly from other threads. Connect `state` to a main-thread slot that converts floats to hardware-friendly types (integers for pixel coords) and calls ControlsModel or camera APIs.
- The Player optionally accepts an `apply_fn` but it may be called from the thread — prefer the `state` signal.

## Typical usage (Zoomer)
1. Create Player with model, optional apply_fn, start_row, end_row:
   ```python
   player = Player(zoomsets_model, None, start_row, end_row, steps_per_second=30)
   ```
2. Connect state to a main-thread slot:
   ```python
   player.state.connect(lambda st: controls_model.ScalerCrop = (int(st['x']), int(st['y']), int(st['w']), int(st['h'])))
   ```
3. Connect progress/finished/stopped for UI updates.
4. Start the player:
   ```python
   player.start()
   ```
5. Stop via `player.stop()` when needed.

## Next-step improvements
- Add easing functions (linear, ease-in/out).
- Add per-key interpolation types (e.g., step for discrete controls).
- Add arbitration if multiple players update the same control (priority, locking).
- Throttle writes or apply only when values change beyond a threshold to reduce control write load.
- Support looping, ping-pong, and sequences of multiple rows.

## Troubleshooting judder
- Ensure camera/control writes are performed on the main thread and are fast.
- Reduce steps_per_second or increase duration if control updates are slow.
- Throttle updates (apply only when state differs sufficiently).

## Keyboard Shortcuts (Video Player)
- Space: Toggle play/pause
- Left/Right: Seek backward/forward 5s
- Ctrl+Left/Right: Seek backward/forward 10s
- Home/End: Jump to start/end
- Esc: Exit back to preview view

Notes:
- The position slider clamps within the media length and updates during playback.
- At end-of-media, playback stops, the slider resets, and play-state signals update.