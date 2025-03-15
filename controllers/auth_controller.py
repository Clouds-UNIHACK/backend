from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import Session, select
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import User  # Assuming you have a SQLAlchemy User model
from database import get_db  # Assuming you have a dependency to get DB session
from typing import Any
from models.user import User
from utils.jwt import create_access_token
from utils.misc import is_valid_email

router = APIRouter()
from utils.misc import is_valid_email

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class RegisterRequest(User):
    name: str
    email: str
    password: str


class LoginRequest(User):
    username: str
    password: str


@router.post("/register")
async def auth_register(request: RegisterRequest, db: Session = Depends(get_db)):
    username = request.username.strip()
    email = request.email.strip()
    password = request.password

    # Validation checks
    if not username:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing username field",
        )
    if not email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing email field",
        )
    if not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing password field",
        )

    if not is_valid_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email provided"
        )

    # Check if the user already exists
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email already in use",
        )

    existing_username = db.query(User).filter(User.username == username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username already in use",
        )

    # Hash the password
    hashed_password = pwd_context.hash(password)

    # Create the user
    user = User(username=username, email=email, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate JWT token
    token = create_access_token(payload={"id": user.id})

    return {
        "success": True,
        "data": {"token": token, "user": {"id": user.id, "name": user.name}},
    }


@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    email = request.email.strip()
    password = request.password

    if not email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing email field",
        )
    if not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing password field",
        )

    # Check if the user exists
    user = db.exec(select(User).where(User.username == request.username)).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # Create and return the access token
    token = create_access_token(payload={"id": user.id})
    return {"access_token": token, "token_type": "bearer"}
