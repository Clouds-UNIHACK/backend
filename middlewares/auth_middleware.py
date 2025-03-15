from fastapi import HTTPException, Request
import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from backend.utils.jwt_token import decode_payload_from_jwt

EXCLUDED_PATHS = {"/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/generate-image"}  # Set for fast lookup

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)  # Skip authentication for excluded paths

        authorization = request.headers.get("Authorization")
        if not authorization:
            return JSONResponse(status_code=401, content="Unauthorized")

        token = authorization.replace("Bearer ", "")
        try:
            payload = decode_payload_from_jwt(token)
        except jwt.ExpiredSignatureError:
            return JSONResponse(status_code=401, content="Token expired")
        except jwt.InvalidTokenError:
            return JSONResponse(status_code=401, content="Invalid token")

        user_id = payload.get("id")
        if not user_id:
            return JSONResponse(status_code=401, content="Invalid token")

        request.state.user_id = user_id  # Attach user ID to request

        return await call_next(request)

