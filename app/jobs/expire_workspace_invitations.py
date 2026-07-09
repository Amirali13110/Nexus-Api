from datetime import datetime, timezone

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace_invitation import (
    WorkspaceInvitation,
    InvitationStatus,
)


async def expire_workspace_invitations(
    db: AsyncSession,
):
    await db.execute(
        update(WorkspaceInvitation)
        .where(
            WorkspaceInvitation.status == InvitationStatus.PENDING,
            WorkspaceInvitation.expires_at <= datetime.now(timezone.utc),
        )
        .values(
            status=InvitationStatus.EXPIRED,
        )
    )

    await db.commit()
