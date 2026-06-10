"""主界面"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QGroupBox, QFormLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QCheckBox, QSplitter, QMessageBox,
    QStatusBar, QMenuBar, QMenu, QAction, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer

from config import (ControlStrategy, TempConfig, PIDDefaults, Permissions, UserRole)
from user.permission import current_user
from control.control_strategy import ControlStrategyManager
from model.two_inertia_model import TwoInertiaModel
from model.feedback_model import FeedbackModel
from model.disturbance import SquareWaveDisturbance
from ui.plot_widget import PlotWidget
from ui.widgets import PIDParamGroup
from utils.data_logger import DataLogger
from utils.validator import (validate_sv, validate_manual_output,
                             validate_disturbance, validate_model_params)
from utils.exception_handler import handle_exception


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PID温度控制仿真系统')
        self.setMinimumSize(1200, 720)

        self._ctrl = ControlStrategyManager(dt=TempConfig.DT)
        self._model = TwoInertiaModel()
        self._feedback = FeedbackModel()
        self._disturbance = SquareWaveDisturbance(dt=TempConfig.DT)
        self._logger = DataLogger()

        self._running = False
        self._paused_display = False
        self._sim_time = 0.0
        self._sv = TempConfig.SV_DEFAULT
        self._pv = TempConfig.PV_INIT
        self._u = 0.0
        self._d = 0.0
        self._inner_pv = 0.0
        self._plant_with_dist = 0.0

        self._timer = QTimer(self)
        self._timer.setInterval(int(TempConfig.DT * 1000))
        self._timer.timeout.connect(self._sim_step)

        self._setup_menu()
        self._setup_ui()
        self._update_strategy_panels()
        self.statusBar().showMessage(
            f'已登录：{current_user.user_id}（{current_user.role}）')

    # ------------------------------------------------------------------
    # 菜单
    # ------------------------------------------------------------------
    def _setup_menu(self):
        mb = self.menuBar()

        sys_menu = mb.addMenu('系统')
        logout_act = QAction('退出登录', self)
        logout_act.triggered.connect(self._logout)
        quit_act = QAction('退出程序', self)
        quit_act.triggered.connect(self.close)
        sys_menu.addAction(logout_act)
        sys_menu.addSeparator()
        sys_menu.addAction(quit_act)

        func_menu = mb.addMenu('功能')
        history_act = QAction('历史曲线', self)
        history_act.triggered.connect(self._open_history)
        func_menu.addAction(history_act)

        user_menu = mb.addMenu('用户管理')
        pwd_act = QAction('修改密码', self)
        pwd_act.triggered.connect(self._change_password)
        user_menu.addAction(pwd_act)
        if current_user.has_permission(Permissions.MANAGE_USERS):
            manage_act = QAction('管理用户', self)
            manage_act.triggered.connect(self._manage_users)
            user_menu.addAction(manage_act)

        help_menu = mb.addMenu('帮助')
        about_act = QAction('关于软件', self)
        about_act.triggered.connect(self._about)
        help_menu.addAction(about_act)

    # ------------------------------------------------------------------
    # UI 布局
    # ------------------------------------------------------------------
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        splitter = QSplitter(Qt.Horizontal)

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_scroll.setFixedWidth(400)

        left_panel = self._build_left_panel()
        left_scroll.setWidget(left_panel)
        splitter.addWidget(left_scroll)

        self._plot = PlotWidget()
        splitter.addWidget(self._plot)
        splitter.setStretchFactor(1, 3)
        splitter.setSizes([400, 800])

        main_layout.addWidget(splitter)

    def _build_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)

        # ---- 仿真控制 ----
        sim_group = QGroupBox('仿真控制')
        sim_layout = QVBoxLayout(sim_group)

        sv_row = QFormLayout()
        self._sv_edit = QLineEdit(str(TempConfig.SV_DEFAULT))
        self._pv_label = QLabel('0.0000')
        self._u_label = QLabel('0.0000')
        sv_row.addRow('设定值 SV：', self._sv_edit)
        sv_row.addRow('过程值 PV：', self._pv_label)
        sv_row.addRow('控制量  u：', self._u_label)
        sim_layout.addLayout(sv_row)

        self._manual_check = QCheckBox('手动模式')
        self._manual_edit = QLineEdit('0')
        self._manual_edit.setPlaceholderText('手动输出值')
        self._manual_edit.setEnabled(False)
        self._manual_check.toggled.connect(self._toggle_manual)
        sim_layout.addWidget(self._manual_check)
        sim_layout.addWidget(self._manual_edit)

        btn_row = QHBoxLayout()
        self._start_btn = QPushButton('开始仿真')
        self._stop_btn = QPushButton('停止仿真')
        self._stop_btn.setObjectName('stopBtn')
        self._stop_btn.setEnabled(False)
        btn_row.addWidget(self._start_btn)
        btn_row.addWidget(self._stop_btn)
        self._pause_btn = QPushButton('暂停显示')
        self._pause_btn.setEnabled(False)
        sim_layout.addLayout(btn_row)
        sim_layout.addWidget(self._pause_btn)

        display_row = QHBoxLayout()
        display_row.addWidget(QLabel('显示点数：'))
        self._display_edit = QLineEdit(str(TempConfig.DISPLAY_POINTS))
        display_row.addWidget(self._display_edit)
        apply_display_btn = QPushButton('应用显示')
        apply_display_btn.setStyleSheet('QPushButton{background-color:#ffffff;color:#334155;border:1px solid #cbd5e1;border-radius:6px;padding:6px 16px;font-size:13px;font-weight:500;min-height:32px;}QPushButton:hover{background-color:#f8fafc;border:1px solid #94a3b8;}QPushButton:pressed{background-color:#f1f5f9;}QPushButton:disabled{background-color:#f1f5f9;color:#94a3b8;border:1px solid #e2e8f0;}')
        apply_display_btn.clicked.connect(self._apply_display_points)
        display_row.addWidget(apply_display_btn)
        sim_layout.addLayout(display_row)

        self._start_btn.clicked.connect(self._start_sim)
        self._stop_btn.clicked.connect(self._stop_sim)
        self._pause_btn.clicked.connect(self._toggle_pause)
        layout.addWidget(sim_group)

        # ---- 控制策略 ----
        strategy_group = QGroupBox('控制策略')
        sg_layout = QVBoxLayout(strategy_group)

        class NoWheelComboBox(QComboBox):
            def wheelEvent(self, event):
                event.ignore()

        self._strategy_combo = NoWheelComboBox()
        for k, v in ControlStrategy.NAMES.items():
            self._strategy_combo.addItem(v, k)
        self._strategy_combo.currentIndexChanged.connect(self._on_strategy_changed)
        sg_layout.addWidget(self._strategy_combo)

        self._limit_label = QLabel('限幅范围：无限制')
        sg_layout.addWidget(self._limit_label)
        layout.addWidget(strategy_group)

        # ---- PID参数 ----
        self._pid_group = PIDParamGroup('PID 参数', PIDDefaults.KP, PIDDefaults.TI, PIDDefaults.TD)
        self._pid_group.params_changed.connect(self._on_pid_params)
        layout.addWidget(self._pid_group)

        self._outer_group = PIDParamGroup('串级外环参数', PIDDefaults.OUTER_KP,
                                          PIDDefaults.OUTER_TI, PIDDefaults.OUTER_TD)
        self._outer_group.params_changed.connect(self._on_outer_params)
        layout.addWidget(self._outer_group)

        self._inner_group = PIDParamGroup('串级内环参数', PIDDefaults.INNER_KP,
                                          PIDDefaults.INNER_TI, PIDDefaults.INNER_TD)
        self._inner_group.params_changed.connect(self._on_inner_params)
        layout.addWidget(self._inner_group)

        # ---- 被控对象 ----
        model_group = QGroupBox('被控对象参数')
        mg_layout = QFormLayout(model_group)
        self._t1_edit = QLineEdit(str(TempConfig.T1_DEFAULT))
        self._t2_edit = QLineEdit(str(TempConfig.T2_DEFAULT))
        self._gain_edit = QLineEdit(str(TempConfig.GAIN_DEFAULT))
        mg_layout.addRow('T₁：', self._t1_edit)
        mg_layout.addRow('T₂：', self._t2_edit)
        mg_layout.addRow('增益：', self._gain_edit)
        apply_model_btn = QPushButton('应用模型参数')
        apply_model_btn.setStyleSheet('QPushButton{background-color:#ffffff;color:#334155;border:1px solid #cbd5e1;border-radius:6px;padding:6px 16px;font-size:13px;font-weight:500;min-height:32px;}QPushButton:hover{background-color:#f8fafc;border:1px solid #94a3b8;}QPushButton:pressed{background-color:#f1f5f9;}QPushButton:disabled{background-color:#f1f5f9;color:#94a3b8;border:1px solid #e2e8f0;}')
        apply_model_btn.clicked.connect(self._apply_model_params)
        mg_layout.addRow('', apply_model_btn)
        layout.addWidget(model_group)

        # ---- 干扰 ----
        dist_group = QGroupBox('干扰信号')
        dg_layout = QFormLayout(dist_group)
        self._dist_amp_edit = QLineEdit('0')
        self._dist_dur_edit = QLineEdit('10')
        self._dist_btn = QPushButton('施加方波干扰')
        self._dist_btn.setStyleSheet('QPushButton{background-color:#ffffff;color:#334155;border:1px solid #cbd5e1;border-radius:6px;padding:6px 16px;font-size:13px;font-weight:500;min-height:32px;}QPushButton:hover{background-color:#f8fafc;border:1px solid #94a3b8;}QPushButton:pressed{background-color:#f1f5f9;}QPushButton:disabled{background-color:#f1f5f9;color:#94a3b8;border:1px solid #e2e8f0;}')
        self._dist_countdown_label = QLabel('')
        dg_layout.addRow('振幅：', self._dist_amp_edit)
        dg_layout.addRow('持续时间(s)：', self._dist_dur_edit)
        dg_layout.addRow('', self._dist_btn)
        dg_layout.addRow('', self._dist_countdown_label)
        self._dist_btn.clicked.connect(self._apply_disturbance)
        layout.addWidget(dist_group)

        layout.addStretch()
        return panel

    # ------------------------------------------------------------------
    # 仿真循环
    # ------------------------------------------------------------------
    def _sim_step(self):
        try:
            ok, _, sv = validate_sv(self._sv_edit.text())
            if ok:
                self._sv = sv

            if self._ctrl.manual_mode:
                is_limited = self._ctrl.strategy != ControlStrategy.PLAIN_PID
                ok2, _, u_manual = validate_manual_output(
                    self._manual_edit.text(), limited=is_limited)
                if ok2:
                    self._ctrl.manual_output = u_manual

            self._d = self._disturbance.step()
            if not self._disturbance.is_active:
                self._dist_btn.setEnabled(True)
                self._dist_countdown_label.setText('')
            else:
                remaining = self._disturbance.remaining_steps * TempConfig.DT
                self._dist_countdown_label.setText(f'剩余 {remaining:.1f}s')

            self._u = self._ctrl.compute(
                setpoint=self._sv,
                pv=self._pv,
                inner_pv=self._inner_pv,
                disturbance=self._d,
                outer_pv=self._plant_with_dist,
            )

            self._inner_pv, plant_out = self._model.step(self._u)
            self._plant_with_dist = plant_out + self._d
            self._pv = self._feedback.step(self._plant_with_dist)

            self._pv_label.setText(f'{self._pv:.4f}')
            self._u_label.setText(f'{self._u:.4f}')

            self._logger.record(self._sim_time, self._sv, self._pv, self._u, self._d)
            self._plot.update_data(self._sim_time, self._sv, self._pv, self._u, self._d)

            self._sim_time += TempConfig.DT

            step_n = int(round(self._sim_time / TempConfig.DT))
            if step_n % 50 == 0:
                self.statusBar().showMessage(
                    f't={self._sim_time:.1f}s  SV={self._sv:.2f}  '
                    f'PV={self._pv:.4f}  u={self._u:.4f}')
            if step_n % 100 == 0:
                self._logger.flush()

        except Exception as e:
            handle_exception(e, '仿真计算错误', show_dialog=False)

    # ------------------------------------------------------------------
    # 按钮回调
    # ------------------------------------------------------------------
    def _start_sim(self):
        if not current_user.has_permission(Permissions.RUN_SIMULATION):
            QMessageBox.warning(self, '权限不足', '您没有运行仿真的权限')
            return
        self._model.reset()
        self._feedback.reset()
        self._ctrl.reset_all()
        self._plot.clear_data()
        self._logger.new_session()
        self._sim_time = 0.0
        self._pv = TempConfig.PV_INIT
        self._inner_pv = 0.0
        self._u = 0.0
        self._d = 0.0
        self._plant_with_dist = 0.0
        self._running = True
        self._timer.start()
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._pause_btn.setEnabled(True)
        self.statusBar().showMessage('仿真运行中...')

    def _stop_sim(self):
        self._running = False
        self._timer.stop()
        self._logger.flush()
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._pause_btn.setEnabled(False)
        self._pause_btn.setText('暂停显示')
        self._plot.set_paused(False)
        self.statusBar().showMessage('仿真已停止')

    def _toggle_pause(self):
        self._paused_display = not self._paused_display
        self._plot.set_paused(self._paused_display)
        self._pause_btn.setText('继续显示' if self._paused_display else '暂停显示')

    def _toggle_manual(self, checked):
        if checked:
            # 切换到手动：让手动输出框自动跟踪当前控制量，实现无冲击
            self._manual_edit.setText(f'{self._u:.4f}')
        self._manual_edit.setEnabled(checked)
        self._ctrl.set_manual_mode(checked, current_output=self._u, inner_pv=self._inner_pv)
        self.statusBar().showMessage(f'已切换至{"手动" if checked else "自动"}模式')

    def _apply_disturbance(self):
        ok, msg, amp, dur = validate_disturbance(
            self._dist_amp_edit.text(), self._dist_dur_edit.text())
        if not ok:
            QMessageBox.warning(self, '参数错误', msg)
            return
        self._disturbance.apply(amp, dur)
        self._dist_btn.setEnabled(False)

    def _apply_display_points(self):
        try:
            n = int(self._display_edit.text())
            if n <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, '参数错误', '显示点数必须是正整数')
            return
        self._plot.set_max_points(n)
        self.statusBar().showMessage(f'显示点数已更新：{n}')

    def _on_strategy_changed(self, idx):
        strategy = self._strategy_combo.itemData(idx)
        self._ctrl.set_strategy(strategy)
        self._update_strategy_panels()
        self.statusBar().showMessage(f'已切换策略：{ControlStrategy.NAMES[strategy]}')

    def _update_strategy_panels(self):
        s = self._ctrl.strategy
        is_cascade = s in (ControlStrategy.CASCADE, ControlStrategy.CASCADE_FF)
        self._pid_group.setVisible(not is_cascade)
        self._outer_group.setVisible(is_cascade)
        self._inner_group.setVisible(is_cascade)

        if s == ControlStrategy.PLAIN_PID:
            self._limit_label.setText('限幅范围：无限制')
        else:
            self._limit_label.setText(
                f'限幅范围：[{TempConfig.U_MIN}, {TempConfig.U_MAX}]')

    def _on_pid_params(self, kp, ti, td):
        self._ctrl.set_pid_params(kp, ti, td)
        self.statusBar().showMessage(f'PID参数已更新：Kp={kp} Ti={ti} Td={td}')

    def _on_outer_params(self, kp, ti, td):
        self._ctrl.set_outer_params(kp, ti, td)
        self.statusBar().showMessage(f'外环参数已更新：Kp={kp} Ti={ti} Td={td}')

    def _on_inner_params(self, kp, ti, td):
        self._ctrl.set_inner_params(kp, ti, td)
        self.statusBar().showMessage(f'内环参数已更新：Kp={kp} Ti={ti} Td={td}')

    def _apply_model_params(self):
        ok, msg, T1, T2, gain = validate_model_params(
            self._t1_edit.text(), self._t2_edit.text(), self._gain_edit.text())
        if not ok:
            QMessageBox.warning(self, '参数错误', msg)
            return
        self._model.set_params(T1, T2, gain)
        self.statusBar().showMessage(f'模型参数已更新：T1={T1} T2={T2} K={gain}')

    # ------------------------------------------------------------------
    # 菜单回调
    # ------------------------------------------------------------------
    def _logout(self):
        if self._running:
            self._stop_sim()
        current_user.logout()
        self.close()
        from user.login_window import LoginWindow
        login = LoginWindow()
        if login.exec_() == LoginWindow.Accepted:
            w = MainWindow()
            w.show()
            import builtins
            builtins._main_win = w

    def _open_history(self):
        from ui.history_window import HistoryWindow
        win = HistoryWindow(self)
        win.exec_()

    def _change_password(self):
        from ui.change_pwd_ui import ChangePasswordDialog
        dlg = ChangePasswordDialog(self)
        dlg.exec_()

    def _manage_users(self):
        from ui.user_manager_ui import UserManagerWindow
        win = UserManagerWindow(self)
        win.exec_()

    def _about(self):
        QMessageBox.information(
            self, '关于软件',
            'PID温度控制仿真系统 v1.0\n\n'
            '支持5种控制策略：\n'
            '  · 普通PID（无限幅）\n'
            '  · 单回路PID（带抗饱和）\n'
            '  · 前馈+反馈控制\n'
            '  · 串级PID控制\n'
            '  · 串级+前馈控制\n\n'
            '开发语言：Python 3.10+  框架：PyQt5'
        )

    def closeEvent(self, event):
        if self._running:
            self._stop_sim()
        event.accept()
