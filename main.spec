# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('components', 'components'), ('ai_file_manager_base.py', '.'), ('app_signals.py', '.'), ('autofocus_widget.py', '.'), ('base_control_widget.py', '.'), ('config_model.py', '.'), ('controls_gui.py', '.'), ('controls_model.py', '.'), ('dummy.py', '.'), ('examine_properties.py', '.'), ('get_modes.py', '.'), ('main_window.py', '.'), ('paths_model.py', '.'), ('paths_widget.py', '.'), ('player.py', '.'), ('res_combo.py', '.'), ('setup_app.py', '.'), ('temp.py', '.'), ('tes_camera_0.py', '.'), ('viewport.py', '.'), ('zoomer.py', '.'), ('zoomsets_model.py', '.')]
binaries = []
hiddenimports = ['av.bytesource', 'av.dictionary', 'av.container.pyio', 'av.utils', 'av.opaque', 'uuid', 'av.video.reformatter', 'OpenGL.platform.egl', 'OpenGL.arrays.strings']
tmp_ret = collect_all('picamera2')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
