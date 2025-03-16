from backend.dtos.responses.label_response_dto import LabelResponseDto
from backend.models.label import Label

def map_label_to_label_response_dto(label: Label) -> LabelResponseDto:
    return LabelResponseDto(id=str(label.id), name=label.name, color=label.color)