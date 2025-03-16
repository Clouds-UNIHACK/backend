from typing import List

from pydantic import BaseModel


class RecommendImageRequestDto(BaseModel):
    image_urls = List[str]
    prompt: str