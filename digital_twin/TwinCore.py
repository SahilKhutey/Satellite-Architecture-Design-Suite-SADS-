# SADS - Digital Twin Core
class TwinCore:
    def __init__(self, spacecraft_id: str):
        self.spacecraft_id = spacecraft_id
        self.telemetry_history = []
        self.current_state = {}

    def update_state(self, val: dict):
        self.current_state = val
        self.telemetry_history.append(val)
