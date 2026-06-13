# SADS User Service
from fastapi import FastAPI

app = FastAPI(title="SADS User Service", version="1.0.0")

@app.get("/status")
def status():
    return {"service": "user-service", "status": "active"}
