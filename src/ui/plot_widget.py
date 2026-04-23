"""实时波形显示组件（pyqtgraph）"""
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from collections import deque
from config import TempConfig


class PlotWidget(QWidget):
    """实时波形显示（SV/PV/u/干扰/误差）"""

    def __init__(self, parent=None, max_points: int = TempConfig.DISPLAY_POINTS):
        super().__init__(parent)
        self._max = max_points
        self._t = deque(maxlen=max_points)
        self._sv = deque(maxlen=max_points)
        self._pv = deque(maxlen=max_points)
        self._u = deque(maxlen=max_points)
        self._d = deque(maxlen=max_points)
        self._e = deque(maxlen=max_points)
        self._paused = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        pg.setConfigOptions(antialias=True, background='w', foreground='k')
        self._plot = pg.PlotWidget(title='实时仿真波形')
        self._plot.addLegend(offset=(10, 10))
        self._plot.showGrid(x=True, y=True, alpha=0.3)
        self._plot.setLabel('left', '幅值')
        self._plot.setLabel('bottom', '时间 (s)')

        pen_sv = pg.mkPen(color='r', width=2)
        pen_pv = pg.mkPen(color='g', width=2)
        pen_u = pg.mkPen(color='b', width=1.5)
        pen_d = pg.mkPen(color=(150, 0, 200), width=1.5, style=Qt.DashLine)
        pen_e = pg.mkPen(color=(0, 180, 180), width=1.5, style=Qt.DashDotLine)

        self._curve_sv = self._plot.plot(pen=pen_sv, name='SV 设定值')
        self._curve_pv = self._plot.plot(pen=pen_pv, name='PV 过程值')
        self._curve_u = self._plot.plot(pen=pen_u, name='u 控制量')
        self._curve_d = self._plot.plot(pen=pen_d, name='d 干扰')
        self._curve_e = self._plot.plot(pen=pen_e, name='e 误差')

        layout.addWidget(self._plot)

    def update_data(self, t, sv, pv, u, d):
        if self._paused:
            return
        self._t.append(t)
        self._sv.append(sv)
        self._pv.append(pv)
        self._u.append(u)
        self._d.append(d)
        self._e.append(sv - pv)

        t_list = list(self._t)
        self._curve_sv.setData(t_list, list(self._sv))
        self._curve_pv.setData(t_list, list(self._pv))
        self._curve_u.setData(t_list, list(self._u))
        self._curve_d.setData(t_list, list(self._d))
        self._curve_e.setData(t_list, list(self._e))

    def clear_data(self):
        for buf in (self._t, self._sv, self._pv, self._u, self._d, self._e):
            buf.clear()
        for curve in (self._curve_sv, self._curve_pv, self._curve_u,
                      self._curve_d, self._curve_e):
            curve.setData([], [])

    def set_paused(self, paused):
        self._paused = paused


class HistoryPlotWidget(QWidget):
    """历史曲线显示"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        pg.setConfigOptions(antialias=True, background='w', foreground='k')
        self._plot = pg.PlotWidget(title='历史仿真曲线')
        self._plot.addLegend(offset=(10, 10))
        self._plot.showGrid(x=True, y=True, alpha=0.3)
        self._plot.setLabel('left', '幅值')
        self._plot.setLabel('bottom', '时间 (s)')
        self._plot.setMouseEnabled(x=True, y=True)

        self._curve_sv = self._plot.plot(pen=pg.mkPen('r', width=2), name='SV')
        self._curve_pv = self._plot.plot(pen=pg.mkPen('g', width=2), name='PV')
        self._curve_u = self._plot.plot(pen=pg.mkPen('b', width=1.5), name='u')
        self._curve_d = self._plot.plot(
            pen=pg.mkPen((150, 0, 200), width=1.5, style=Qt.DashLine), name='d')

        layout.addWidget(self._plot)

    def load_data(self, data):
        if not data:
            return
        t = [r['t'] for r in data]
        sv = [r['sv'] for r in data]
        pv = [r['pv'] for r in data]
        u = [r['u'] for r in data]
        d = [r['d'] for r in data]
        self._curve_sv.setData(t, sv)
        self._curve_pv.setData(t, pv)
        self._curve_u.setData(t, u)
        self._curve_d.setData(t, d)
        self._plot.autoRange()
