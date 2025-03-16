import uuid
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.models.folder_label import FolderLabel
from backend.models.label import Label


class LabelRepository:
    @staticmethod
    async def create_label(db: AsyncSession, name: str, color: Optional[str], user_id: str) -> Label:
        try:
            # Create the folder
            label = Label(name=name, color=color, user_id=user_id)
            if not color:
                label.color = "FF0000"

            db.add(label)
            await db.commit()
            await db.refresh(label)
            return label
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def get_labels_by_user_id(db: AsyncSession, user_id: str):
        # Get all labels
        result = await db.execute(select(Label).where(Label.user_id == user_id))
        labels = result.scalars().all()
        return labels

    @staticmethod
    async def get_label_by_id(db: AsyncSession, label_id: str) -> Label:
        result = await db.execute(select(Label).where(Label.id == label_id))
        label = result.scalars().first()
        return label

    @staticmethod
    async def get_labels_by_ids(db: AsyncSession, label_ids: List[uuid.UUID]) -> List[Label]:
        result = await db.execute(select(Label).where(Label.id.in_(label_ids)))
        return result.scalars().all()

    @staticmethod
    async def get_labels_by_folder_id(db: AsyncSession, user_id: str, folder_id: str):
        # Filter folders by folder
        result = await db.execute(
            select(Label)
            .join(FolderLabel, Label.id == FolderLabel.label_id)
            .where(Label.user_id == user_id, FolderLabel.folder_id == folder_id))
        return result.scalars().all()


    @staticmethod
    async def get_label_by_name(db: AsyncSession, name: str, user_id: str) -> Label:
        result = await db.execute(select(Label).where(Label.name == name, Label.user_id == user_id))
        label = result.scalars().first()
        return label

    @staticmethod
    async def update_label(db: AsyncSession, new_name: str, new_color: str, label_id: str) -> Label:
        try:
            # Retrieve the folder to update
            label = await LabelRepository.get_label_by_id(db, label_id)

            if label:
                # Update the label's name
                label.name = new_name
                label.color = new_color

                await db.commit()
                await db.refresh(label)
                return label
            else:
                raise ValueError("Label not found")
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def delete_label(db: AsyncSession, label_id: str):
        try:
            # Retrieve the folder to delete
            label = await LabelRepository.get_label_by_id(db, label_id)

            if label:
                # Delete the label
                await db.delete(label)
                await db.commit()
            else:
                raise ValueError("Label not found")
        except Exception as e:
            await db.rollback()
            raise e
