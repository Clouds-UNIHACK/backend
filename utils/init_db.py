from sqlmodel import SQLModel
from backend.database.database import engine
from backend.models.user import User
from backend.models.folder import Folder
from backend.models.image import Image
from backend.models.label import Label
from backend.models.folder_label import FolderLabel

def init_db():
    SQLModel.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
