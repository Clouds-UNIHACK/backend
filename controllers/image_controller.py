import asyncio

import requests
from fastapi import APIRouter, File, UploadFile, HTTPException
from starlette.responses import JSONResponse

from backend.utils.const import kling_ai_api_domain
from backend.utils.kling_ai_token import encode_kling_ai_jwt_token
from backend.utils.misc import encode_image

router = APIRouter(prefix="/api/v1", tags=["Image"])

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

    response = requests.post(f"{kling_ai_api_domain}/v1/images/kolors-virtual-try-on", json=data, headers=header)

    if response.status_code == 200:
        task_id = response.json().get("data", {}).get("task_id")
        if not task_id:
            raise HTTPException(status_code=400, detail="Task ID not found in the response")

        # Asynchronously poll for the generation task from kling ai
        async def poll_kling_ai():
            nonlocal header, task_id
            task_url = f"{kling_ai_api_domain}/v1/images/kolors-virtual-try-on/{task_id}"

            while True:
                task_response = requests.get(task_url, headers=header)
                if task_response.status_code == 200:
                    task_data = task_response.json()
                    task_status = task_data.get("data", {}).get("task_status")

                    match task_status:
                        case "succeed":
                            images = task_data.get("data", {}).get("task_result", {}).get("images", [])
                            if images:
                                return images[0].get("url")

                            raise HTTPException(status_code=400, detail="No image found in task_result")
                        case "failed":
                            error_msg = task_data.get("data", {}).get("task_status_msg", "Unknown error")
                            raise HTTPException(status_code=400, detail=f"Image generation failed: {error_msg}")
                        case _:
                            # Polling every 5 seconds

                            await asyncio.sleep(5)
                else:
                    task_response_data = response.json()
                    task_error_code = task_response_data.get("code")
                    task_message = task_response_data.get("message")
                    raise HTTPException(status_code=400, detail=f"Fail to fetch task id from Kling AI. Returns with: "
                                                                f"error_code: {task_error_code}, message: {task_message}, token: {token}")
        image_url = await poll_kling_ai()

        return JSONResponse(content={"image_url": image_url}, status_code=200)
    else:
        response_data = response.json()
        error_code = response_data.get("code")
        message = response_data.get("message")
        raise HTTPException(status_code=400, detail=f"Failed to start image generation. Kling AI returns with: "
                                                    f"error_code: {error_code}, message: {message}, token: {token}")



