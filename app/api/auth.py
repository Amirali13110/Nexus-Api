from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_db
from app.core.security import (
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_password,
)
from app.models.auth import User
from app.schemas.auth import UserCreate, TokenResponse, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def sign_up(credentials: UserCreate, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(User).where(
            (User.email == credentials.email) | (User.username == credentials.username)
        )
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        field = "Email" if existing_user.email == credentials.email else "Username"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field} already registered",
        )

    hashed_password = get_password_hash(credentials.password)
    new_user = User(
        username=credentials.username,
        email=credentials.email,
        hashed_password=hashed_password,
    )

    db.add(new_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered",
        )
    await db.refresh(new_user)

    access_token = create_access_token(data={"sub": str(new_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": new_user,
    }


@router.post("/signin", response_model=TokenResponse)
async def sign_in(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token_data = {"sub": str(user.id)}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )
