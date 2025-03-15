from pydantic import BaseModel


class ImageResponseDto(BaseModel):
    id: str
    url: str