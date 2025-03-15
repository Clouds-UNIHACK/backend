import uuid

from sqlalchemy import Column, String, ForeignKey

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Image(Base):
    __tablename__ = "image"

    image_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    public_id = Column(String, nullable=True)
    url = Column(String, nullable=False)
    folder_id = Column(String, ForeignKey('folder.folder_id'), nullable=True)

    folder = relationship("Folder", back_populates="image")
