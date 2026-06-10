"""用户管理界面（管理员专用）"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QMessageBox,
    QFormLayout, QGroupBox, QHeaderView, QInputDialog
)
from user.user_manager import UserManager
from user.permission import current_user
from config import UserRole, Permissions


class UserManagerWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 权限拦截：仅管理员可进入
        if not current_user.is_admin:
            QMessageBox.warning(
                self, '权限不足',
                '您没有权限进入用户管理界面'
            )
            self.reject()
            return

        self._manager = UserManager()
        self.setWindowTitle('用户管理')
        self.setMinimumSize(600, 420)
        self._setup_ui()
        self._refresh_table()

    def _setup_ui(self):
        root = QVBoxLayout(self)

        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(['用户ID', '显示名称', '角色'])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        root.addWidget(self._table)

        btn_row = QHBoxLayout()
        self._del_btn = QPushButton('删除选中用户')
        self._pwd_btn = QPushButton('重置密码')
        self._role_btn = QPushButton('切换角色')
        refresh_btn = QPushButton('刷新')
        for b in (self._del_btn, self._pwd_btn, self._role_btn, refresh_btn):
            b.setMinimumHeight(30)
            btn_row.addWidget(b)
        root.addLayout(btn_row)

        add_group = QGroupBox('添加新用户')
        add_layout = QFormLayout(add_group)
        self._new_id = QLineEdit()
        self._new_pwd = QLineEdit()
        self._new_pwd.setEchoMode(QLineEdit.Password)
        self._new_name = QLineEdit()
        self._new_role = QComboBox()
        self._new_role.addItems(['普通用户', '管理员'])
        add_layout.addRow('用户ID：', self._new_id)
        add_layout.addRow('密  码：', self._new_pwd)
        add_layout.addRow('显示名：', self._new_name)
        add_layout.addRow('角  色：', self._new_role)
        add_btn = QPushButton('添加用户')
        add_btn.setMinimumHeight(30)
        add_layout.addRow('', add_btn)
        root.addWidget(add_group)

        self._del_btn.clicked.connect(self._delete_user)
        self._pwd_btn.clicked.connect(self._reset_password)
        self._role_btn.clicked.connect(self._toggle_role)
        refresh_btn.clicked.connect(self._refresh_table)
        add_btn.clicked.connect(self._add_user)

    def _refresh_table(self):
        users = self._manager.get_all_users()
        self._table.setRowCount(len(users))
        for i, u in enumerate(users):
            self._table.setItem(i, 0, QTableWidgetItem(u['user_id']))
            self._table.setItem(i, 1, QTableWidgetItem(u['display_name']))
            role_text = '管理员' if u['role'] == UserRole.ADMIN else '普通用户'
            self._table.setItem(i, 2, QTableWidgetItem(role_text))

    def _selected_user_id(self):
        row = self._table.currentRow()
        if row < 0:
            QMessageBox.warning(self, '提示', '请先选择一个用户')
            return None
        return self._table.item(row, 0).text()

    def _delete_user(self):
        uid = self._selected_user_id()
        if uid is None:
            return
        if QMessageBox.question(self, '确认', f'确定删除用户 {uid}？') == QMessageBox.Yes:
            ok, msg = self._manager.delete_user(uid)
            (QMessageBox.information if ok else QMessageBox.warning)(self, '结果', msg)
            self._refresh_table()

    def _reset_password(self):
        uid = self._selected_user_id()
        if uid is None:
            return
        pwd, ok = QInputDialog.getText(
            self, '重置密码', f'输入用户 {uid} 的新密码：', QLineEdit.Password)
        if ok and pwd:
            res_ok, msg = self._manager.admin_change_password(uid, pwd)
            (QMessageBox.information if res_ok else QMessageBox.warning)(self, '结果', msg)

    def _toggle_role(self):
        uid = self._selected_user_id()
        if uid is None:
            return
        users = self._manager.get_all_users()
        current_role = next(
            (u['role'] for u in users if u['user_id'] == uid), UserRole.USER)
        new_role = UserRole.USER if current_role == UserRole.ADMIN else UserRole.ADMIN
        ok, msg = self._manager.change_role(uid, new_role)
        (QMessageBox.information if ok else QMessageBox.warning)(self, '结果', msg)
        self._refresh_table()

    def _add_user(self):
        uid = self._new_id.text().strip()
        pwd = self._new_pwd.text()
        name = self._new_name.text().strip()
        role = UserRole.ADMIN if self._new_role.currentIndex() == 1 else UserRole.USER
        ok, msg = self._manager.add_user(uid, pwd, role, name)
        (QMessageBox.information if ok else QMessageBox.warning)(self, '结果', msg)
        if ok:
            self._new_id.clear()
            self._new_pwd.clear()
            self._new_name.clear()
            self._refresh_table()
