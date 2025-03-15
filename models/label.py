import uuid

from sqlalchemy import Column, String

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Label(Base):
    __tablename__ = "label"

    label_id = Column(String, primary_key=True, defualt=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    color = Column(String, nullable=True)

    folders = relationship("Folder", secondary="folder_label", back_populates="label")