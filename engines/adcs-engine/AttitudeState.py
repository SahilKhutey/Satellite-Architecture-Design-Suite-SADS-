# SADS - Attitude State
class AttitudeState:
    def __init__(self, q: list = None, w: list = None):
        self.q = q if q else [0.0, 0.0, 0.0, 1.0]  # Quaternion
        self.w = w if w else [0.0, 0.0, 0.0]  # Angular velocity
