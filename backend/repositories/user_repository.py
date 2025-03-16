from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.user import User
from sqlmodel import select

class UserRepository:
    @staticmethod
    async def create_user(db: AsyncSession, username: str, email: str, hashed_password: str) -> User:
        try:
            # Create the user
            user = User(username=username, email=email, password=hashed_password)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> User:
        # Check if the user exists
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        return user

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User:
        # Check if the user exists
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        return user
