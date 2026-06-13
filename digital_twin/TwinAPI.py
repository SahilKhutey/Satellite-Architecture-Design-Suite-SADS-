from fastapi import APIRouter
from .TwinCore import TwinCore
from .StateSynchronizer import StateSynchronizer

router = APIRouter()
core = TwinCore("DEFAULT-SAT")

@router.get("/twin/state")
def get_twin_state():
    return core.current_state

@router.post("/twin/telemetry")
def post_telemetry(data: dict):
    est_temp = core.current_state.get("temp_k", 298.15)
    measured_temp = data.get("temp_k")
    
    if measured_temp is not None:
        synced_temp = StateSynchronizer.filter_step(est_temp, measured_temp, gain=0.1)
        data["temp_k"] = synced_temp
        
    core.update_state(data)
    return {"status": "SUCCESS", "synchronized_state": core.current_state}
