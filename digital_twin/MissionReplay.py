from typing import List

class MissionReplay:
    def __init__(self):
        self.recorded_frames: List[dict] = []
        self.playback_index: int = 0

    def record_frame(self, frame: dict):
        self.recorded_frames.append(frame)

    def next_frame(self) -> dict:
        if self.playback_index < len(self.recorded_frames):
            frame = self.recorded_frames[self.playback_index]
            self.playback_index += 1
            return frame
        return {}

    def reset_playback(self):
        self.playback_index = 0
