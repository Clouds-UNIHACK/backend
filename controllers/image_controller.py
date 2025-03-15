from functools import reduce
from http.client import HTTPException
from io import BytesIO

import requests
from PIL import Image
from fastapi import APIRouter, Depends, Request, File, UploadFile, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.session import get_session
from backend.dtos.requests.image.save_picture_request_dto import SavePictureRequestDto
from backend.dtos.requests.image.update_image_request_dto import UpdateImageRequestDto
from backend.mappers.images_mapper import map_image_to_image_response_dto
from backend.repositories.image_repository import ImageRepository
from backend.services.cloudinary_service import upload_cloudinary, delete_image_from_cloudinary
from backend.services.kling_ai_service import call_kling_ai_generate_task
from backend.utils.kling_ai_token import encode_kling_ai_jwt_token
from backend.utils.misc import encode_image
from starlette.responses import JSONResponse


router = APIRouter(prefix="/api/v1", tags=["Images"])

@router.post("/generate-image")
async def generate_image(human_image: UploadFile = File(...), cloth_image: UploadFile = File(...)):
    encoded_human_image = encode_image(human_image)
    encoded_cloth_image = encode_image(cloth_image)

    token = f"Bearer {encode_kling_ai_jwt_token()}"

    header = {
        "Content-Type": "application/json",
        "Authorization": token
    }

    data = {
        "human_image": encoded_human_image,
        "cloth_image": encoded_cloth_image
    }

    try:
        image_url = await call_kling_ai_generate_task(header, data)
        return JSONResponse(content={"image_url": image_url}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

@router.post("/save-image")
async def save_image(
        data_request: SavePictureRequestDto,
        http_request: Request,
        db: AsyncSession = Depends(get_session)
):
    try:
        # Download the image from the provided URL
        response = requests.get(data_request.kling_url)
        response.raise_for_status()

        image_data = BytesIO(response.content)

        # Compress image for less bytes
        image = Image.open(image_data)
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format="JPEG", quality=75)
        img_byte_arr.seek(0)

        cloudinary_result = await upload_cloudinary(img_byte_arr)

        print(f"Image uploaded to: {cloudinary_result['secure_url']}")

        # Get user_id from the current user by getting token
        user_id = http_request.state.user_id

        try:
            await ImageRepository.save_image(db, cloudinary_result["secure_url"], cloudinary_result["public_id"], user_id)
            return JSONResponse(content={"secure_url": cloudinary_result["secure_url"], "public_id": cloudinary_result["public_id"]}, status_code=200)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Cannot save image to the database {e}")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Cannot download the image from that url: {data_request.kling_url} - {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

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

        # If the image doesn't have the same user_id as the current request user_id, they are doing something naughty :3
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

@router.put("/update_image")
async def update_image(
        data_request: UpdateImageRequestDto,
        http_request: Request,
        db: AsyncSession = Depends(get_session)
):
    try:
        image = await ImageRepository.get_image_by_id(db, data_request.image_id)

        # If the image doesn't have the same user_id as the current request user_id, they are doing something naughty :3
        if http_request.state.user_id != image.user_id: raise Exception("Unauthorized")

        # Update (move) image to its new folder
        new_image = await ImageRepository.update_image_folder_id(db, data_request.image_id, data_request.folder_id)
        return JSONResponse(content=map_image_to_image_response_dto(new_image), status_code=200)
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