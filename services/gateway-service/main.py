# SADS API Gateway Service
import os
import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="SADS API Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Backend endpoints routing URLs
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
SIMULATION_SERVICE_URL = os.getenv("SIMULATION_SERVICE_URL", "http://localhost:8002")
DIGITAL_TWIN_SERVICE_URL = os.getenv("DIGITAL_TWIN_SERVICE_URL", "http://localhost:8005")
AI_COPILOT_SERVICE_URL = os.getenv("AI_COPILOT_SERVICE_URL", "http://localhost:8006")

client = httpx.AsyncClient()

@app.get("/api/status")
async def status():
    return {
        "service": "Gateway",
        "status": "operational",
        "auth_url": AUTH_SERVICE_URL,
        "simulation_url": SIMULATION_SERVICE_URL,
        "digital_twin_url": DIGITAL_TWIN_SERVICE_URL,
        "ai_copilot_url": AI_COPILOT_SERVICE_URL
    }

@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_auth(request: Request, path: str):
    url = f"{AUTH_SERVICE_URL}/{path}"
    return await forward_request(request, url)

@app.api_route("/api/simulation/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_simulation(request: Request, path: str):
    url = f"{SIMULATION_SERVICE_URL}/{path}"
    return await forward_request(request, url)

@app.api_route("/api/twin/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_twin(request: Request, path: str):
    url = f"{DIGITAL_TWIN_SERVICE_URL}/api/twin/{path}"
    return await forward_request(request, url)

@app.api_route("/api/ai/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_ai(request: Request, path: str):
    url = f"{AI_COPILOT_SERVICE_URL}/api/ai/{path}"
    return await forward_request(request, url)


async def forward_request(request: Request, url: str) -> Response:
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)
    
    try:
        resp = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
            params=request.query_params,
            timeout=10.0
        )
        return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Service unavailable: {str(e)}")

# Mount static web files if in production directory
WEB_DIR = "/app/apps/web"
if os.path.exists(WEB_DIR):
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web_client")
elif os.path.exists("./apps/web"):
    app.mount("/", StaticFiles(directory="./apps/web", html=True), name="web_client")
