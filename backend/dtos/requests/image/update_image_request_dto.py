from pydantic import BaseModel


class UpdateImageRequestDto(BaseModel):
    id: str
    folder_id: str