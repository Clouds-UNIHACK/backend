from http.client import HTTPException
from io import BytesIO

import cloudinary
import cloudinary.uploader
import requests

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
from backend.database.session import get_session
from backend.dtos.requests.save_picture_request_dyo import SavePictureRequestDto
from backend.repositories.image_repository import ImageRepository

cloudinary.config(
    cloud_name = CLOUDINARY_CLOUD_NAME,
    api_key = CLOUDINARY_API_KEY,
    api_secret = CLOUDINARY_API_SECRET
)

router = APIRouter(prefix="/api/v1", tags=["Images"])

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

        upload_result = cloudinary.uploader.upload(
            image_data,
            folder="Clouds-Unihack"
        )

        print(f"Image uploaded to: {upload_result['secure_url']}")

        # Get user_id from the current user by getting token
        user_id = http_request.state.user_id

        try:
            await ImageRepository.save_image(db, upload_result["secure_url"], upload_result["public_id"], user_id)
        except Exception as e:
            raise HTTPException(f"Cannot save image to the database {e}")

    except requests.exceptions.RequestException as e:
        raise HTTPException(f"Cannot download the image from that url: {data_request.kling_url}")
    except cloudinary.exceptions.Error as e:
        raise HTTPException(f"Error uploading to cloudinary")