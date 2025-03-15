from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from backend.models.folder_label import FolderLabel
import uuid

from backend.models.user import User


class Label(SQLModel, table=True):
    __tablename__ = "label"

    label_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)
    color: Optional[str] = Field(nullable=True)
    user_id: Optional[uuid.UUID] = Field(foreign_key="user.user_id")

    folders: List["Folder"] = Relationship(
        back_populates="label",
        link_model=FolderLabel
    )
    user: User = Relationship(back_populates="user")
