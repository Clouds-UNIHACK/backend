from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from backend.database.session import get_session  # Async session dependency
from backend.dtos.requests.auth.login_request_dto import LoginRequestDto
from backend.dtos.requests.auth.register_request_dto import RegisterRequestDto
from backend.models.user import User
from backend.repositories.user_repository import UserRepository
from backend.utils.jwt_token import create_access_token
from backend.utils.misc import is_valid_email

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/register")
async def auth_register(request: RegisterRequestDto, db: AsyncSession = Depends(get_session)):
    username = request.username.strip()
    email = request.email.strip()
    password = request.password

    # Validation checks
    if not username:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Missing username field")
    if not email:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Missing email field")
    if not password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Missing password field")
    if not is_valid_email(email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email provided")

    # Check if the user already exists
    existing_username = await UserRepository.get_user_by_username(db, username)
    if existing_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already in use")

    existing_email = await UserRepository.get_user_by_email(db, email)
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")

    # Hash the password
    hashed_password = pwd_context.hash(password)

    user: User
    try:
        user = await UserRepository.create_user(db, username, email, hashed_password)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Unable to create user account: {e}")

    # Generate JWT token
    token = create_access_token(payload={"id": str(user.id)})

    return {"success": True, "data": {"token": token, "user": {"id": str(user.id), "name": user.username}}}


@router.post("/login")
async def login(request: LoginRequestDto, db: AsyncSession = Depends(get_session)):
    username = request.username
    password = request.password

    if not username:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Missing username field")
    if not password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Missing password field")

    user: User
    try:
        user = await UserRepository.get_user_by_username(db, username)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You've enter the wrong username or password")

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You've enter the wrong username or password")

    # Create and return the access token
    token = create_access_token(payload={"id": str(user.id)})
    return {"access_token": token, "token_type": "Bearer"}
