# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('C:\\SimControl\\assets', 'assets')]
binaries = [('C:\\Users\\94691\\AppData\\Local\\conda\\conda\\envs\\sim_env\\Library\\bin\\ffi-8.dll', '.'), ('C:\\Users\\94691\\AppData\\Local\\conda\\conda\\envs\\sim_env\\Library\\bin\\ffi-7.dll', '.'), ('C:\\Users\\94691\\AppData\\Local\\conda\\conda\\envs\\sim_env\\Library\\bin\\ffi.dll', '.'), ('C:\\Users\\94691\\AppData\\Local\\conda\\conda\\envs\\sim_env\\Library\\bin\\libexpat.dll', '.')]
hiddenimports = ['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'PyQt5.sip', 'pyqtgraph', 'pyqtgraph.graphicsItems', 'pyqtgraph.widgets', 'control', 'model', 'ui', 'user', 'utils', 'openpyxl', 'xml.parsers.expat', 'pyexpat', 'xml.etree.ElementTree']
tmp_ret = collect_all('openpyxl')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('et_xmlfile')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['C:\\SimControl\\src\\main.py'],
    pathex=['C:\\SimControl\\src'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    a.binaries,
    a.datas,
    [],
    name='PID温度控制仿真系统',
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
