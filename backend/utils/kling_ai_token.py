import time
import jwt

from backend.config import KLING_AI_ACCESS_KEY, KLING_AI_SECRET_KEY


def encode_kling_ai_jwt_token():

    header = {
        "alg": "HS256",
        "typ": "JWT"
    }

    payload = {
        "iss": KLING_AI_ACCESS_KEY,
        "exp": int(time.time()) + 1800, # The valid time represents the current time+1800s(30min)
        "nbf": int(time.time()) - 5 # The time when it starts to take effect represents the current time minus 5s
    }


    return jwt.encode(payload, KLING_AI_SECRET_KEY, algorithm="HS256", headers=header)