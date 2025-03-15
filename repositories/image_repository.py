from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.image import Image

class ImageRepository:
    @staticmethod
    async def save_image(db: AsyncSession, public_url: str, public_id: str, user_id: str):
        try:
            new_image = Image(public_url=public_url, public_id=public_id, user_id=user_id)
            db.add(new_image)
            await db.commit()
            await db.refresh(new_image)
        except Exception as e:
            await db.rollback()
            raise e

