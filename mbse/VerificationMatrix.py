# SADS - Verification Matrix
from typing import List, Dict
from .RequirementsManager import RequirementsManager
from .TraceabilityEngine import TraceabilityEngine

class VerificationMatrix:
    @staticmethod
    def verify_all(req_manager: RequirementsManager, trace_engine: TraceabilityEngine, component_values: Dict[str, float]) -> List[dict]:
        results = []
        for req_id, req in req_manager.requirements.items():
            component_ids = trace_engine.get_components_for_requirement(req_id)
            total_value = sum(component_values.get(cid, 0.0) for cid in component_ids)
            satisfied = req.is_satisfied(total_value)
            results.append({
                "requirement_id": req_id,
                "satisfied": satisfied,
                "measured_value": total_value,
                "limit_value": req.limit_value
            })
        return results
