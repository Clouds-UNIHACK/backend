from sqlmodel import SQLModel, Field
import uuid

class FolderLabel(SQLModel, table=True):
    __tablename__ = 'folder_label'

    folder_label_id: int = Field(default=None, primary_key=True)
    folder_id: uuid.UUID = Field(foreign_key="folder.folder_id")
    label_id: uuid.UUID = Field(foreign_key="label.label_id")