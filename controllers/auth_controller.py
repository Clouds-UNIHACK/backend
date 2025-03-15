from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import Session, select
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from backend.database.session import (
    get_session,
)  # Assuming you have a dependency to get DB session
from backend.dtos.requests.login_request_dto import LoginRequestDto
from backend.dtos.requests.register_request_dto import RegisterRequestDto
from backend.models.user import User
from backend.utils.jwt_token import create_access_token
from backend.utils.misc import is_valid_email

router = APIRouter(prefix="/api/v1", tags=["Authentication"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/register")
async def auth_register(request: RegisterRequestDto, db: Session = Depends(get_session)):
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
async def login(request: LoginRequestDto, db: Session = Depends(get_session)):
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
