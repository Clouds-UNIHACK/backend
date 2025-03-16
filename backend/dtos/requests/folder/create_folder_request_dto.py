from pydantic import BaseModel


class CreateFolderRequestDto(BaseModel):
    name: str