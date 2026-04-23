"""双惯性环节被控对象模型"""
from typing import Tuple
from config import TempConfig


class FirstOrderLag:
    """一阶惯性环节（欧拉离散化）"""

    def __init__(self, T: float, gain: float = 1.0, dt: float = TempConfig.DT):
        self.T = T
        self.gain = gain
        self.dt = dt
        self._y = 0.0

    def reset(self) -> None:
        self._y = 0.0

    def step(self, u: float) -> float:
        alpha = self.dt / (self.T + self.dt)
        self._y = self._y + alpha * (self.gain * u - self._y)
        return self._y

    @property
    def output(self) -> float:
        return self._y


class TwoInertiaModel:
    """双惯性环节串联被控对象 G(s)=K/((T1s+1)(T2s+1))"""

    def __init__(self,
                 T1: float = TempConfig.T1_DEFAULT,
                 T2: float = TempConfig.T2_DEFAULT,
                 gain: float = TempConfig.GAIN_DEFAULT,
                 dt: float = TempConfig.DT):
        self.lag1 = FirstOrderLag(T=T1, gain=gain, dt=dt)
        self.lag2 = FirstOrderLag(T=T2, gain=1.0, dt=dt)
        self.dt = dt

    def reset(self) -> None:
        self.lag1.reset()
        self.lag2.reset()

    def step(self, u: float) -> Tuple[float, float]:
        """
        返回 (inner_output, final_output)
        inner_output: 第一惯性环节输出（供串级内环反馈）
        final_output: 第二惯性环节输出（未加干扰）
        """
        inner = self.lag1.step(u)
        final = self.lag2.step(inner)
        return inner, final

    def set_params(self, T1: float, T2: float, gain: float) -> None:
        self.lag1.T = T1
        self.lag1.gain = gain
        self.lag2.T = T2
