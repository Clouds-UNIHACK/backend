import re
import base64
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
