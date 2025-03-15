import base64
import os
from backend.config import *
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.controllers import image_controller, kling_ai_controller, auth_controller
from backend.middlewares.auth_middleware import AuthMiddleware
from transformers import pipeline, CLIPProcessor, CLIPModel
from PIL import Image
from io import BytesIO
from backend.image_utils import decode_image, generate_caption, get_shop_recommendations, Product, search_google_shopping
import torch.nn.functional as F

serper_api_key = os.getenv("SERPER_API_KEY")  # Replace with your actual SerpApi key

app = FastAPI(title="Clouds-Unihack API")

BLIP_pipe = pipeline("image-to-text", model="rcfg/FashionBLIP-1", use_fast=True)
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_controller.router)
app.include_router(kling_ai_controller.router)
app.include_router(image_controller.router)
# app.include_router(folder_controller.router)
# app.include_router(label_controller.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Clouds-Unihack API"}

# Provide error response for any server exceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": "An error occurred"}
    )

@app.post("/api/ai-recommend-shops")
async def ai_recommend_shops(request: Request):
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

        # Get the recommended images from Google Shopping API
        recommended_images: list[Product] = search_google_shopping(generated_caption, serper_api_key)
        
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
    

