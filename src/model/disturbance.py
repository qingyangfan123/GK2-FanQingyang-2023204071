"""干扰信号发生器"""


class SquareWaveDisturbance:
    """方波干扰信号（施加一次，持续指定秒数后自动结束）"""

    def __init__(self, dt: float = 0.1):
        self.dt = dt
        self._amplitude = 0.0
        self._remaining_steps = 0
        self._active = False

    def apply(self, amplitude: float, duration: float) -> None:
        """施加方波干扰"""
        self._amplitude = amplitude
        self._remaining_steps = max(1, int(duration / self.dt))
        self._active = True

    def step(self) -> float:
        """每个仿真步调用一次，返回当前干扰值"""
        if not self._active or self._remaining_steps <= 0:
            self._active = False
            return 0.0
        self._remaining_steps -= 1
        if self._remaining_steps <= 0:
            self._active = False
        return self._amplitude

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def remaining_steps(self) -> int:
        return self._remaining_steps
