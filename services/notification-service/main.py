# SADS Notification Service
from fastapi import FastAPI

app = FastAPI(title="SADS Notification Service", version="1.0.0")

@app.get("/status")
def status():
    return {"service": "notification-service", "status": "active"}
