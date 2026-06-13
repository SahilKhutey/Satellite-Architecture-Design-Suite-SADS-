# SADS - PID Controller
class PIDController:
    def __init__(self, kp: float, ki: float, kd: float):
        self.kp = kp
        self.ki = ki
        self.kd = kd
    def command(self, error: float, dt: float) -> float:
        return self.kp * error
