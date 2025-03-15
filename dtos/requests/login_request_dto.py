from pydantic import BaseModel

class LoginRequestDto(BaseModel):
    username: str
    password: str