# backend/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from jose import jwt, JWTError
from backend.config import settings

bearer = HTTPBearer(auto_error=False)

async def get_clerk_public_keys() -> dict:
    url = "https://api.clerk.com/v1/jwks"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers={"Authorization": f"Bearer {settings.clerk_secret_key}"})
        return resp.json()

async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
    token = credentials.credentials
    try:
        header = jwt.get_unverified_header(token)
        jwks = await get_clerk_public_keys()
        key = next((k for k in jwks.get("keys", []) if k["kid"] == header.get("kid")), None)
        if not key:
            raise HTTPException(status_code=401, detail="Invalid token key")
        payload = jwt.decode(token, key, algorithms=["RS256"])
        return {
            "clerk_id": payload["sub"],
            "role": payload.get("public_metadata", {}).get("role", "parent"),
        }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user
