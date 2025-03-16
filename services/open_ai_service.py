import openai

from backend.config import OPEN_API_KEY

openai.api_key = OPEN_API_KEY

async def analyse_images_stylist_open_ai(img_urls, prompt):
    response = await openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": "You are a stylist helping users to choose the best clothes in provided images for an occasion."},
            {"role": "user", "content": prompt, "images": img_urls}
        ]
    )

    return {"response": response["choices"][0]["message"]["content"]}
