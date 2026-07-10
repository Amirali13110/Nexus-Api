from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum,
    func,
)
from sqlalchemy.orm import relationship
from ulid import ULID

from app.core.database import Base
from app.enums.issue import IssuePriority, IssueStatus


class Issue(Base):
    __tablename__ = "issues"

    id = Column(
        String(26),
        primary_key=True,
        default=lambda: str(ULID()),
    )
    title = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    workspace_id = Column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    project_id = Column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_by = Column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    assignee_id = Column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    due_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    priority = Column(
        Enum(IssuePriority),
        nullable=False,
        default=0,
    )

    status = Column(
        Enum(IssueStatus),
        nullable=False,
        default=IssueStatus.BACKLOG,
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

    workspace = relationship(
        "Workspace",
        back_populates="issues",
    )

    project = relationship(
        "Project",
        back_populates="issues",
    )

    creator = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_issues",
    )

    assignee = relationship(
        "User",
        foreign_keys=[assignee_id],
        back_populates="assigned_issues",
    )
