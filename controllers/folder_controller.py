from functools import reduce
from http.client import HTTPException
from io import BytesIO

import requests
from PIL import Image
from fastapi import APIRouter, Depends, Request, File, UploadFile, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.session import get_session
from backend.dtos.requests.image.save_picture_request_dto import SavePictureRequestDto
from backend.mappers.images_mapper import map_image_to_image_response_dto
from backend.repositories.image_repository import ImageRepository
from backend.services.cloudinary_service import upload_cloudinary, delete_image_from_cloudinary
from backend.services.kling_ai_service import call_kling_ai_generate_task
from backend.utils.kling_ai_token import encode_kling_ai_jwt_token
from backend.utils.misc import encode_image
from starlette.responses import JSONResponse


router = APIRouter(prefix="/api/v1", tags=["Images"])

@router.get("/saved-images")
async def get_images(
        http_request: Request,
        db: AsyncSession = Depends(get_session)
):
    try:
        # Get all images from the current user
        user_id = http_request.state.user_id

        images = await ImageRepository.get_images_by_user_id(db, user_id)
        images_dto = reduce(lambda lists, image: lists.append(map_image_to_image_response_dto(image)), images, [])
        return JSONResponse(content=images_dto, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

@router.get("/saved-images/{image_id}")
async def get_image_by_id(
        image_id: str,
        http_request: Request,
        db: AsyncSession = Depends(get_session)
):
    try:
        image = await ImageRepository.get_image_by_id(db, image_id)

        # If the deleted image doesn't have the same user_id as the current request user_id, they are doing something naughty :3
        if http_request.state.user_id != image.user_id: raise Exception("Unauthorized")

        return JSONResponse(content=map_image_to_image_response_dto(image), status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

@router.get("/saved-images")
async def get_images_by_folder_id(
        http_request: Request,
        folder_id: str = Query(..., alias="folder-id"),
        db: AsyncSession = Depends(get_session)
):
    try:
        # Get image from current user with specific ID
        user_id = http_request.state.user_id
        images = await ImageRepository.get_images_by_folder_id(db, user_id, folder_id)
        images_dto = reduce(lambda lists, image: lists.append(map_image_to_image_response_dto(image)), images, [])
        return JSONResponse(content=images_dto, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

@router.delete("/delete-image/{image_id}")
async def delete_image(
        image_id: str,
        http_request: Request,
        db: AsyncSession = Depends(get_session)
):
    try:
        # Get image with this specific ID to get Cloudinary public_id
        image = await ImageRepository.get_image_by_id(db, image_id)

        # If the deleted image doesn't have the same user_id as the current request user_id, they are doing something naughty :3
        if http_request.state.user_id != image.user_id: raise Exception("Unauthorized")

        cloudinary_result = await delete_image_from_cloudinary(image.public_id)
        if cloudinary_result["result"] != "ok": raise Exception("Failed to delete image in cloudinary")

        await ImageRepository.delete_image(db, str(image.id))
        return JSONResponse(content={"result": "ok"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)