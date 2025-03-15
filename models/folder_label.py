from sqlalchemy import Column, String, Integer, ForeignKey

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class FolderLabel(Base):
    __tablename__ = "folder_label"

    folder_label_id = Column(Integer, primary_key=True)
    folder_id = Column(String, ForeignKey('folder.folder_id'), nullable=False)
    label_id = Column(String, ForeignKey('label.label_id'), nullable=False)

    folder = relationship("Folder", back_populates="label")
    label = relationship("Label", back_populates="folder")