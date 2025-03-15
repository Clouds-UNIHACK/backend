from pydantic import BaseModel


class UpdateImageRequestDto(BaseModel):
    image_id: str
    folder_id: str