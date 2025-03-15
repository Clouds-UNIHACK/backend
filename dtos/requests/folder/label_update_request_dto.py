from pydantic import BaseModel

class LabelUpdateRequestDto(BaseModel):
    id: str
    name: str
    color: str