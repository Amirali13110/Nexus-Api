import app.models

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)

from sqlalchemy.orm import relationship
from ulid import ULID

from app.core.database import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    __table_args__ = (
        UniqueConstraint(
            "owner_id",
            "slug",
            name="uq_workspace_owner_slug",
        ),
    )

    id = Column(
        String(26),
        primary_key=True,
        default=lambda: str(ULID()),
    )

    owner_id = Column(
        String(26),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    slug = Column(
        String(100),
        nullable=False,
        index=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    invitations = relationship("WorkspaceInvitation", back_populates="workspace")

    projects = relationship("Project", back_populates="workspace")

    members = relationship(
        "WorkspaceMember",
        back_populates="workspace",
    )
