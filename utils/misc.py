import re
import base64
from io import BytesIO
from PIL import Image
from fastapi import UploadFile


def is_valid_email(email: str) -> bool:
    """
    Check if the email is valid.
    """
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

# Convert image to Base64 string
def encode_image(image: UploadFile):
    image_bytes = image.file.read()
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    return encoded_image

def decode_image(image_data: str) -> Image.Image:
    """Decode a base64 string into a PIL Image."""
    try:
        image_bytes = BytesIO(base64.b64decode(image_data))
        return Image.open(image_bytes)
    except Exception as e:
        raise Exception(f"Invalid image data: {e}")
