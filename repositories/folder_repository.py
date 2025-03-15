from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.models.folder import Folder


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
    async def get_folder_by_id(db: AsyncSession, folder_id: str) -> Folder:
        result = await db.execute(select(Folder).where(Folder.id == folder_id))
        folder = result.scalars().first()
        return folder

    @staticmethod
    async def get_folder_by_name(db: AsyncSession, name: str) -> Folder:
        result = await db.execute(select(Folder).where(Folder.name == name))
        folder = result.scalars().first()
        return folder

    @staticmethod
    async def update_folder(db: AsyncSession, folder_id: str, new_name: str) -> Folder:
        try:
            result = await db.execute(select(Folder).where(Folder.id == folder_id))
            folder = result.scalars().first()

            if folder:
                # Update the folder's name
                folder.name = new_name

                await db.commit()
                await db.refresh(folder)
                return folder
            else:
                raise ValueError("Folder not found")
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def delete_folder(db: AsyncSession, folder_id: str):
        try:
            # Retrieve the folder to delete
            folder = await db.execute(select(Folder).where(Folder.id == folder_id))
            folder = folder.scalars().first()

            if folder:
                # Delete the folder
                await db.delete(folder)
                await db.commit()
            else:
                raise ValueError("Folder not found")
        except Exception as e:
            await db.rollback()
            raise e




