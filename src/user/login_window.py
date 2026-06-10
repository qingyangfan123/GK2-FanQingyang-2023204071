"""登录界面"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFormLayout, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from user.user_manager import UserManager
from user.permission import current_user


class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._manager = UserManager()
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle('PID温度控制仿真系统 - 登录')
        self.setFixedSize(440, 340)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 40)
        root.setSpacing(20)

        title = QLabel('PID 温度控制仿真系统')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 22px; color: #1e293b; font-weight: bold;')
        root.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        root.addWidget(sep)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignLeft)
        self._id_edit = QLineEdit()
        self._id_edit.setPlaceholderText('请输入用户ID')
        self._id_edit.setText('admin')
        form.addRow('用户ID：', self._id_edit)

        self._pwd_edit = QLineEdit()
        self._pwd_edit.setEchoMode(QLineEdit.Password)
        self._pwd_edit.setPlaceholderText('请输入密码')
        form.addRow('密  码：', self._pwd_edit)
        root.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)
        self._login_btn = QPushButton('登 录')
        self._login_btn.setDefault(True)
        self._login_btn.setMinimumHeight(40)
        quit_btn = QPushButton('退 出')
        quit_btn.setMinimumHeight(40)
        btn_row.addWidget(self._login_btn)
        btn_row.addWidget(quit_btn)
        root.addLayout(btn_row)

        self._login_btn.clicked.connect(self._do_login)
        quit_btn.clicked.connect(self.reject)
        self._pwd_edit.returnPressed.connect(self._do_login)

    def _do_login(self):
        user_id = self._id_edit.text().strip()
        password = self._pwd_edit.text()
        if not user_id or not password:
            QMessageBox.warning(self, '提示', '请输入用户ID和密码')
            return
        ok, role, msg = self._manager.login(user_id, password)
        if ok:
            current_user.login(user_id, role)
            self.accept()
        else:
            QMessageBox.warning(self, '登录失败', msg)
            self._pwd_edit.clear()
            self._pwd_edit.setFocus()
