"""参数校验工具"""
from typing import Tuple
from config import TempConfig


def validate_pid_params(kp: str, ti: str, td: str) -> Tuple[bool, str, float, float, float]:
    """
    校验PID参数字符串，返回 (ok, message, kp, ti, td)
    """
    try:
        kp_v = float(kp)
        ti_v = float(ti)
        td_v = float(td)
    except ValueError:
        return False, 'PID参数必须是数字', 0, 0, 0
    if kp_v < 0:
        return False, 'Kp 不能为负数', 0, 0, 0
    if ti_v <= 0:
        return False, 'Ti 必须大于0', 0, 0, 0
    if td_v < 0:
        return False, 'Td 不能为负数', 0, 0, 0
    return True, '', kp_v, ti_v, td_v


def validate_sv(sv: str) -> Tuple[bool, str, float]:
    try:
        v = float(sv)
    except ValueError:
        return False, '设定值必须是数字', 0
    if v < TempConfig.SV_MIN or v > TempConfig.SV_MAX:
        return False, f'设定值范围 {TempConfig.SV_MIN}~{TempConfig.SV_MAX}', 0
    return True, '', v


def validate_manual_output(u: str, limited: bool = True) -> Tuple[bool, str, float]:
    try:
        v = float(u)
    except ValueError:
        return False, '控制量必须是数字', 0
    if limited:
        if v < TempConfig.U_MIN or v > TempConfig.U_MAX:
            return False, f'控制量范围 {TempConfig.U_MIN}~{TempConfig.U_MAX}', 0
    return True, '', v


def validate_disturbance(amp: str, dur: str) -> Tuple[bool, str, float, float]:
    try:
        amp_v = float(amp)
        dur_v = float(dur)
    except ValueError:
        return False, '干扰参数必须是数字', 0, 0
    if dur_v <= 0:
        return False, '干扰持续时间必须大于0', 0, 0
    return True, '', amp_v, dur_v


def validate_model_params(T1: str, T2: str, gain: str) -> Tuple[bool, str, float, float, float]:
    try:
        T1_v = float(T1)
        T2_v = float(T2)
        g_v = float(gain)
    except ValueError:
        return False, '模型参数必须是数字', 0, 0, 0
    if T1_v <= 0 or T2_v <= 0:
        return False, 'T1、T2 必须大于0', 0, 0, 0
    if g_v <= 0:
        return False, '增益必须大于0', 0, 0, 0
    return True, '', T1_v, T2_v, g_v
