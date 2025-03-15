import cloudinary
import cloudinary.uploader
from backend.config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

cloudinary.config(
    cloud_name = CLOUDINARY_CLOUD_NAME,
    api_key = CLOUDINARY_API_KEY,
    api_secret = CLOUDINARY_API_SECRET
)

async def call_cloudinary_service(img_bytes):
    try:
        upload_result = cloudinary.uploader.upload(
            img_bytes,
            folder="Clouds-Unihack"
        )
        return upload_result
    except cloudinary.exceptions.Error as e:
        raise Exception(f"Error uploading to cloudinary: {e}")

