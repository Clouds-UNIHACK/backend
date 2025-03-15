import asyncio
from backend.utils.const import kling_ai_api_domain
import requests

async def call_kling_ai_generate_task(header, data):
    response = requests.post(f"{kling_ai_api_domain}/v1/images/kolors-virtual-try-on", json=data, headers=header)

    if response.status_code == 200:
        task_id = response.json().get("data", {}).get("task_id")
        if not task_id:
            raise Exception("Task ID not found in the response")

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

                            raise Exception("No image found in task_result")
                        case "failed":
                            error_msg = task_data.get("data", {}).get("task_status_msg", "Unknown error")
                            raise Exception(f"Image generation failed: {error_msg}")
                        case _:
                            # Polling every 5 seconds

                            await asyncio.sleep(5)
                else:
                    task_response_data = response.json()
                    task_error_code = task_response_data.get("code")
                    task_message = task_response_data.get("message")
                    raise Exception(f"Fail to fetch task id from Kling AI. Returns with: "
                                    f"error_code: {task_error_code}, message: {task_message}")

        return await poll_kling_ai()

    else:
        response_data = response.json()
        error_code = response_data.get("code")
        message = response_data.get("message")
        raise Exception(f"Failed to start image generation. Kling AI returns with: error_code: {error_code}, message: {message}")