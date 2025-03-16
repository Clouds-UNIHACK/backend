from fastapi import HTTPException
import requests
from transformers import pipeline, CLIPProcessor, CLIPModel
from PIL import Image
from io import BytesIO
import torch
import torch.nn.functional as F

class Product:
    def __init__(self, title: str, image_url: str, shop_name: str, price: float):
        self.title = title
        self.image : Image.Image = Image.open(BytesIO(requests.get(image_url).content))
        self.shop = shop_name
        self.price = price
        self.image_url = image_url
        self.link = f"https://www.google.com/search?q={title.replace(' ', '+')}+Shop%3A+{shop_name}"
        self.similarity_score = 0
    def __str__(self):
        return f"Title: {self.title}\nShop: {self.shop}\nLink: {self.link}\nSimilarity Score: {self.similarity_score}"
    def to_dict(self):
        return {
            "title": self.title,
            "image_url": self.image_url,
            "shop": self.shop,
            "price": self.price,
            "link": self.link
        }

def search_google_shopping(query: str, serper_api_key: str) -> list[Product]:
    # Set up the parameters for SerpApi's Google Shopping endpoint
    params = {
        "engine": "google",
        "q": query,
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us",
        "tbm": "shop",  # indicates shopping results
        "api_key": serper_api_key
    }

    response = requests.get("https://serpapi.com/search", params=params)
    response.raise_for_status()  # raises an error if the request failed
    results = response.json()
    shopping_results = results.get("shopping_results", [])
    products = []
    for product in shopping_results:
        title = product.get("title")
        image_url = product.get("thumbnail")
        shop_name = product.get("source")
        price = product.get("price")
        product_obj = Product(title, image_url, shop_name, price)
        products.append(product_obj)
    return products

def get_clip_embedding(image: Image.Image, clip_processor: CLIPProcessor, clip_model: CLIPModel):
    inputs = clip_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        image_features = clip_model.get_image_features(**inputs)
    # Normalize the embedding
    return image_features / image_features.norm(dim=-1, keepdim=True)

def get_similarity_score(img1_embedding, img2_embedding):
    similarity_score_cos = F.cosine_similarity(img1_embedding, img2_embedding)
    return similarity_score_cos.item()

def get_shop_recommendations(image: Image.Image, recommended_images: list[Product], clip_processor: CLIPProcessor, clip_model: CLIPModel) -> \
list[Product]:
    img1_embedding = get_clip_embedding(image, clip_processor, clip_model)

    for recommended_image in recommended_images:
        img2_embedding = get_clip_embedding(recommended_image.image, clip_processor, clip_model)
        similarity_score = get_similarity_score(img1_embedding, img2_embedding)
        recommended_image.similarity_score = similarity_score
    recommended_images.sort(reverse=True, key=lambda x: x.similarity_score)
    top_6_recommendations = recommended_images if len(recommended_images) < 6 else recommended_images[:6]
    return top_6_recommendations

def generate_caption(image: Image.Image, pipe: pipeline) -> str:
    """Generate a caption for the given image using the FashionBLIP-1 model."""
    try:
        caption = pipe(image)
        generated_text = caption[0]['generated_text']
        return generated_text
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating caption") from e