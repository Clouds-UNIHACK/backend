from fastapi import Request, HTTPException, Response
from typing import Callable
from functools import wraps
import jwt
from sqlmodel import Session, select
from models.user import User
from utils.jwt import decode_payload_from_jwt  # Your JWT decoding function


# Middleware for checking Authorization token
def auth_middleware(db: Session):
    """
    Authorization middleware to check if the Bearer token is valid and attach the associated user to the request.
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, response: Response, *args, **kwargs):
            # Unauthorized response function
            def unauthenticated():
                raise HTTPException(status_code=401, detail="Unauthorized")

            # Check Authorization header
            authorization = request.headers.get("Authorization")
            if not authorization:
                return unauthenticated()

            # Extract token from Bearer header
            token = authorization.replace("Bearer ", "")
            try:
                payload = decode_payload_from_jwt(token)  # Decode and verify JWT
            except jwt.ExpiredSignatureError:
                return unauthenticated()
            except jwt.JWTError:
                return unauthenticated()

            # Extract user ID from payload
            user_id = payload.get("id")
            if not user_id:
                return unauthenticated()

            # Query user from database using SQLModel
            statement = select(User).where(User.id == user_id)
            user = db.exec(statement).first()
            if not user:
                return unauthenticated()

            # Attach user to the request object
            request.state.user = user

            return await func(request, response, *args, **kwargs)

        return wrapper

    return decorator
