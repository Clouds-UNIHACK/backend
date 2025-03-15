from typing import List

from sqlmodel import SQLModel, Field, Relationship
import uuid

from backend.models.label import Label


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(unique=True, nullable=False)
    email: str = Field(nullable=False)
    password: str = Field(nullable=False)

    labels: List[Label] = Relationship(back_populates="user")
    folders: List["Folder"] = Relationship(back_populates="user")
    images: List["Image"] = Relationship(back_populates="user")
