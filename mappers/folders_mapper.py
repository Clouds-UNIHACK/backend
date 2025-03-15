from functools import reduce

from backend.mappers.labels_mapper import map_label_to_label_response_dto
from backend.models.folder import Folder

from backend.dtos.responses.folder_response_dto import FolderResponseDto


def map_folder_to_folder_response_dto(folder: Folder) -> FolderResponseDto:
    labels_dto = reduce(lambda lists, label: lists.append(map_label_to_label_response_dto(label)), folder.labels, [])
    return FolderResponseDto(id=str(folder.id), name=folder.name, labels=labels_dto)