"""程序入口"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from exception import install_exception_handler
from config import Paths


def _ensure_dirs():
    for d in (Paths.DATA, Paths.HISTORY, Paths.USERS, Paths.LOGS):
        os.makedirs(d, exist_ok=True)


def main():
    install_exception_handler()
    _ensure_dirs()

    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setApplicationName('PID温度控制仿真系统')

    if os.path.exists(Paths.STYLE):
        with open(Paths.STYLE, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())

    from user.login_window import LoginWindow
    login = LoginWindow()
    if login.exec_() != LoginWindow.Accepted:
        sys.exit(0)

    from ui.main_window import MainWindow
    win = MainWindow()
    win.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
