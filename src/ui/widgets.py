"""自定义控件：PID参数面板、状态栏等"""
from PyQt5.QtWidgets import (
    QGroupBox, QFormLayout, QLineEdit, QHBoxLayout,
    QPushButton, QLabel, QWidget, QVBoxLayout
)
from PyQt5.QtCore import pyqtSignal
from config import PIDDefaults


class PIDParamGroup(QGroupBox):
    """PID参数输入面板，支持实时更新"""
    params_changed = pyqtSignal(float, float, float)

    def __init__(self, title='PID参数',
                 kp=PIDDefaults.KP, ti=PIDDefaults.TI, td=PIDDefaults.TD,
                 parent=None):
        super().__init__(title, parent)
        self._setup_ui(kp, ti, td)

    def _setup_ui(self, kp, ti, td):
        layout = QFormLayout(self)
        self._kp = QLineEdit(str(kp))
        self._ti = QLineEdit(str(ti))
        self._td = QLineEdit(str(td))
        layout.addRow('Kp：', self._kp)
        layout.addRow('Ti：', self._ti)
        layout.addRow('Td：', self._td)
        apply_btn = QPushButton('应用参数')
        apply_btn.clicked.connect(self._emit)
        layout.addRow('', apply_btn)

    def _emit(self):
        from utils.validator import validate_pid_params
        ok, msg, kp, ti, td = validate_pid_params(
            self._kp.text(), self._ti.text(), self._td.text())
        if not ok:
            from exception import show_error_dialog
            show_error_dialog(msg, '参数错误')
            return
        self.params_changed.emit(kp, ti, td)

    def get_params(self):
        try:
            return float(self._kp.text()), float(self._ti.text()), float(self._td.text())
        except ValueError:
            return PIDDefaults.KP, PIDDefaults.TI, PIDDefaults.TD

    def set_params(self, kp, ti, td):
        self._kp.setText(str(kp))
        self._ti.setText(str(ti))
        self._td.setText(str(td))


class StatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        self._label = QLabel('就绪')
        layout.addWidget(self._label)
        layout.addStretch()

    def set_message(self, msg):
        self._label.setText(msg)
