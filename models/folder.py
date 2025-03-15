from sqlmodel import SQLModel, Field, Relationship
from typing import List
import uuid

from models.image import Image
from models.label import Label


class Folder(SQLModel, table=True):
    __tablename__ = "folder"

    folder_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)

    images: List[Image] = Relationship(back_populates="folder")
    labels: List[Label] = Relationship(
        back_populates="folder",
        link_model="FolderLabel"
    )