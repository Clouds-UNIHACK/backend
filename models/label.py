from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from backend.models.folder_label import FolderLabel
import uuid

class Label(SQLModel, table=True):
    __tablename__ = "label"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)
    color: Optional[str] = Field(nullable=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=True)

    folders: List["Folder"] = Relationship(
        back_populates="labels",
        link_model=FolderLabel
    )
    user: "User" = Relationship(back_populates="labels")
