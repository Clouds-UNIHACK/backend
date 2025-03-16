from fastapi import APIRouter, Depends, Request, HTTPException, Query

from backend.dtos.requests.image.recommend_image_request_dto import RecommendImageRequestDto
from backend.services.open_ai_service import analyse_images_stylist_open_ai

router = APIRouter(prefix="/api/v1", tags=["OPEN AI API"])

@router.post("/recommend-stylist")
async def recommend_stylist(
        data_request: RecommendImageRequestDto
):
    return await analyse_images_stylist_open_ai(data_request.image_urls, data_request.prompt)

