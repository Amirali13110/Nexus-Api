from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)

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

    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(
        Integer,
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
