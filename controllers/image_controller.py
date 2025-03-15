from http.client import HTTPException
from io import BytesIO

import requests
from PIL import Image
from fastapi import APIRouter, Depends, Request, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.session import get_session
from backend.dtos.requests.image.save_picture_request_dto import SavePictureRequestDto
from backend.repositories.image_repository import ImageRepository
from backend.services.cloudinary_service import call_cloudinary_service
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

        cloudinary_result = await call_cloudinary_service(img_byte_arr)

        print(f"Image uploaded to: {cloudinary_result['secure_url']}")

        # Get user_id from the current user by getting token
        user_id = http_request.state.user_id

        try:
            await ImageRepository.save_image(db, cloudinary_result["secure_url"], cloudinary_result["public_id"], user_id)
            return JSONResponse(content={"secure_url": cloudinary_result["secure_url"], "public_id": cloudinary_result["public_id"]}, status_code=200)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Cannot save image to the database {e}")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Cannot download the image from that url: {data_request.kling_url}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)
