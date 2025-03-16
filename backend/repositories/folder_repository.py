from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.models.folder import Folder
from backend.models.folder_label import FolderLabel
from backend.models.label import Label


class FolderRepository:
    @staticmethod
    async def create_folder(db: AsyncSession, name: str, user_id: str) -> Folder:
        try:
            # Create the folder
            folder = Folder(name=name, user_id=user_id)
            db.add(folder)
            await db.commit()
            await db.refresh(folder)
            return folder
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def get_folders_by_user_id(db: AsyncSession, user_id: str):
        # Get all folders from user_id
        result = await db.execute(select(Folder).where(Folder.user_id == user_id))
        folders = result.scalars().all()
        return folders

    @staticmethod
    async def get_folders_by_label_id(db: AsyncSession, user_id: str, label_id: str):
        # Filter folders by label
        result = await db.execute(
            select(Folder)
            .join(FolderLabel, Folder.id == FolderLabel.folder_id)
            .where(Folder.user_id == user_id, FolderLabel.label_id == label_id))
        return result.scalars().all()

    @staticmethod
    async def get_folder_by_id(db: AsyncSession, folder_id: str) -> Folder:
        result = await db.execute(select(Folder).where(Folder.id == folder_id))
        folder = result.scalars().first()
        return folder

    @staticmethod
    async def get_folder_by_name(db: AsyncSession, name: str, user_id: str) -> Folder:
        result = await db.execute(select(Folder).where(Folder.name == name, Folder.user_id == user_id))
        folder = result.scalars().first()
        return folder

    @staticmethod
    async def update_folder(db: AsyncSession, folder_id: str, new_name: str) -> Folder:
        try:
            # Retrieve the folder to update
            folder = await FolderRepository.get_folder_by_id(db, folder_id)

            if folder:
                # Update the folder's name
                folder.name = new_name

                await db.commit()
                await db.refresh(folder)
                return folder
            else:
                raise Exception("Folder not found")
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def update_folder_labels(db: AsyncSession, folder_id: str, labels: List[Label]):
        try:
            # Retrieve the folder to update
            folder = await FolderRepository.get_folder_by_id(db, folder_id)
            print(folder.labels)

            if folder:
                folder.labels = labels

                db.add(folder)
                await db.commit()
                await db.refresh(folder)
            else:
                raise Exception("Folder not found")
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def delete_folder(db: AsyncSession, folder_id: str):
        try:
            # Retrieve the folder to delete
            folder = await FolderRepository.get_folder_by_id(db, folder_id)

            if folder:
                # Delete the folder
                await db.delete(folder)
                await db.commit()
            else:
                raise ValueError("Folder not found")
        except Exception as e:
            await db.rollback()
            raise e




