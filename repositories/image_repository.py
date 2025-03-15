from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.models.image import Image

class ImageRepository:
    @staticmethod
    async def save_image(db: AsyncSession, public_url: str, public_id: str, user_id: str):
        try:
            new_image = Image(url=public_url, public_id=public_id, user_id=user_id)
            db.add(new_image)
            await db.commit()
            await db.refresh(new_image)
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def get_images_by_user_id(db: AsyncSession, user_id: str):
        # Get all images
        result = await db.execute(select(Image).where(Image.user_id == user_id))
        images = result.scalars().all()
        return images

    @staticmethod
    async def get_images_by_folder_id(db: AsyncSession, user_id: str, folder_id: str):
        # Filter images by folder_id
        result = await db.execute(
            select(Image)
            .where(Image.user_id == user_id, Image.folder_id == folder_id))
        return result.scalars().all()

    @staticmethod
    async def get_image_by_id(db: AsyncSession, image_id: str) -> Image:
        result = await db.execute(select(Image).where(Image.id == image_id))
        image = result.scalars().first()
        return image

    @staticmethod
    async def delete_image(db: AsyncSession, image_id: str):
        try:
            # Retrieve the image to delete
            folder = ImageRepository.get_image_by_id(db, image_id)

            if folder:
                # Delete the image
                await db.delete(folder)
                await db.commit()
            else:
                raise ValueError("Folder not found")
        except Exception as e:
            await db.rollback()
            raise e
