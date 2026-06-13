# SADS Authentication Service
import os
import jwt
import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

app = FastAPI(title="SADS Authentication", version="1.0.0")

JWT_SECRET = os.getenv("JWT_SECRET", "sads_super_secret_jwt_key_2026")
security = HTTPBearer()

class AuthUser(BaseModel):
    username: str
    password: str

@app.post("/register")
def register(user: AuthUser):
    # Stub registration
    return {"status": "success", "username": user.username}

@app.post("/login")
def login(user: AuthUser):
    # In production, check credentials against postgres database
    if user.username == "admin" and user.password == "admin":
        payload = {
            "sub": user.username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/verify")
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return {"username": payload["sub"], "status": "authorized"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
