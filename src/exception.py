"""全局异常处理模块"""
import sys
import traceback
import logging
import os

from PyQt5.QtWidgets import QApplication, QMessageBox


def setup_logger(log_path: str) -> logging.Logger:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logger = logging.getLogger('SimControl')
    logger.setLevel(logging.ERROR)
    if not logger.handlers:
        fh = logging.FileHandler(log_path, encoding='utf-8')
        fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.addHandler(fh)
    return logger


_logger = None


def get_logger() -> logging.Logger:
    from config import Paths
    global _logger
    if _logger is None:
        _logger = setup_logger(Paths.ERROR_LOG)
    return _logger


class CalculationException(Exception):
    pass


class ParameterException(Exception):
    pass


def show_error_dialog(message: str, title: str = '错误') -> None:
    try:
        app = QApplication.instance()
        if app:
            box = QMessageBox()
            box.setWindowTitle(title)
            box.setIcon(QMessageBox.Critical)
            box.setText(message)
            box.exec_()
    except Exception:
        pass


def show_info_dialog(message: str, title: str = '提示') -> None:
    try:
        app = QApplication.instance()
        if app:
            box = QMessageBox()
            box.setWindowTitle(title)
            box.setIcon(QMessageBox.Information)
            box.setText(message)
            box.exec_()
    except Exception:
        pass


def _global_exception_handler(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        get_logger().error('未捕获异常:\n%s', tb_str)
    except Exception:
        pass
    show_error_dialog(f'程序发生未知错误，已记录日志。\n\n{exc_value}', '程序异常')


def install_exception_handler() -> None:
    sys.excepthook = _global_exception_handler
