from typing import Optional

from pydantic import BaseModel


class LabelResponseDto(BaseModel):
    id: str
    name: str
    color: Optional[str]