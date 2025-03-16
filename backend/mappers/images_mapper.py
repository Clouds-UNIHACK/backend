from backend.dtos.responses.image_response_dto import ImageResponseDto
from backend.models.image import Image

def map_image_to_image_response_dto(image: Image) -> ImageResponseDto:
    return ImageResponseDto(id=str(image.id), url=image.url)
