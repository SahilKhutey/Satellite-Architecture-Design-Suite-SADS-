# SADS File Service
from fastapi import FastAPI

app = FastAPI(title="SADS File Service", version="1.0.0")

@app.get("/status")
def status():
    return {"service": "file-service", "status": "active"}
