"""修改密码对话框"""
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QMessageBox
)
from user.user_manager import UserManager
from user.permission import current_user


class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._manager = UserManager()
        self.setWindowTitle('修改密码')
        self.setFixedSize(320, 200)
        self._setup_ui()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        form = QFormLayout()
        self._old = QLineEdit()
        self._old.setEchoMode(QLineEdit.Password)
        self._new1 = QLineEdit()
        self._new1.setEchoMode(QLineEdit.Password)
        self._new2 = QLineEdit()
        self._new2.setEchoMode(QLineEdit.Password)
        form.addRow('原密码：', self._old)
        form.addRow('新密码：', self._new1)
        form.addRow('确认密码：', self._new2)
        root.addLayout(form)

        btns = QHBoxLayout()
        ok_btn = QPushButton('确认修改')
        cancel_btn = QPushButton('取消')
        ok_btn.setMinimumHeight(32)
        cancel_btn.setMinimumHeight(32)
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        root.addLayout(btns)

        ok_btn.clicked.connect(self._on_ok)
        cancel_btn.clicked.connect(self.reject)

    def _on_ok(self):
        old = self._old.text()
        new1 = self._new1.text()
        new2 = self._new2.text()
        if not old or not new1 or not new2:
            QMessageBox.warning(self, '提示', '请填写所有字段')
            return
        if new1 != new2:
            QMessageBox.warning(self, '提示', '两次新密码不一致')
            return
        ok, msg = self._manager.change_password(current_user.user_id, old, new1)
        if ok:
            QMessageBox.information(self, '成功', msg)
            self.accept()
        else:
            QMessageBox.warning(self, '失败', msg)
