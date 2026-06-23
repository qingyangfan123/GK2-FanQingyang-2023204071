"""控制策略管理器"""
from typing import Optional
from config import ControlStrategy, TempConfig, PIDDefaults
from control.pid_controller import SimplePIDController, PIDController
from control.cascade_control import CascadeController, CascadeWithFeedforward
from control.feedforward_control import FeedforwardFeedbackController


class ControlStrategyManager:
    """5种控制策略统一管理，支持运行中无缝切换"""

    def __init__(self, dt: float = TempConfig.DT):
        self.dt = dt
        self.strategy = ControlStrategy.PLAIN_PID
        self.manual_mode = False
        self.manual_output = 0.0
        self._last_output = 0.0
        self._last_inner_pv = 0.0
        self._last_inner_sp = 0.0
        self._last_pv = 0.0
        self._last_setpoint = 0.0
        self._last_outer_pv = 0.0

        # 实例化全部控制器
        self._plain_pid = SimplePIDController(dt=dt)
        self._single_pid = PIDController(dt=dt)
        self._ff_ctrl = FeedforwardFeedbackController(dt=dt)
        self._cascade = CascadeController(dt=dt)
        self._cascade_ff = CascadeWithFeedforward(dt=dt)

    # ------------------------------------------------------------------
    # 策略切换
    # ------------------------------------------------------------------
    def set_strategy(self, strategy: int) -> None:
        if strategy == self.strategy:
            return
        self.strategy = strategy
        # 计算当前误差，用于设置目标控制器的 _prev_error，避免微分冲击
        error = self._last_setpoint - self._last_pv
        # 让新策略的控制器积分跟踪当前输出，实现无缝切换
        if strategy == ControlStrategy.PLAIN_PID:
            self._plain_pid._prev_error = error
            self._plain_pid.track_output(self._last_output)
        elif strategy == ControlStrategy.SINGLE_PID:
            self._single_pid._prev_error = error
            self._single_pid.track_output(self._last_output)
        elif strategy == ControlStrategy.FEEDFORWARD:
            self._ff_ctrl.pid._prev_error = error
            self._ff_ctrl.track_output(self._last_output)
        elif strategy == ControlStrategy.CASCADE:
            outer_error = self._last_setpoint - self._last_outer_pv
            inner_error = self._last_inner_sp - self._last_inner_pv
            self._cascade.outer._prev_error = outer_error
            self._cascade.inner._prev_error = inner_error
            self._cascade.track_output(self._last_output, self._last_inner_pv)
        elif strategy == ControlStrategy.CASCADE_FF:
            outer_error = self._last_setpoint - self._last_outer_pv
            inner_error = self._last_inner_sp - self._last_inner_pv
            self._cascade_ff.cascade.outer._prev_error = outer_error
            self._cascade_ff.cascade.inner._prev_error = inner_error
            self._cascade_ff.track_output(self._last_output, self._last_inner_pv)

    def set_manual_mode(self, manual: bool, current_output: float,
                        inner_pv: float = 0.0) -> None:
        if manual == self.manual_mode:
            return
        self.manual_mode = manual
        if not manual:
            # 切回自动：同步当前误差并跟踪当前手动输出，实现无扰切换
            error = self._last_setpoint - self._last_pv
            if self.strategy == ControlStrategy.PLAIN_PID:
                self._plain_pid._prev_error = error
                self._plain_pid.track_output(current_output)
            elif self.strategy == ControlStrategy.SINGLE_PID:
                self._single_pid._prev_error = error
                self._single_pid.track_output(current_output)
            elif self.strategy == ControlStrategy.FEEDFORWARD:
                self._ff_ctrl.pid._prev_error = error
                self._ff_ctrl.track_output(current_output)
            elif self.strategy == ControlStrategy.CASCADE:
                outer_error = self._last_setpoint - self._last_outer_pv
                inner_error = current_output - inner_pv
                self._cascade.outer._prev_error = outer_error
                self._cascade.inner._prev_error = inner_error
                # 手动输出视为内环设定值，同步后再做无扰跟踪
                self._cascade._last_inner_sp = current_output
                self._cascade.track_output(current_output, inner_pv)
            elif self.strategy == ControlStrategy.CASCADE_FF:
                outer_error = self._last_setpoint - self._last_outer_pv
                inner_error = current_output - inner_pv
                self._cascade_ff.cascade.outer._prev_error = outer_error
                self._cascade_ff.cascade.inner._prev_error = inner_error
                self._cascade_ff.cascade._last_inner_sp = current_output
                self._cascade_ff.track_output(current_output, inner_pv)

    # ------------------------------------------------------------------
    # 计算输出
    # ------------------------------------------------------------------
    def compute(self, setpoint: float, pv: float,
                inner_pv: float = 0.0,
                disturbance: float = 0.0,
                outer_pv: Optional[float] = None) -> float:
        if self.manual_mode:
            self._last_output = self.manual_output
            self._last_pv = pv
            self._last_setpoint = setpoint
            self._last_inner_pv = inner_pv
            if outer_pv is not None:
                self._last_outer_pv = outer_pv
            return self.manual_output

        if outer_pv is None:
            outer_pv = pv

        s = self.strategy
        if s == ControlStrategy.PLAIN_PID:
            output = self._plain_pid.compute(setpoint, pv)
        elif s == ControlStrategy.SINGLE_PID:
            output = self._single_pid.compute(setpoint, pv)
        elif s == ControlStrategy.FEEDFORWARD:
            output = self._ff_ctrl.compute(setpoint, pv, disturbance)
        elif s == ControlStrategy.CASCADE:
            output = self._cascade.compute(setpoint, outer_pv, inner_pv)
            self._last_inner_sp = self._cascade._last_inner_sp
        elif s == ControlStrategy.CASCADE_FF:
            output = self._cascade_ff.compute(setpoint, outer_pv, inner_pv, disturbance)
            self._last_inner_sp = self._cascade_ff.cascade._last_inner_sp
        else:
            output = 0.0

        self._last_output = output
        self._last_inner_pv = inner_pv
        self._last_pv = pv
        self._last_setpoint = setpoint
        self._last_outer_pv = outer_pv
        return output

    # ------------------------------------------------------------------
    # 参数设置
    # ------------------------------------------------------------------
    def set_pid_params(self, kp: float, ti: float, td: float) -> None:
        self._plain_pid.set_params(kp, ti, td)
        self._single_pid.set_params(kp, ti, td)
        self._ff_ctrl.set_params(kp, ti, td)

    def set_outer_params(self, kp: float, ti: float, td: float) -> None:
        self._cascade.outer.set_params(kp, ti, td)
        self._cascade_ff.cascade.outer.set_params(kp, ti, td)

    def set_inner_params(self, kp: float, ti: float, td: float) -> None:
        self._cascade.inner.set_params(kp, ti, td)
        self._cascade_ff.cascade.inner.set_params(kp, ti, td)

    def reset_all(self) -> None:
        self._plain_pid.reset()
        self._single_pid.reset()
        self._ff_ctrl.reset()
        self._cascade.reset()
        self._cascade_ff.reset()

    def set_limits(self, u_min: float, u_max: float) -> None:
        """动态更新所有控制器的输出限幅"""
        TempConfig.U_MIN = u_min
        TempConfig.U_MAX = u_max
        # 单回路 PID
        self._single_pid.u_min = u_min
        self._single_pid.u_max = u_max
        # 前馈+反馈
        self._ff_ctrl.pid.u_min = u_min
        self._ff_ctrl.pid.u_max = u_max
        # 串级外环 / 内环
        self._cascade.outer.u_min = u_min
        self._cascade.outer.u_max = u_max
        self._cascade.inner.u_min = u_min
        self._cascade.inner.u_max = u_max
        # 串级+前馈
        self._cascade_ff.cascade.outer.u_min = u_min
        self._cascade_ff.cascade.outer.u_max = u_max
        self._cascade_ff.cascade.inner.u_min = u_min
        self._cascade_ff.cascade.inner.u_max = u_max

    # ------------------------------------------------------------------
    # 属性快捷访问
    # ------------------------------------------------------------------
    @property
    def pid(self) -> PIDController:
        return self._single_pid

    @property
    def plain_pid(self) -> SimplePIDController:
        return self._plain_pid

    @property
    def cascade(self) -> CascadeController:
        return self._cascade
