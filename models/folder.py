from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from backend.models.folder_label import FolderLabel
import uuid

from backend.models.user import User


class Folder(SQLModel, table=True):
    __tablename__ = "folder"

    folder_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)
    user_id: Optional[uuid.UUID] = Field(foreign_key="user.user_id")

    user: User = Relationship(back_populates="user")
    images: List["Image"] = Relationship(back_populates="folder")
    labels: List["Label"] = Relationship(
        back_populates="folder",
        link_model=FolderLabel
    )
