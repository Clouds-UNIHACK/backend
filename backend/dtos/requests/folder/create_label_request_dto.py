from typing import Optional

from pydantic import BaseModel


class CreateLabelRequestDto(BaseModel):
    name: str
    color: Optional[str]
