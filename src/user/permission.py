"""权限校验模块"""
from config import UserRole, Permissions


class CurrentUser:
    """当前登录用户上下文（全局单例）"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._user_id = ''
            cls._instance._role = ''
        return cls._instance

    def login(self, user_id: str, role: str) -> None:
        self._user_id = user_id
        self._role = role

    def logout(self) -> None:
        self._user_id = ''
        self._role = ''

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def role(self) -> str:
        return self._role

    @property
    def is_admin(self) -> bool:
        return self._role == UserRole.ADMIN

    @property
    def is_logged_in(self) -> bool:
        return bool(self._user_id)

    def has_permission(self, perm: str) -> bool:
        perms = Permissions.ROLE_PERMISSIONS.get(self._role, [])
        return perm in perms


current_user = CurrentUser()
