from typing import List

from pydantic import BaseModel

from backend.dtos.responses.label_response_dto import LabelResponseDto


class FolderResponseDto(BaseModel):
    id: str
    name: str
    labels: List[LabelResponseDto]