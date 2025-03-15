from functools import reduce
from http.client import HTTPException
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.session import get_session
from backend.dtos.requests.folder.create_label_request_dto import CreateLabelRequestDto
from backend.dtos.requests.folder.label_update_request_dto import LabelUpdateRequestDto
from backend.mappers.labels_mapper import map_label_to_label_response_dto
from backend.repositories.folder_repository import FolderRepository
from backend.repositories.image_repository import ImageRepository
from backend.repositories.label_repository import LabelRepository
from backend.services.cloudinary_service import delete_image_from_cloudinary
from starlette.responses import JSONResponse

router = APIRouter(prefix="/api/v1", tags=["Labels"])

@router.post("/create-label")
async def create_label(
        data_request: CreateLabelRequestDto,
        http_request: Request,
        db: AsyncSession = Depends(get_session)
):
    user_id = http_request.state.user_id

    try:
        new_label = await LabelRepository.create_label(db, data_request.name, data_request.color, user_id)
        return JSONResponse(content=map_label_to_label_response_dto(new_label), status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot create folder to the database {e}")

@router.get("/labels")
async def get_labels(
        http_request: Request,
        db: AsyncSession = Depends(get_session)
):
    try:
        # Get all labels from the current user
        user_id = http_request.state.user_id

        labels = await LabelRepository.get_labels_by_user_id(db, user_id)
        labels_dto = reduce(lambda lists, label: lists.append(map_label_to_label_response_dto(label)), labels, [])
        return JSONResponse(content=labels_dto, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

@router.put("/update-label")
async def update_label(
        data_request: LabelUpdateRequestDto,
        http_request: Request,
        db: AsyncSession = Depends(get_session)
):
    try:
        label = await LabelRepository.get_label_by_id(db, data_request.id)

        # If the label doesn't have the same user_id as the current request user_id, they are doing something naughty :3
        if http_request.state.user_id != label.user_id: raise Exception("Unauthorized")

        # Update label's name and color
        new_color = await LabelRepository.update_label(db, data_request.name, data_request.color, data_request.id)

        return JSONResponse(content=map_label_to_label_response_dto(new_color), status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

@router.delete("/delete-label/{label_id}")
async def delete_label(
        label_id: str,
        http_request: Request,
        db: AsyncSession = Depends(get_session)
):
    try:
        user_id = http_request.state.user_id

        # Get label
        label = await LabelRepository.get_label_by_id(db, label_id)

        # If the deleted label doesn't have the same user_id as the current request user_id, they are doing something naughty :3
        if user_id != label.user_id: raise Exception("Unauthorized")

        await LabelRepository.delete_label(db, label_id)
        return JSONResponse(content={"result": "ok"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)