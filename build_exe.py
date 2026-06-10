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
DIST = os.path.join(ROOT, 'dist')

# conda 环境下 PyInstaller 可能无法自动收集的 DLL
_FFI_SRC = r'C:\Users\94691\AppData\Local\conda\conda\envs\sim_env\Library\bin'

# 清理旧缓存，避免 PyInstaller 复用过期分析结果
for path in (SPEC, BUILD, DIST):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
            print(f'已删除目录：{path}')
        else:
            os.remove(path)
            print(f'已删除文件：{path}')

# 验证打包所用的 Python 环境中 openpyxl 是否可用
print(f'使用 Python 解释器: {PYTHON}')
ver_result = subprocess.run(
    [PYTHON, '-c', 'import openpyxl; print(openpyxl.__version__)'],
    capture_output=True, text=True
)
if ver_result.returncode == 0:
    print(f'验证通过：openpyxl 版本 {ver_result.stdout.strip()}')
else:
    print(f'警告：打包环境缺少 openpyxl！错误：{ver_result.stderr.strip()}')

cmd = [
    PYTHON, '-m', 'PyInstaller',
    '--onefile',
    '--windowed',
    '--clean',
    '--log-level', 'INFO',
    '--name', 'PID温度控制仿真系统',
    '--distpath', DIST,
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
    # Excel 导出依赖：强制完整收集 openpyxl 及其依赖 et_xmlfile
    '--collect-all', 'openpyxl',
    '--collect-all', 'et_xmlfile',
    '--hidden-import', 'openpyxl',
    # openpyxl 解析 XML 需要的标准库模块（pyexpat 是 xml.parsers.expat 的底层 C 扩展）
    '--hidden-import', 'xml.parsers.expat',
    '--hidden-import', 'pyexpat',
    '--hidden-import', 'xml.etree.ElementTree',
]

# 将 conda 下缺失的 ffi DLL 打包进 exe
for dll in ('ffi-8.dll', 'ffi-7.dll', 'ffi.dll'):
    src = os.path.join(_FFI_SRC, dll)
    if os.path.exists(src):
        cmd.append(f'--add-binary={src}{os.pathsep}.')
        print(f'找到并加入打包：{dll}')

# 打包 pyexpat 需要的 libexpat.dll（conda 环境特有）
_libexpat = os.path.join(_FFI_SRC, 'libexpat.dll')
if os.path.exists(_libexpat):
    cmd.append(f'--add-binary={_libexpat}{os.pathsep}.')
    print(f'找到并加入打包：libexpat.dll')

cmd.append(MAIN)

print('开始打包...')
result = subprocess.run(cmd, cwd=ROOT)
if result.returncode == 0:
    print('\n打包成功！输出文件：dist/PID温度控制仿真系统.exe')
else:
    print('\n打包失败，请检查错误信息。')
