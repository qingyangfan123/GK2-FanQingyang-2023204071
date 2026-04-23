"""时间格式化工具"""
import time


def get_current_time_str(fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    return time.strftime(fmt)


def seconds_to_hms(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f'{h:02d}:{m:02d}:{s:02d}'
