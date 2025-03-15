import uuid

from sqlalchemy import Column, String

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Folder(Base):
    __tablename__ = "folder"

    folder_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)

    images = relationship("Image", back_populates="folder")
    labels = relationship("Label", secondary="folder_label", back_populates="folder")

