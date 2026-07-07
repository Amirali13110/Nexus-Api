from datetime import datetime, timedelta, timezone
from app.models.profile import Profile
from app.services.email_services import (
    send_reset_password_email,
    send_email_change_confirmation,
)

from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import settings
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_db
from app.core.security import (
    generate_reset_token,
    get_current_user,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    hash_token,
    verify_password,
)
from app.models.auth import PasswordResetToken, User, EmailChangeToken

from app.schemas.auth import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserCreate,
    TokenResponse,
    UpdateEmailRequest,
    ConfirmEmailUpdateRequest,
    UpdatePasswordRequest,
    UserLogin,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])

frontend_url = settings.FRONTEND_URL


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def sign_up(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == payload.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    result = await db.execute(
        select(Profile).where(Profile.username == payload.username)
    )
    existing_profile = result.scalar_one_or_none()

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    hashed_password = get_password_hash(payload.password)

    new_user = User(
        email=payload.email,
        hashed_password=hashed_password,
    )

    db.add(new_user)

    try:
        await db.flush()

        new_profile = Profile(
            user_id=new_user.id,
            username=payload.username,
            full_name=payload.full_name,
        )

        db.add(new_profile)

        await db.commit()

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create account.",
        )

    await db.refresh(new_user)
    await db.refresh(new_profile)

    access_token = create_access_token(data={"sub": str(new_user.id)})

    refresh_token = create_refresh_token(data={"sub": str(new_user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": new_user,
    }


@router.post("/signin", response_model=TokenResponse)
async def sign_in(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
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


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if user:
        await db.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used == False,
            )
            .values(used=True)
        )
        raw_token = generate_reset_token()
        token_hash = hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        db.add(reset_token)
        await db.commit()

        reset_link = f"{frontend_url}/updatePassword?token={raw_token}"
        background_tasks.add_task(send_reset_password_email, user.email, reset_link)

    return {"message": "If that email is registered, a reset link has been sent."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    token_hash = hash_token(payload.token)

    result = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    )
    reset_token = result.scalar_one_or_none()

    if (
        not reset_token
        or reset_token.used
        or reset_token.expires_at < datetime.now(timezone.utc)
    ):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    result = await db.execute(select(User).where(User.id == reset_token.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user.hashed_password = get_password_hash(payload.new_password)
    reset_token.used = True

    await db.execute(
        delete(PasswordResetToken).where(PasswordResetToken.user_id == user.id)
    )

    await db.commit()

    return {"message": "Password has been reset successfully."}


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    email = form_data.username

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


#


@router.patch("/update-password", status_code=status.HTTP_200_OK)
async def update_password(
    payload: UpdatePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    if payload.current_password == payload.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password",
        )

    current_user.hashed_password = get_password_hash(payload.new_password)
    await db.commit()

    return {"message": "Password updated successfully"}


@router.patch("/update-email", status_code=status.HTTP_200_OK)
async def update_email(
    payload: UpdateEmailRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(payload.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect",
        )

    if payload.new_email == current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New email must be different from your current email",
        )

    result = await db.execute(select(User).where(User.email == payload.new_email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    await db.execute(
        update(EmailChangeToken)
        .where(
            EmailChangeToken.user_id == current_user.id, EmailChangeToken.used == False
        )
        .values(used=True)
    )

    raw_token = generate_reset_token()
    token_hash = hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

    email_token = EmailChangeToken(
        user_id=current_user.id,
        new_email=payload.new_email,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(email_token)
    await db.commit()

    confirm_link = f"{frontend_url}/updateEmail?token={raw_token}"
    background_tasks.add_task(
        send_email_change_confirmation, payload.new_email, confirm_link
    )

    return {"message": "Verification link sent to your new email address"}


@router.post("/confirm-email-update", status_code=status.HTTP_200_OK)
async def confirm_email_update(
    payload: ConfirmEmailUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    token_hash = hash_token(payload.token)

    result = await db.execute(
        select(EmailChangeToken).where(EmailChangeToken.token_hash == token_hash)
    )
    email_token = result.scalar_one_or_none()

    if (
        not email_token
        or email_token.used
        or email_token.expires_at < datetime.now(timezone.utc)
    ):
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification link"
        )

    result = await db.execute(select(User).where(User.email == email_token.new_email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    result = await db.execute(select(User).where(User.id == email_token.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification link"
        )

    user.email = email_token.new_email
    email_token.used = True
    await db.commit()

    return {"message": "Email updated successfully"}
