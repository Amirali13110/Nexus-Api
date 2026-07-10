from sqlalchemy import (
    Column,
    DateTime,
    String,
    Text,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from ulid import ULID
import app.models
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    __table_args__ = (
        UniqueConstraint(
            "workspace_id", "slug", name="unique_project_slug_per_workspace"
        ),
    )

    id = Column(
        String(26),
        primary_key=True,
        default=lambda: str(ULID()),
    )

    name = Column(String(255), nullable=False)

    description = Column(Text, nullable=True)

    slug = Column(String(255), nullable=False, index=True)

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

    workspace_id = Column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )

    workspace = relationship("Workspace", back_populates="projects")
    issues = relationship(
        "Issue", back_populates="project", cascade="all,delete-orphan"
    )
