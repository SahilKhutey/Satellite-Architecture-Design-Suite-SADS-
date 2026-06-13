# SADS - Traceability Engine
from typing import Dict, List

class TraceabilityEngine:
    def __init__(self):
        self.trace_map: Dict[str, List[str]] = {}  # requirement_id -> list of component_ids

    def add_trace(self, requirement_id: str, component_id: str):
        if requirement_id not in self.trace_map:
            self.trace_map[requirement_id] = []
        self.trace_map[requirement_id].append(component_id)

    def get_components_for_requirement(self, requirement_id: str) -> List[str]:
        return self.trace_map.get(requirement_id, [])
