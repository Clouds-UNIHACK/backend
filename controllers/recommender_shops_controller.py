from fastapi.responses import JSONResponse
from transformers import pipeline, CLIPProcessor, CLIPModel
from PIL import Image
from io import BytesIO
from fastapi import HTTPException, APIRouter, UploadFile, File

from backend.config import SERPER_API_KEY
from backend.services.image_recommendation_service import generate_caption, get_shop_recommendations, Product, search_google_shopping

BLIP_pipe = pipeline("image-to-text", model="rcfg/FashionBLIP-1", use_fast=True)
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

router = APIRouter(prefix="/api/v1", tags=["Shops Recommender"])

@router.post("/ai-recommend-shops")
async def ai_recommend_shops(image: UploadFile = File(...)):
    try:
        # Read the image from the uploaded file
        image_bytes = await image.read()

        # Print some debug info on the server side
        print(f"Received image: {image.filename}, size: {len(image_bytes)} bytes, content_type: {image.content_type}")
        # Convert bytes to PIL Image
        try:
            pil_image = Image.open(BytesIO(image_bytes))
            print(f"Successfully opened image with size: {pil_image.size}, mode: {pil_image.mode}")
        except Exception as e:
            print(f"Error opening image: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

        # Generate the caption for the image
        generated_caption = generate_caption(pil_image, BLIP_pipe)

        # Get the recommended images from Google Shopping API
        recommended_images: list[Product] = search_google_shopping(generated_caption, SERPER_API_KEY)

        # Get shop recommendations
        shop_recommendations: list[Product] = get_shop_recommendations(pil_image, recommended_images, clip_processor, clip_model)

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