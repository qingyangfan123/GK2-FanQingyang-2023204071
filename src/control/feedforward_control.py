"""前馈控制器模块"""
from config import TempConfig, PIDDefaults
from control.pid_controller import PIDController


class FeedforwardFeedbackController:
    """前馈+反馈复合控制器"""

    def __init__(self, dt: float = TempConfig.DT,
                 ff_gain: float = PIDDefaults.FF_GAIN):
        self.dt = dt
        self.ff_gain = ff_gain
        self.pid = PIDController(
            kp=PIDDefaults.KP,
            ti=PIDDefaults.TI,
            td=PIDDefaults.TD,
            dt=dt,
            u_max=TempConfig.U_MAX,
            u_min=TempConfig.U_MIN,
        )

    def reset(self) -> None:
        self.pid.reset()

    def compute(self, setpoint: float, pv: float, disturbance: float) -> float:
        fb_out = self.pid.compute(setpoint, pv)
        ff_out = self.ff_gain * disturbance
        output = fb_out + ff_out
        output = max(TempConfig.U_MIN, min(TempConfig.U_MAX, output))
        return output

    def track_output(self, output: float) -> None:
        self.pid.track_output(output)

    def set_params(self, kp: float, ti: float, td: float) -> None:
        self.pid.set_params(kp, ti, td)
