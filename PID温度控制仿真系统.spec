# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\SimControl\\src\\main.py'],
    pathex=['C:\\SimControl\\src'],
    binaries=[],
    datas=[('C:\\SimControl\\assets', 'assets')],
    hiddenimports=['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'PyQt5.sip', 'pyqtgraph', 'pyqtgraph.graphicsItems', 'pyqtgraph.widgets', 'control', 'model', 'ui', 'user', 'utils'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PID温度控制仿真系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PID温度控制仿真系统',
)
