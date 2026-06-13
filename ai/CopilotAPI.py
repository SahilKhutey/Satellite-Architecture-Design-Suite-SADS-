# SADS - Copilot API
from fastapi import APIRouter
from .ArchitectureAdvisor import ArchitectureAdvisor
from .AerospaceRAG import AerospaceRAG

router = APIRouter()

@router.get("/ai/advise")
def advise(power_margin: float = 0.15, thermal_margin: float = 5.0):
    recs = ArchitectureAdvisor.analyze_margins(power_margin, thermal_margin, 0.05)
    ref = AerospaceRAG.query_reference("power")
    return {"recommendations": recs, "reference": ref}
