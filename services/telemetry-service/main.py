# SADS Telemetry Service
from fastapi import FastAPI

app = FastAPI(title="SADS Telemetry Service", version="1.0.0")

@app.get("/status")
def status():
    return {"service": "telemetry-service", "status": "active"}
