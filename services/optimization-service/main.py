# SADS Optimization Service
from fastapi import FastAPI

app = FastAPI(title="SADS Optimization Service", version="1.0.0")

@app.get("/status")
def status():
    return {"service": "optimization-service", "status": "active"}
