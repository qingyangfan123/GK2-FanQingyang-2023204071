"""一键打包脚本（PyInstaller）"""
import subprocess
import sys
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src')

# 优先使用 sim_env 的 Python，避免 base 环境（Python 3.6）缺少依赖
_SIM_ENV_PYTHON = r'C:\Users\94691\AppData\Local\conda\conda\envs\sim_env\python.exe'
PYTHON = _SIM_ENV_PYTHON if os.path.exists(_SIM_ENV_PYTHON) else sys.executable
ASSETS = os.path.join(ROOT, 'assets')
MAIN = os.path.join(SRC, 'main.py')
SPEC = os.path.join(ROOT, 'PID温度控制仿真系统.spec')
BUILD = os.path.join(ROOT, 'build')

# 清理旧缓存，避免 PyInstaller 复用过期分析结果
for path in (SPEC, BUILD):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
            print(f'已删除目录：{path}')
        else:
            os.remove(path)
            print(f'已删除文件：{path}')

cmd = [
    PYTHON, '-m', 'PyInstaller',
    '--onedir',
    '--windowed',
    '--clean',
    '--name', 'PID温度控制仿真系统',
    '--distpath', os.path.join(ROOT, 'dist'),
    '--workpath', BUILD,
    '--specpath', ROOT,
    f'--add-data={ASSETS}{os.pathsep}assets',
    f'--paths={SRC}',
    # PyQt5 隐式导入
    '--hidden-import=PyQt5',
    '--hidden-import=PyQt5.QtCore',
    '--hidden-import=PyQt5.QtGui',
    '--hidden-import=PyQt5.QtWidgets',
    '--hidden-import=PyQt5.sip',
    # pyqtgraph 隐式导入
    '--hidden-import=pyqtgraph',
    '--hidden-import=pyqtgraph.graphicsItems',
    '--hidden-import=pyqtgraph.widgets',
    # 项目模块隐式导入
    '--hidden-import=control',
    '--hidden-import=model',
    '--hidden-import=ui',
    '--hidden-import=user',
    '--hidden-import=utils',
    MAIN,
]

print('开始打包...')
result = subprocess.run(cmd, cwd=ROOT)
if result.returncode == 0:
    # 手动将 ffi DLL 复制到 _internal 目录（PyInstaller 无法自动收集 conda Library/bin 下的 DLL）
    _internal = os.path.join(ROOT, 'dist', 'PID温度控制仿真系统', '_internal')
    _ffi_src = r'C:\Users\94691\AppData\Local\conda\conda\envs\sim_env\Library\bin'
    for dll in ('ffi-8.dll', 'ffi-7.dll', 'ffi.dll'):
        src = os.path.join(_ffi_src, dll)
        if os.path.exists(src):
            shutil.copy2(src, _internal)
            print(f'已复制：{dll} → _internal/')
    print('\n打包成功！输出文件：dist/PID温度控制仿真系统/')
else:
    print('\n打包失败，请检查错误信息。')
