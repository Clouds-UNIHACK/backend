# Load environment variables from .env file
import os

from dotenv import load_dotenv

dotenv_path = "backend/.env"
# Load environment variables from the .env file
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print("Could not find .env file")

# PostgreSQL Database Configs (For Local Development Only)
POSTGRES_USER = os.getenv("POSTGRES_USER", "your_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "your_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "your_database")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# Load Kling AI API Key
KLING_AI_ACCESS_KEY = os.getenv("KLING_AK")
KLING_AI_SECRET_KEY = os.getenv("KLING_SK")

# Load Cloudinary API Key
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# Load Server JWT Secret Key
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")

# Load Serper API Key
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Load Open API Key
OPEN_API_KEY = os.getenv("OPEN_AI_KEY")

# Load Front End Server
FRONTEND_HOST = os.getenv("FRONTEND_HOST")
FRONTEND_PORT = os.getenv("FRONTEND_PORT")
