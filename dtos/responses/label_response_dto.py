from typing import Optional

from pydantic import BaseModel


class LabelResponseDto(BaseModel):
    name: str
    color: Optional[str]