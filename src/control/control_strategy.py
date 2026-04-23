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
        self.strategy = strategy

    def set_manual_mode(self, manual: bool, current_output: float,
                        inner_pv: float = 0.0) -> None:
        if manual == self.manual_mode:
            return
        self.manual_mode = manual
        if not manual:
            # 切回自动：让各控制器积分跟踪当前手动输出，实现无扰切换
            self._single_pid.track_output(current_output)
            self._ff_ctrl.track_output(current_output)
            self._cascade.track_output(current_output, inner_pv)
            self._cascade_ff.track_output(current_output, inner_pv)
            self._plain_pid.track_output(current_output)

    # ------------------------------------------------------------------
    # 计算输出
    # ------------------------------------------------------------------
    def compute(self, setpoint: float, pv: float,
                inner_pv: float = 0.0,
                disturbance: float = 0.0,
                outer_pv: Optional[float] = None) -> float:
        if self.manual_mode:
            return self.manual_output

        if outer_pv is None:
            outer_pv = pv

        s = self.strategy
        if s == ControlStrategy.PLAIN_PID:
            return self._plain_pid.compute(setpoint, pv)
        elif s == ControlStrategy.SINGLE_PID:
            return self._single_pid.compute(setpoint, pv)
        elif s == ControlStrategy.FEEDFORWARD:
            return self._ff_ctrl.compute(setpoint, pv, disturbance)
        elif s == ControlStrategy.CASCADE:
            return self._cascade.compute(setpoint, outer_pv, inner_pv)
        elif s == ControlStrategy.CASCADE_FF:
            return self._cascade_ff.compute(setpoint, outer_pv, inner_pv, disturbance)
        return 0.0

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
