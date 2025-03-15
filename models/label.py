from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import uuid

from models.folder import Folder

class Label(SQLModel, table=True):
    __tablename__ = "label"

    label_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)
    color: Optional[str] = Field(nullable=True)

    folders: List[Folder] = Relationship(
        back_populates="label",
        link_model="FolderLabel"
    )