"""用户管理业务逻辑"""
from typing import List, Dict, Tuple
from user.user_data import UserDataManager
from config import UserRole


class UserManager:
    """用户CRUD，对外暴露业务方法"""

    def __init__(self):
        self._db = UserDataManager()

    def login(self, user_id: str, password: str) -> Tuple[bool, str, str]:
        """
        返回 (success, role, message)
        """
        user = self._db.get_user(user_id)
        if not user:
            return False, '', '用户不存在'
        if not self._db.verify_password(user_id, password):
            return False, '', '密码错误'
        return True, user['role'], '登录成功'

    def get_all_users(self) -> List[Dict]:
        data = self._db.get_all()
        result = []
        for uid, info in data.items():
            result.append({
                'user_id': uid,
                'display_name': info.get('display_name', uid),
                'role': info.get('role', UserRole.USER),
            })
        return result

    def add_user(self, user_id: str, password: str, role: str,
                 display_name: str = '') -> Tuple[bool, str]:
        if not user_id.strip():
            return False, '用户ID不能为空'
        if len(password) < 4:
            return False, '密码长度不能少于4位'
        if role not in (UserRole.ADMIN, UserRole.USER):
            return False, '角色非法'
        ok = self._db.add_user(user_id.strip(), password, role, display_name)
        if ok:
            return True, '添加成功'
        return False, '用户ID已存在'

    def delete_user(self, user_id: str) -> Tuple[bool, str]:
        if user_id == 'admin':
            return False, '不允许删除内置管理员'
        ok = self._db.delete_user(user_id)
        return (True, '删除成功') if ok else (False, '用户不存在')

    def change_password(self, user_id: str, old_password: str,
                        new_password: str) -> Tuple[bool, str]:
        if not self._db.verify_password(user_id, old_password):
            return False, '原密码错误'
        if len(new_password) < 4:
            return False, '新密码长度不能少于4位'
        self._db.change_password(user_id, new_password)
        return True, '密码修改成功'

    def admin_change_password(self, user_id: str,
                              new_password: str) -> Tuple[bool, str]:
        if len(new_password) < 4:
            return False, '密码长度不能少于4位'
        ok = self._db.change_password(user_id, new_password)
        return (True, '密码修改成功') if ok else (False, '用户不存在')

    def change_role(self, user_id: str, role: str) -> Tuple[bool, str]:
        if user_id == 'admin':
            return False, '不允许修改内置管理员角色'
        ok = self._db.change_role(user_id, role)
        return (True, '角色修改成功') if ok else (False, '用户不存在')
