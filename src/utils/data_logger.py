"""数据记录器（历史数据JSON存储）"""
from typing import List, Dict
import json
import os
import time
from config import Paths
from exception import get_logger


class DataLogger:
    """仿真数据记录，按会话分文件存储"""

    def __init__(self):
        os.makedirs(Paths.HISTORY, exist_ok=True)
        self._logger = get_logger()
        self._session_id = time.strftime('%Y%m%d_%H%M%S')
        self._buffer: List[Dict] = []
        self._file_path = os.path.join(
            Paths.HISTORY, f'session_{self._session_id}.json'
        )

    def new_session(self) -> None:
        """开始新的记录会话"""
        self._session_id = time.strftime('%Y%m%d_%H%M%S')
        self._buffer = []
        self._file_path = os.path.join(
            Paths.HISTORY, f'session_{self._session_id}.json'
        )

    def record(self, t: float, sv: float, pv: float,
               u: float, disturbance: float) -> None:
        self._buffer.append({
            't': round(t, 3),
            'sv': round(sv, 4),
            'pv': round(pv, 4),
            'u': round(u, 4),
            'd': round(disturbance, 4),
        })

    def flush(self) -> None:
        """将缓冲写入文件"""
        if not self._buffer:
            return
        try:
            existing = []
            if os.path.exists(self._file_path):
                with open(self._file_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            existing.extend(self._buffer)
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False)
            self._buffer = []
        except Exception as e:
            self._logger.error(f'写入历史数据失败: {e}', exc_info=True)

    def get_sessions(self) -> List[Dict]:
        """返回所有历史会话信息"""
        sessions = []
        try:
            for fname in sorted(os.listdir(Paths.HISTORY), reverse=True):
                if fname.endswith('.json') and fname.startswith('session_'):
                    path = os.path.join(Paths.HISTORY, fname)
                    ts = fname.replace('session_', '').replace('.json', '')
                    try:
                        display = time.strftime(
                            '%Y-%m-%d %H:%M:%S',
                            time.strptime(ts, '%Y%m%d_%H%M%S')
                        )
                    except ValueError as e:
                        self._logger.warning(f'历史文件名时间解析失败 [{ts}]: {e}')
                        display = ts
                    sessions.append({'file': path, 'time': display, 'id': ts})
        except OSError as e:
            self._logger.error(f'读取历史目录失败: {e}', exc_info=True)
        return sessions

    def load_session(self, file_path: str) -> List[Dict]:
        """加载指定会话数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            self._logger.error(f'加载历史记录失败 [{file_path}]: {e}', exc_info=True)
            return []
