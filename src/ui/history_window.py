"""历史数据查询窗口"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
    QLabel, QFileDialog, QMessageBox, QSplitter, QWidget
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
