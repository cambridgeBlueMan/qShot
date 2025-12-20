from qt import QtWidgets, Qt
from adjustments import AdjustmentsWidget
from res_combo import ResCombo
import subprocess
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

MINIMUM_WIDTH = 485

class ComponentBase(QtWidgets.QWidget):
    def __init__(
        self,
        cam=None,
        config_model=None,
        controls_model=None,
        paths_model=None,
        resolutions_model=None,
        parent=None,
        show_jpeg_quality=True,
        show_ae=True,
        show_resolution=True,
        show_adjustments=True,
        show_filename=True,
        show_terminal=True,
        **kwargs
    ):
        super().__init__(parent)
        self.setMinimumWidth(MINIMUM_WIDTH)
        self.cam = cam
        self.config_model = config_model
        self.controls_model = controls_model
        self.paths_model = paths_model
        self.resolutions_model = resolutions_model
        self.show_terminal = show_terminal  # <-- Add this line

        self.base_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.base_layout)

        # --- Common Controls Group (hidden by default, toggled by "more..." button) ---
        self.common_controls_group = QtWidgets.QGroupBox("Common Controls")
        self.common_controls_group.setVisible(False)
        group_layout = QtWidgets.QVBoxLayout()

        # --- JPEG Quality Slider ---
        if show_jpeg_quality:
            jpeg_layout = QtWidgets.QHBoxLayout()
            jpeg_label = QtWidgets.QLabel("JPEG Quality")
            self.jpeg_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
            self.jpeg_slider.setMinimum(self.controls_model._control_ranges["JpegQuality"][0])
            self.jpeg_slider.setMaximum(self.controls_model._control_ranges["JpegQuality"][1])
            self.jpeg_slider.setValue(self.controls_model.JpegQuality)
            self.jpeg_slider.setTickInterval(1)
            self.jpeg_value_label = QtWidgets.QLabel(str(self.controls_model.JpegQuality))
            jpeg_layout.addWidget(jpeg_label)
            jpeg_layout.addWidget(self.jpeg_slider)
            jpeg_layout.addWidget(self.jpeg_value_label)
            group_layout.addLayout(jpeg_layout)
            self.jpeg_slider.valueChanged.connect(self.on_jpeg_slider_changed)
            self.controls_model.JpegQualityChanged.connect(self.on_jpeg_quality_changed)

        # --- Automatic Exposure Control (AE) Checkbox ---
        if show_ae:
            ae_layout = QtWidgets.QHBoxLayout()
            self.ae_checkbox = QtWidgets.QCheckBox("Automatic Exposure Control (AE)")
            self.ae_checkbox.setChecked(self.controls_model.AeEnable)
            ae_layout.addWidget(self.ae_checkbox)
            group_layout.addLayout(ae_layout)
            self.ae_checkbox.stateChanged.connect(self.on_ae_checkbox_changed)
            self.controls_model.AeEnableChanged.connect(self.on_ae_enable_changed)

        # --- Select Resolution Row ---
        if show_resolution:
            res_layout = QtWidgets.QHBoxLayout()
            res_label = QtWidgets.QLabel("Select Resolution")
            self.res_combo = ResCombo(
                config_model=self.config_model,
                resolutions_model=self.resolutions_model
            )
            res_layout.addWidget(res_label)
            res_layout.addWidget(self.res_combo)
            group_layout.addLayout(res_layout)
            self.res_combo.currentIndexChanged.connect(self.set_size_in_config)

            # Set highest available mode at startup
            if hasattr(self.cam, "sensor_modes") and self.cam.sensor_modes:
                highest_mode_dict = self.cam.sensor_modes[-1]
                if self.config_model:
                    if 'size' in highest_mode_dict:
                        self.config_model.set_nested('sensor', 'output_size', highest_mode_dict['size'])
                    if 'bit_depth' in highest_mode_dict:
                        self.config_model.set_nested('sensor', 'bit_depth', highest_mode_dict['bit_depth'])
                self.res_combo.generateComboItems(highest_mode_dict)
                self.res_combo.set_largest_resolution()

        # --- Adjustments Widget ---
        if show_adjustments:
            self.adjustments_widget = AdjustmentsWidget(self.controls_model, mode="dials")
            group_layout.addWidget(self.adjustments_widget)

        # --- File Name Group Box ---
        if show_filename:
            filename_group = QtWidgets.QGroupBox("File name")
            filename_group.setStyleSheet("""
                QtWidgets.QGroupBox {
                    font-weight: bold;
                }
            """)
            filename_grid = QtWidgets.QGridLayout()
            filename_grid.addWidget(QtWidgets.QLabel("Image root:"), 0, 0)
            self.img_root = QtWidgets.QLineEdit(self.paths_model.rootnames.get("img", "img_"))
            filename_grid.addWidget(self.img_root, 0, 1)
            filename_grid.addWidget(QtWidgets.QLabel("Strategy:"), 1, 0)
            self.strategy = QtWidgets.QComboBox()
            self.strategy.addItems(["date", "sequence", "hash"])
            self.strategy.setCurrentText(self.paths_model.strategy)
            filename_grid.addWidget(self.strategy, 1, 1)
            self.preview_label = QtWidgets.QLabel(self.paths_model.generate_filename("img"))
            filename_grid.addWidget(self.preview_label, 2, 0, 1, 2)
            filename_group.setLayout(filename_grid)
            group_layout.addWidget(filename_group)

            self.img_root.editingFinished.connect(self._update_img_root_in_model)
            self.strategy.currentIndexChanged.connect(self._update_strategy_in_model)
            self.paths_model.pathsChanged.connect(self._update_from_model)

        # Connect config model signal
        if self.config_model:
            self.config_model.configChanged.connect(self.on_config_changed)

        self.common_controls_group.setLayout(group_layout)
        self.base_layout.addWidget(self.common_controls_group)

        # --- Terminal-like status window ---
        if show_terminal:
            self.terminal = QtWidgets.QTextBrowser(self)
            self.terminal.setReadOnly(True)
            self.terminal.setFixedHeight(100)  # ~4-5 lines
            self.terminal.setStyleSheet("""
                background-color: #222;
                color: #A8FF60;
                font-family: 'Fira Mono', 'Consolas', 'Monospace';
                font-size: 9pt;
                border: 1px solid #444;
            """)
            self.terminal.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.WidgetWidth)  # Enable wrapping
            self.terminal.setOpenExternalLinks(False)
            self.terminal.anchorClicked.connect(self.handle_terminal_link)
            self.base_layout.addWidget(self.terminal)
        self.base_layout.addStretch()

    # --- Common Signal Handlers ---
    def on_jpeg_slider_changed(self, value):
        self.controls_model.JpegQuality = value
        self.jpeg_value_label.setText(str(value))
        if hasattr(self.cam, "options") and isinstance(self.cam.options, dict):
            self.cam.options["quality"] = value

    def on_jpeg_quality_changed(self, value):
        self.jpeg_slider.setValue(value)
        self.jpeg_value_label.setText(str(value))

    def on_ae_checkbox_changed(self, state):
        self.controls_model.AeEnable = bool(state)

    def on_ae_enable_changed(self, value):
        self.ae_checkbox.setChecked(bool(value))

    def set_size_in_config(self, index):
        size = self.res_combo.itemData(index)
        if size and self.config_model and self.cam:
            self.config_model.set_nested('main', 'size', size)
            was_running = getattr(self.cam, 'started', False)
            if was_running:
                self.cam.stop()
            config_dict = self.config_model.to_dict()
            self.cam.configure(config_dict)
            # Apply persisted controls after configure
            controls_dict = self.controls_model.get_controls_dict()
            if controls_dict:
                self.cam.set_controls(controls_dict)
            if was_running:
                self.cam.start()

    def _update_from_model(self):
        if hasattr(self, "img_root") and self.img_root.text() != self.paths_model.rootnames.get("img", "img_"):
            self.img_root.blockSignals(True)
            self.img_root.setText(self.paths_model.rootnames.get("img", "img_"))
            self.img_root.blockSignals(False)
            self.preview_label.setText(self.paths_model.generate_filename("img"))
        if hasattr(self, "strategy") and self.strategy.currentText() != self.paths_model.strategy:
            self.strategy.blockSignals(True)
            self.strategy.setCurrentText(self.paths_model.strategy)
            self.strategy.blockSignals(False)
            self.preview_label.setText(self.paths_model.generate_filename("img"))

    def _update_img_root_in_model(self):
        img_root = self.img_root.text().strip() or "img_"
        if img_root != self.paths_model.rootnames.get("img", "img_"):
            self.paths_model.set_rootname("img", img_root)
        self.preview_label.setText(self.paths_model.generate_filename("img"))

    def _update_strategy_in_model(self, index):
        strategy_text = self.strategy.itemText(index)
        if strategy_text != self.paths_model.strategy:
            self.paths_model.set_strategy(strategy_text)
        self.preview_label.setText(self.paths_model.generate_filename("img"))

    def on_config_changed(self, cfg):
        was_running = getattr(self.cam, 'started', False)
        if was_running:
            self.cam.stop()
        self.cam.configure(cfg)
        # Apply persisted controls after configure
        controls_dict = self.controls_model.get_controls_dict()
        if controls_dict:
            self.cam.set_controls(controls_dict)
        if was_running:
            self.cam.start()

    def toggle_common_controls(self, checked):
        self.common_controls_group.setVisible(checked)
        if checked:
            self.more_button.setText("less")
        else:
            self.more_button.setText("more...")

    def append_terminal(self, text, color=None, clear=False, replace_last_line=False):
        """
        Append or update a line in the terminal window.
        - text: The message to display.
        - color: Optional text color (CSS string, e.g. '#A8FF60').
        - clear: If True, clear the terminal before adding.
        - replace_last_line: If True, replace the last line (for status/progress).
        """
        if clear:
            self.terminal.clear()
        if color:
            html = f'<span style="color:{color}">{text}</span>'
        else:
            html = text

        if replace_last_line:
            cursor = self.terminal.textCursor()
            cursor.movePosition(QtWidgets.QTextCursor.End)
            cursor.select(QtWidgets.QTextCursor.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deletePreviousChar()
            cursor.insertHtml(html)
            cursor.insertBlock()
        else:
            self.terminal.append(html)

    def handle_terminal_link(self, url):
        file_path = url.toLocalFile()
        from vlc_player_test import MainWindow as VLCPlayerWindow
        # Create and show the VLC player window
        self.vlc_window = VLCPlayerWindow(file_path)
        self.vlc_window.show()