"""串级控制器模块"""
from config import TempConfig, PIDDefaults
from control.pid_controller import PIDController


class CascadeController:
    """串级PID控制器（双回路）"""

    def __init__(self, dt: float = TempConfig.DT):
        self.dt = dt
        self.outer = PIDController(
            kp=PIDDefaults.OUTER_KP,
            ti=PIDDefaults.OUTER_TI,
            td=PIDDefaults.OUTER_TD,
            dt=dt,
            u_max=TempConfig.U_MAX,
            u_min=TempConfig.U_MIN,
        )
        self.inner = PIDController(
            kp=PIDDefaults.INNER_KP,
            ti=PIDDefaults.INNER_TI,
            td=PIDDefaults.INNER_TD,
            dt=dt,
            u_max=TempConfig.U_MAX,
            u_min=TempConfig.U_MIN,
        )
        self._last_inner_sp = 0.0

    def reset(self) -> None:
        self.outer.reset()
        self.inner.reset()

    def compute(self, setpoint: float, outer_pv: float, inner_pv: float) -> float:
        """
        setpoint: 外环设定值
        outer_pv: 外环反馈（被控对象最终输出+干扰）
        inner_pv: 内环反馈（第一惯性环节输出）
        """
        inner_sp = self.outer.compute(setpoint, outer_pv)
        self._last_inner_sp = inner_sp
        output = self.inner.compute(inner_sp, inner_pv)
        return output

    def track_output(self, output: float, inner_pv: float) -> None:
        self.inner.track_output(output)
        # 外环输出是内环设定值，track_output 应跟踪最近一次的内环设定值
        self.outer.track_output(self._last_inner_sp)


class CascadeWithFeedforward:
    """串级+前馈控制器"""

    def __init__(self, dt: float = TempConfig.DT,
                 ff_gain: float = PIDDefaults.FF_GAIN):
        self.cascade = CascadeController(dt=dt)
        self.ff_gain = ff_gain

    def reset(self) -> None:
        self.cascade.reset()

    def compute(self, setpoint: float, outer_pv: float, inner_pv: float,
                disturbance: float) -> float:
        cascade_out = self.cascade.compute(setpoint, outer_pv, inner_pv)
        ff_out = self.ff_gain * disturbance
        output = cascade_out + ff_out
        output = max(TempConfig.U_MIN, min(TempConfig.U_MAX, output))
        return output

    def track_output(self, output: float, inner_pv: float) -> None:
        self.cascade.track_output(output, inner_pv)
