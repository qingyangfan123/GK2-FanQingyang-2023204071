"""反馈（传感器）环节模型"""
from config import TempConfig


class FeedbackModel:
    """一阶低通滤波器模拟传感器动态 H(s)=1/(Tc*s+1)"""

    def __init__(self, Tc: float = TempConfig.TC, dt: float = TempConfig.DT):
        self.Tc = Tc
        self.dt = dt
        self._y = 0.0

    def reset(self) -> None:
        self._y = 0.0

    def step(self, u: float) -> float:
        alpha = self.dt / (self.Tc + self.dt)
        self._y = self._y + alpha * (u - self._y)
        return self._y

    @property
    def output(self) -> float:
        return self._y
