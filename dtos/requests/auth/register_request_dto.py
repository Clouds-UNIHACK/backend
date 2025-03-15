from pydantic import BaseModel

class RegisterRequestDto(BaseModel):
    username: str
    email: str
    password: str