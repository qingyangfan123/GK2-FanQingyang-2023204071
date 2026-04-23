"""用户数据持久化（JSON + 简单加密）"""
from typing import Optional
import json
import os
import hashlib
from config import Paths, UserRole


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


DEFAULT_USERS = {
    'admin': {
        'password': _hash_password('admin123'),
        'role': UserRole.ADMIN,
        'display_name': '管理员',
    },
    'user': {
        'password': _hash_password('user123'),
        'role': UserRole.USER,
        'display_name': '普通用户',
    },
}


class UserDataManager:
    """用户数据JSON读写"""

    def __init__(self, path: str = Paths.USERS_FILE):
        self.path = path
        self._ensure_file()

    def _ensure_file(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            self._write(DEFAULT_USERS)

    def _read(self) -> dict:
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return dict(DEFAULT_USERS)

    def _write(self, data: dict) -> None:
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_all(self) -> dict:
        return self._read()

    def get_user(self, user_id: str) -> Optional[dict]:
        return self._read().get(user_id)

    def verify_password(self, user_id: str, password: str) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        return user['password'] == _hash_password(password)

    def add_user(self, user_id: str, password: str, role: str,
                 display_name: str = '') -> bool:
        data = self._read()
        if user_id in data:
            return False
        data[user_id] = {
            'password': _hash_password(password),
            'role': role,
            'display_name': display_name or user_id,
        }
        self._write(data)
        return True

    def delete_user(self, user_id: str) -> bool:
        data = self._read()
        if user_id not in data:
            return False
        del data[user_id]
        self._write(data)
        return True

    def change_password(self, user_id: str, new_password: str) -> bool:
        data = self._read()
        if user_id not in data:
            return False
        data[user_id]['password'] = _hash_password(new_password)
        self._write(data)
        return True

    def change_role(self, user_id: str, role: str) -> bool:
        data = self._read()
        if user_id not in data:
            return False
        data[user_id]['role'] = role
        self._write(data)
        return True
