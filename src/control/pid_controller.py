"""PID控制器模块"""
from config import TempConfig, PIDDefaults


class SimplePIDController:
    """普通PID控制器（无限幅、无抗饱和，用于教学演示积分饱和）"""

    def __init__(self, kp: float = PIDDefaults.KP,
                 ti: float = PIDDefaults.TI,
                 td: float = PIDDefaults.TD,
                 dt: float = TempConfig.DT):
        self.kp = kp
        self.ti = ti
        self.td = td
        self.dt = dt
        self._integral = 0.0
        self._prev_error = 0.0

    def reset(self) -> None:
        self._integral = 0.0
        self._prev_error = 0.0

    def compute(self, setpoint: float, pv: float) -> float:
        error = setpoint - pv
        self._integral += error * self.dt
        derivative = (error - self._prev_error) / self.dt if self.dt > 0 else 0.0
        self._prev_error = error
        ki = self.kp / self.ti if self.ti > 0 else 0.0
        kd = self.kp * self.td
        return self.kp * error + ki * self._integral + kd * derivative

    def set_params(self, kp: float, ti: float, td: float) -> None:
        self.kp = kp
        self.ti = ti
        self.td = td

    def track_output(self, output: float) -> None:
        """手动切回自动时让积分跟踪当前输出，实现无扰切换。"""
        ki = self.kp / self.ti if self.ti > 0 else 0.0
        if ki != 0:
            # _prev_error 已在 set_strategy / set_manual_mode 中同步为当前误差
            current_error = self._prev_error
            self._integral = (output - self.kp * current_error) / ki
        else:
            self._integral = 0.0
        # 注意：不重置 _prev_error，否则切换后微分项会产生冲击


class PIDController:
    """带抗积分饱和的位置式PID控制器"""

    def __init__(self, kp: float = PIDDefaults.KP,
                 ti: float = PIDDefaults.TI,
                 td: float = PIDDefaults.TD,
                 dt: float = TempConfig.DT,
                 u_max: float = TempConfig.U_MAX,
                 u_min: float = TempConfig.U_MIN):
        self.kp = kp
        self.ti = ti
        self.td = td
        self.dt = dt
        self.u_max = u_max
        self.u_min = u_min
        self._integral = 0.0
        self._prev_error = 0.0

    def reset(self) -> None:
        self._integral = 0.0
        self._prev_error = 0.0

    def compute(self, setpoint: float, pv: float) -> float:
        error = setpoint - pv
        ki = self.kp / self.ti if self.ti > 0 else 0.0
        kd = self.kp * self.td
        derivative = (error - self._prev_error) / self.dt if self.dt > 0 else 0.0

        # 计算当前输出（不含积分）
        output_no_i = self.kp * error + ki * self._integral + kd * derivative

        # 条件积分抗饱和
        saturated_high = output_no_i > self.u_max and error > 0
        saturated_low = output_no_i < self.u_min and error < 0
        if not (saturated_high or saturated_low):
            self._integral += error * self.dt

        output = self.kp * error + ki * self._integral + kd * derivative
        output = max(self.u_min, min(self.u_max, output))
        self._prev_error = error
        return output

    def set_params(self, kp: float, ti: float, td: float) -> None:
        self.kp = kp
        self.ti = ti
        self.td = td

    def track_output(self, output: float) -> None:
        """手动模式下让积分跟踪当前输出，实现无扰切换。"""
        ki = self.kp / self.ti if self.ti > 0 else 0.0
        if ki != 0:
            # _prev_error 已在 set_strategy / set_manual_mode 中同步为当前误差
            current_error = self._prev_error
            self._integral = (output - self.kp * current_error) / ki
        else:
            self._integral = 0.0
        # 注意：不重置 _prev_error，否则切换后微分项会产生冲击
