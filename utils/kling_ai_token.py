import time
import jwt
import os
import logging

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

KLING_AI_ACCESS_KEY = os.getenv("KLING_AI_ACCESS_KEY", "")
KLING_AI_SECRET_KEY = os.getenv("KLING_AI_SECRET_KEY", "")

def encode_kling_ai_jwt_token():
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }

    payload = {
        "iss": KLING_AI_ACCESS_KEY,
        "exp": int(time.time()) + 1800, # The valid time represents the current time+1800s(30min)
        "nbf": int(time.time()) - 5 # The time when it starts to take effect represents the current time minus 5s
    }

    token = jwt.encode(payload, KLING_AI_SECRET_KEY, headers=headers)
    return token