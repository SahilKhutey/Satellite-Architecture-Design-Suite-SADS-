# SADS - Requirements Manager
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Requirement:
    id: str
    name: str
    category: str  # "mass" | "power" | "thermal" | "cost"
    limit_value: float
    operator: str  # "less_than" | "greater_than"

    def is_satisfied(self, current_value: float) -> bool:
        if self.operator == "less_than":
            return current_value <= self.limit_value
        elif self.operator == "greater_than":
            return current_value >= self.limit_value
        return False

class RequirementsManager:
    def __init__(self):
        self.requirements: Dict[str, Requirement] = {}

    def add_requirement(self, req: Requirement):
        self.requirements[req.id] = req

    def get_category_requirements(self, category: str) -> List[Requirement]:
        return [r for r in self.requirements.values() if r.category == category]
