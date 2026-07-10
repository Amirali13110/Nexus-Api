import app.models
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, func
from ulid import ULID
from app.core.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(
        String(26),
        primary_key=True,
        default=lambda: str(ULID()),
    )
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    profile = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    workspace_members = relationship(
        "WorkspaceMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    sent_workspace_invitations = relationship(
        "WorkspaceInvitation",
        back_populates="invited_by",
    )


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(
        String(26),
        primary_key=True,
        default=lambda: str(ULID()),
    )
    user_id = Column(
        String(26),
        ForeignKey("users.id", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash = Column(String, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EmailChangeToken(Base):
    __tablename__ = "email_change_tokens"

    id = Column(
        String(26),
        primary_key=True,
        default=lambda: str(ULID()),
    )
    user_id = Column(
        String(26),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    new_email = Column(String, nullable=False)
    token_hash = Column(String, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
