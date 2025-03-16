from pydantic import BaseModel


class FolderUpdateRequestDto(BaseModel):
    id: str
    name: str
    label_ids: list[str]