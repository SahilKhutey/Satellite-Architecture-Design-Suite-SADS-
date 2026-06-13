from typing import Dict, Any

class KnowledgeBase:
    def __init__(self):
        self.standards: Dict[str, Dict[str, Any]] = {
            "nasa-std-5001": {
                "title": "Structural Design and Test Factors of Safety for Spaceflight Hardware",
                "margin_yield": 1.25,
                "margin_ultimate": 1.40
            },
            "smad-ch11": {
                "title": "Spacecraft Subsystem Design",
                "default_eps_margin": 0.20,
                "default_thermal_margin_k": 10.0,
                "default_pointing_deg": 0.1
            }
        }

    def query_standard(self, standard_id: str) -> Dict[str, Any]:
        return self.standards.get(standard_id.lower(), {})
