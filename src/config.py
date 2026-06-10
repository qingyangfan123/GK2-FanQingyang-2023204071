"""全局配置模块"""
import os
import sys


def get_base_path() -> str:
    """获取程序根目录（兼容开发和打包环境）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 单文件模式会把资源解压到临时目录 sys._MEIPASS
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_app_dir() -> str:
    """获取程序持久化数据目录（exe所在目录或项目根目录）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Paths:
    """路径配置"""
    BASE = get_base_path()
    APP_DIR = get_app_dir()
    DATA = os.path.join(APP_DIR, 'data')
    HISTORY = os.path.join(DATA, 'history_data')
    USERS = os.path.join(DATA, 'users')
    LOGS = os.path.join(DATA, 'logs')
    USERS_FILE = os.path.join(USERS, 'users.json')
    ERROR_LOG = os.path.join(LOGS, 'error.log')
    ASSETS = os.path.join(BASE, 'assets')
    STYLE = os.path.join(ASSETS, 'style.qss')


class TempConfig:
    """温度控制参数配置"""
    SV_MIN = 0.0
    SV_MAX = 30.0
    SV_DEFAULT = 20.0
    PV_INIT = 0.0
    U_MAX = 30.0
    U_MIN = -30.0

    # 被控对象参数
    T1_DEFAULT = 1.0
    T2_DEFAULT = 2.0
    GAIN_DEFAULT = 1.0

    # 反馈滤波时间常数
    TC = 0.1

    # 仿真步长(s)
    DT = 0.1

    # 显示点数
    DISPLAY_POINTS = 300


class PIDDefaults:
    """PID默认参数"""
    # 单回路/普通PID
    KP = 2.0
    TI = 2.0
    TD = 0.5

    # 串级外环
    OUTER_KP = 2.0
    OUTER_TI = 2.0
    OUTER_TD = 0.5

    # 串级内环
    INNER_KP = 1.0
    INNER_TI = 2.0
    INNER_TD = 0.0

    # 前馈增益
    FF_GAIN = -0.5


class ControlStrategy:
    """控制策略枚举"""
    PLAIN_PID = 0       # 普通PID（无限幅）
    SINGLE_PID = 1      # 单回路PID（带抗饱和）
    FEEDFORWARD = 2     # 前馈+反馈
    CASCADE = 3         # 串级PID
    CASCADE_FF = 4      # 串级+前馈

    NAMES = {
        0: '普通PID（无限幅）',
        1: '单回路PID（带抗饱和）',
        2: '前馈+反馈控制',
        3: '串级PID控制',
        4: '串级+前馈控制',
    }


class UserRole:
    """用户角色"""
    ADMIN = 'admin'
    USER = 'user'


class Permissions:
    """权限常量"""
    CHANGE_OWN_PASSWORD = 'change_own_password'
    MANAGE_USERS = 'manage_users'
    CHANGE_OTHER_PERMISSIONS = 'change_other_permissions'
    RUN_SIMULATION = 'run_simulation'
    EXPORT_HISTORY = 'export_history'

    ROLE_PERMISSIONS = {
        UserRole.ADMIN: [
            CHANGE_OWN_PASSWORD,
            MANAGE_USERS,
            CHANGE_OTHER_PERMISSIONS,
            RUN_SIMULATION,
            EXPORT_HISTORY,
        ],
        UserRole.USER: [
            CHANGE_OWN_PASSWORD,
            RUN_SIMULATION,
            EXPORT_HISTORY,
        ],
    }
