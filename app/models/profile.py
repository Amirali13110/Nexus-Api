import app.models
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from ulid import ULID

from app.core.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(
        String(26),
        primary_key=True,
        default=lambda: str(ULID()),
    )

    user_id = Column(
        String(26),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    username = Column(String(30), unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)

    user = relationship(
        "User",
        back_populates="profile",
    )
