import app.models

from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from ulid import ULID
from app.core.database import Base
from app.enums.member import WorkspaceRole


class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELED = "canceled"


class WorkspaceInvitation(Base):
    __tablename__ = "workspace_invitations"

    id = Column(
        String(26),
        primary_key=True,
        default=lambda: str(ULID()),
    )

    workspace_id = Column(
        String(26),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    invited_by_id = Column(
        String(26),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    email = Column(
        String,
        nullable=False,
        index=True,
    )

    role = Column(
        SQLEnum(WorkspaceRole),
        nullable=False,
        default=WorkspaceRole.MEMBER,
    )

    status = Column(
        SQLEnum(InvitationStatus),
        nullable=False,
        default=InvitationStatus.PENDING,
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    accepted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    workspace = relationship(
        "Workspace",
        back_populates="invitations",
    )

    invited_by = relationship(
        "User",
        back_populates="sent_workspace_invitations",
    )
