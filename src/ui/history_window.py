"""历史数据查询窗口"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
    QLabel, QFileDialog, QMessageBox, QSplitter, QWidget, QLineEdit
)
from PyQt5.QtCore import Qt
from ui.plot_widget import HistoryPlotWidget
from utils.data_logger import DataLogger
from utils.excel_exporter import export_to_excel
from user.permission import current_user
from config import Permissions


class HistoryWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._logger = DataLogger()
        self.setWindowTitle('历史曲线')
        self.setMinimumSize(900, 550)
        self._current_data = []
        self._setup_ui()
        self._load_sessions()

    def _setup_ui(self):
        root = QVBoxLayout(self)

        splitter = QSplitter(Qt.Horizontal)

        left_w = QWidget()
        left = QVBoxLayout(left_w)
        left_w.setMaximumWidth(220)

        left.addWidget(QLabel('历史记录：'))
        self._session_list = QListWidget()
        left.addWidget(self._session_list)

        load_btn = QPushButton('加载选中记录')
        load_btn.clicked.connect(self._load_selected)
        left.addWidget(load_btn)

        left.addWidget(QLabel('时间筛选(s)：'))
        filter_row = QHBoxLayout()
        self._t_start = QLineEdit()
        self._t_start.setPlaceholderText('起始')
        self._t_end = QLineEdit()
        self._t_end.setPlaceholderText('结束')
        filter_row.addWidget(QLabel('从'))
        filter_row.addWidget(self._t_start)
        filter_row.addWidget(QLabel('到'))
        filter_row.addWidget(self._t_end)
        left.addLayout(filter_row)

        filter_btn = QPushButton('筛选当前数据')
        filter_btn.clicked.connect(self._filter_data)
        left.addWidget(filter_btn)

        reset_btn = QPushButton('显示全部')
        reset_btn.clicked.connect(self._show_all)
        left.addWidget(reset_btn)

        export_btn = QPushButton('导出Excel')
        export_btn.clicked.connect(self._export)
        if not current_user.has_permission(Permissions.EXPORT_HISTORY):
            export_btn.setEnabled(False)
        left.addWidget(export_btn)

        splitter.addWidget(left_w)

        self._plot = HistoryPlotWidget()
        splitter.addWidget(self._plot)
        splitter.setStretchFactor(1, 3)

        root.addWidget(splitter)

        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.accept)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(close_btn)
        root.addLayout(row)

    def _load_sessions(self):
        self._sessions = self._logger.get_sessions()
        self._session_list.clear()
        for s in self._sessions:
            self._session_list.addItem(s['time'])

    def _load_selected(self):
        row = self._session_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, '提示', '请先选择一条记录')
            return
        self._current_data = self._logger.load_session(self._sessions[row]['file'])
        self._plot.load_data(self._current_data)

    def _filter_data(self):
        if not self._current_data:
            QMessageBox.warning(self, '提示', '请先加载历史记录')
            return
        try:
            t_start = float(self._t_start.text()) if self._t_start.text().strip() else None
            t_end = float(self._t_end.text()) if self._t_end.text().strip() else None
        except ValueError:
            QMessageBox.warning(self, '提示', '时间范围请输入数字')
            return
        filtered = [
            r for r in self._current_data
            if (t_start is None or r['t'] >= t_start)
            and (t_end is None or r['t'] <= t_end)
        ]
        if not filtered:
            QMessageBox.information(self, '提示', '该时间范围内无数据')
            return
        self._plot.load_data(filtered)

    def _show_all(self):
        if not self._current_data:
            QMessageBox.warning(self, '提示', '请先加载历史记录')
            return
        self._plot.load_data(self._current_data)

    def _export(self):
        if not self._current_data:
            QMessageBox.warning(self, '提示', '请先加载历史记录')
            return
        path, _ = QFileDialog.getSaveFileName(self, '导出Excel', '', 'Excel文件 (*.xlsx)')
        if not path:
            return
        if not path.endswith('.xlsx'):
            path += '.xlsx'
        ok, msg = export_to_excel(self._current_data, path)
        (QMessageBox.information if ok else QMessageBox.warning)(self, '导出', msg)
