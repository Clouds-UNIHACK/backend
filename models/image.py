from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
import uuid

from backend.models.folder import Folder
from backend.models.user import User


class Image(SQLModel, table=True):
    __tablename__ = "image"

    image_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    public_id: str = Field(nullable=True)
    url: str = Field(nullable=False)
    folder_id: Optional[uuid.UUID] = Field(default=None, foreign_key="folder.folder_id", nullable=True)
    user_id: Optional[uuid.UUID] = Field(foreign_key="user.user_id")

    folder: Optional[Folder] = Relationship(back_populates="image")
    user: User = Relationship(back_populates="user")
