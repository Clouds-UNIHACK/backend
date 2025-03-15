import uuid
from copy import deepcopy
from functools import reduce
from http.client import HTTPException
from fastapi import APIRouter, Depends, Request, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.session import get_session
from backend.dtos.requests.folder.create_folder_request_dto import CreateFolderRequestDto
from backend.dtos.requests.folder.folder_update_request_dto import FolderUpdateRequestDto
from backend.mappers.folders_mapper import map_folder_to_folder_response_dto
from backend.repositories.folder_repository import FolderRepository
from backend.repositories.image_repository import ImageRepository
from backend.repositories.label_repository import LabelRepository
from backend.services.cloudinary_service import delete_image_from_cloudinary
from starlette.responses import JSONResponse


router = APIRouter(prefix="/api/v1", tags=["Folders"])

@router.post("/create-folder")
async def create_folder(
        data_request: CreateFolderRequestDto,
        http_request: Request,
        db: AsyncSession = Depends(get_session)
):
    user_id = http_request.state.user_id

    try:
        new_folder = await FolderRepository.create_folder(db, data_request.name, user_id)
        return JSONResponse(content={"id": str(new_folder.id), "name": new_folder.name}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot create folder to the database {e}")

@router.get("/folders")
async def get_folders(
        http_request: Request,
        db: AsyncSession = Depends(get_session)
):
    try:
        user_id = http_request.state.user_id

        # Get all folders from the current user
        folders = await FolderRepository.get_folders_by_user_id(db, user_id)
        folders_dto = [map_folder_to_folder_response_dto(folder) for folder in folders]
        return folders_dto
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

@router.get("/folders/{folder_id}")
async def get_folder_by_id(
        folder_id: str,
        http_request: Request,
        db: AsyncSession = Depends(get_session)
):
    try:
        folder = await FolderRepository.get_folder_by_id(db, folder_id)

        # If the folder doesn't have the same user_id as the current request user_id, they are doing something naughty :3
        if http_request.state.user_id != str(folder.user_id): raise Exception("Unauthorized")

        return map_folder_to_folder_response_dto(folder)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

@router.get("/folders/labels")
async def get_folders_by_label_id(
        http_request: Request,
        label_id: str = Query(..., alias="label-id"),
        db: AsyncSession = Depends(get_session)
):
    try:
        # Get folder from current user with specific ID
        user_id = http_request.state.user_id

        folders = await FolderRepository.get_folders_by_label_id(db, user_id, label_id)
        folders_dto = [map_folder_to_folder_response_dto(folder) for folder in folders]
        return folders_dto
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

@router.put("/update-folder")
async def update_folder(
        data_request: FolderUpdateRequestDto,
        http_request: Request,
        db: AsyncSession = Depends(get_session)
):
    try:
        folder = await FolderRepository.get_folder_by_id(db, data_request.id)

        # If the folder doesn't have the same user_id as the current request user_id, they are doing something naughty :3
        if http_request.state.user_id != str(folder.user_id): raise Exception("Unauthorized")

        # Update folder's name
        new_folder = await FolderRepository.update_folder(db, data_request.id, data_request.name)

        if data_request.label_ids:
            label_ids = [uuid.UUID(label_id) for label_id in data_request.label_ids]

            labels = await LabelRepository.get_labels_by_ids(db, label_ids)

            # Add/Remove labels for the folder
            new_folder = await FolderRepository.update_folder_labels(db, str(folder.id), labels)

        return map_folder_to_folder_response_dto(new_folder)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

@router.delete("/delete-folder/{folder_id}")
async def delete_folder(
        folder_id: str,
        http_request: Request,
        db: AsyncSession = Depends(get_session)
):
    try:
        user_id = http_request.state.user_id

        # Get folder with folder_id
        folder = await FolderRepository.get_folder_by_id(db, folder_id)

        # If the deleted folder doesn't have the same user_id as the current request user_id, they are doing something naughty :3
        if user_id != folder.user_id: raise Exception("Unauthorized")

        # Get all images in this folder (We want to remove all of them when the folder is removed)
        images = await ImageRepository.get_images_by_folder_id(db, user_id, str(folder.id))

        for image in images:
            cloudinary_result = await delete_image_from_cloudinary(image.public_id)
            if cloudinary_result["result"] != "ok": raise Exception("Failed to delete image in cloudinary")

            await ImageRepository.delete_image(db, str(image.id))

        await FolderRepository.delete_folder(db, folder_id)
        return JSONResponse(content={"result": "ok"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)