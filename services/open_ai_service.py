from openai import OpenAI

client = OpenAI()
from backend.config import OPEN_API_KEY


async def analyse_images_stylist_open_ai(img_urls, prompt):
    content = [{"type": "text", "text": prompt}]
    for img_url in img_urls:
        content.append({"type": "image_url", "image_url": {"url": img_url}})

    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": content}]
    )

    print(response.choices[0])
    return {"response": response.choices[0]}
