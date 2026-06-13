# SADS AI Copilot Service
import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Enable importing from root folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.ArchitectureAdvisor import ArchitectureAdvisor
from ai.OptimizationAgent import OptimizationAgent

app = FastAPI(title="SADS AI Copilot Service", version="1.0.0")

class ReviewRequest(BaseModel):
    power_margin: float
    thermal_margin_k: float
    pointing_error_deg: float

class OptimizeRequest(BaseModel):
    load_w: float
    eclipse_min: float
    cost_factor: float = 1.0

@app.get("/status")
def status():
    return {"service": "ai-copilot-service", "status": "active"}

@app.post("/api/ai/review")
def ai_review(req: ReviewRequest):
    recs = ArchitectureAdvisor.analyze_margins(
        power_margin=req.power_margin,
        thermal_margin_k=req.thermal_margin_k,
        pointing_error_deg=req.pointing_error_deg
    )
    return {
        "status": "warning" if recs else "optimal",
        "recommendations": recs
    }

@app.post("/api/ai/optimize")
def ai_optimize(req: OptimizeRequest):
    result = OptimizationAgent.optimize_eps(
        load_w=req.load_w,
        eclipse_min=req.eclipse_min,
        cost_factor=req.cost_factor
    )
    return result
