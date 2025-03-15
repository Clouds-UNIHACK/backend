import base64
import os

from fastapi.responses import JSONResponse
from transformers import pipeline, CLIPProcessor, CLIPModel
from PIL import Image
from io import BytesIO
from fastapi import HTTPException, Request, APIRouter

from backend.config import SERPER_API_KEY
from backend.services.image_recommendation_service import generate_caption, get_shop_recommendations, Product, search_google_shopping
from backend.utils.misc import decode_image
import torch.nn.functional as F

BLIP_pipe = pipeline("image-to-text", model="rcfg/FashionBLIP-1", use_fast=True)
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

router = APIRouter(prefix="/api/v1", tags=["Shops Recommender"])

@router.post("/ai-recommend-shops")
async def ai_recommend_shops(request: Request):
    print("ai_recommend_shops")
    try:
        # Read the image from the request
        request_data = await request.json()
        image_data = request_data.get("image")  # Expecting base64 string
        if not image_data:
            raise HTTPException(status_code=400, detail="Image data is required")

        # Decode the image
        image = decode_image(image_data)

        # Generate the caption for the image
        generated_caption = generate_caption(image, BLIP_pipe)
        print(f"Generated Caption: {generated_caption}")

        # Get the recommended images from Google Shopping API
        recommended_images: list[Product] = search_google_shopping(generated_caption, SERPER_API_KEY)

        # Get shop recommendations
        shop_recommendations: list[Product] = get_shop_recommendations(image, recommended_images, clip_processor, clip_model)

        # Convert shop_recommendations to a JSON-serializable format
        serialized_recommendations = [shop_recommendation.to_dict() for shop_recommendation in shop_recommendations]

        return JSONResponse(
            status_code=200,
            content={"shop_recommendations": serialized_recommendations}
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e