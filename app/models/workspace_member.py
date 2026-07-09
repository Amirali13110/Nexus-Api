import app.models

from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from ulid import ULID

from app.core.database import Base


class WorkspaceRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "user_id",
            name="uq_workspace_member",
        ),
    )

    id = Column(
        String(26),
        primary_key=True,
        default=lambda: str(ULID()),
    )

    workspace_id = Column(
        String(26), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )

    user_id = Column(
        String(26),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    role = Column(
        SQLEnum(WorkspaceRole),
        nullable=False,
        default=WorkspaceRole.MEMBER,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    workspace = relationship(
        "Workspace",
        back_populates="members",
    )

    user = relationship(
        "User",
        back_populates="workspace_members",
    )
