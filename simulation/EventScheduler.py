from typing import List, Tuple, Callable

class EventScheduler:
    def __init__(self):
        self.events: List[Tuple[float, Callable[[], None]]] = []

    def schedule_event(self, time_s: float, callback: Callable[[], None]):
        self.events.append((time_s, callback))
        self.events.sort(key=lambda x: x[0])

    def trigger_events(self, current_time_s: float):
        triggered = []
        for time_s, cb in list(self.events):
            if time_s <= current_time_s:
                cb()
                triggered.append((time_s, cb))
        for item in triggered:
            self.events.remove(item)
