import jwt
from datetime import datetime, timedelta

import os
from typing import Union, Optional, Dict, Any

from backend.config import SECRET_KEY

# Secret key for encoding and decoding the JWT token
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120


# Function to create an access token
def create_access_token(
    payload: dict,
    expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
) -> str:

    to_encode = payload.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_payload_from_jwt(token: str) -> Optional[Dict[str, Any]]:
    try:
        decoded = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=ALGORITHM,  # Ensure that the algorithm used for verification matches the signing algorithm
            options={"verify_exp": True},  # Verify expiration by default
        )
        return decoded
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None
