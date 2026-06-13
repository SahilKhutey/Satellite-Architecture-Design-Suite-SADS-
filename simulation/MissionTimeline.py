# SADS - Mission Timeline
from dataclasses import dataclass, field
from typing import List

@dataclass
class MissionTimeline:
    satellite_name: str
    phases: List[str] = field(default_factory=list)
