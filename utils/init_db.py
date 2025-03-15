from sqlmodel import SQLModel
from backend.database.database import engine
from backend.models.user import User
from backend.models.folder import Folder
from backend.models.image import Image
from backend.models.label import Label
from backend.models.folder_label import FolderLabel

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

if __name__ == "__main__":
    init_db()
