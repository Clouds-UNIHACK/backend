from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
import uuid

from backend.models.folder import Folder
from backend.models.user import User


class Image(SQLModel, table=True):
    __tablename__ = "image"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    public_id: str = Field(nullable=True)
    url: str = Field(nullable=False)
    folder_id: Optional[uuid.UUID] = Field(default=None, foreign_key="folder.id", nullable=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)

    folder: Optional[Folder] = Relationship(back_populates="images")
    user: User = Relationship(back_populates="images")
