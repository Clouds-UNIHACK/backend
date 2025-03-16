from pydantic import BaseModel


class SaveImageRequestDto(BaseModel):
    kling_url: str
