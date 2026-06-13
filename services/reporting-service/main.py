# SADS Reporting Service
from fastapi import FastAPI

app = FastAPI(title="SADS Reporting Service", version="1.0.0")

@app.get("/status")
def status():
    return {"service": "reporting-service", "status": "active"}
