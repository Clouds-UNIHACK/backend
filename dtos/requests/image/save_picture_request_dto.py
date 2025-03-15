from pydantic import BaseModel


class SavePictureRequestDto(BaseModel):
    kling_url: str
