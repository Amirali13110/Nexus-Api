from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.auth import User
from app.models.workspace import Workspace
from app.models.workspace_member import (
    WorkspaceMember,
    WorkspaceRole,
)
from app.schemas.workspace_member import (
    WorkspaceMemberResponse,
    WorkspaceMemberRoleUpdate,
)

router = APIRouter(
    prefix="/workspaces",
    tags=["Workspace Members"],
)


@router.get(
    "/{workspace_id}/members",
    response_model=list[WorkspaceMemberResponse],
    status_code=status.HTTP_200_OK,
)
async def get_workspace_members(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )

    current_membership = result.scalar_one_or_none()

    if not current_membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this workspace.",
        )

    result = await db.execute(
        select(WorkspaceMember)
        .options(
            joinedload(WorkspaceMember.user).joinedload(User.profile),
        )
        .where(
            WorkspaceMember.workspace_id == workspace_id,
        )
        .order_by(
            WorkspaceMember.created_at.asc(),
        )
    )

    members = result.scalars().all()

    return members


@router.get(
    "/{workspace_id}/members/{member_id}",
    response_model=WorkspaceMemberResponse,
    status_code=status.HTTP_200_OK,
)
async def get_workspace_member(
    workspace_id: str,
    member_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )

    current_membership = result.scalar_one_or_none()

    if not current_membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this workspace.",
        )

    result = await db.execute(
        select(WorkspaceMember)
        .options(
            joinedload(WorkspaceMember.user).joinedload(User.profile),
        )
        .where(
            WorkspaceMember.id == member_id,
            WorkspaceMember.workspace_id == workspace_id,
        )
    )

    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace member not found.",
        )

    return member


@router.patch(
    "/{workspace_id}/members/{member_id}/role",
    status_code=status.HTTP_200_OK,
)
async def update_member_role(
    workspace_id: str,
    member_id: str,
    payload: WorkspaceMemberRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))

    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    result = await db.execute(
        select(WorkspaceMember)
        .options(joinedload(WorkspaceMember.user))
        .where(
            WorkspaceMember.id == member_id,
            WorkspaceMember.workspace_id == workspace_id,
        )
    )

    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=404, detail="Member not found in this workspace"
        )

    if member.user_id == workspace.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change the workspace owner's role",
        )

    is_owner = current_user.id == workspace.owner_id

    if not is_owner:

        result = await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == current_user.id,
            )
        )

        acting_member = result.scalar_one_or_none()

        if not acting_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this workspace",
            )

        if acting_member.role != WorkspaceRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update member roles",
            )

        if member.role != WorkspaceRole.MEMBER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only update members, not other admins",
            )

    if member.role == payload.role:
        return {"message": "Member role is already set to this role"}

    member.role = payload.role

    await db.commit()

    return {"message": "Member role has been changed successfully"}


@router.delete(
    "/{workspace_id}/members/{member_id}",
    status_code=status.HTTP_200_OK,
)
async def remove_workspace_member(
    workspace_id: str,
    member_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.id == member_id,
            WorkspaceMember.workspace_id == workspace_id,
        )
    )

    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace member not found.",
        )

    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )

    current_membership = result.scalar_one_or_none()

    if not current_membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to manage this workspace.",
        )

    if current_membership.role == WorkspaceRole.MEMBER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to remove members.",
        )

    if member.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove yourself from the workspace.",
        )

    if member.role == WorkspaceRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The workspace owner cannot be removed.",
        )

    if (
        current_membership.role == WorkspaceRole.ADMIN
        and member.role != WorkspaceRole.MEMBER
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins can only remove members.",
        )

    await db.delete(member)

    await db.commit()

    return {
        "message": "Workspace member removed successfully.",
    }


@router.delete(
    "/{workspace_id}/leave",
    status_code=status.HTTP_200_OK,
)
async def leave_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))

    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    if workspace.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Workspace owner cannot leave. Transfer ownership first.",
        )

    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )

    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=404, detail="You are not a member of this workspace"
        )

    await db.delete(member)

    await db.commit()

    return {"message": "You have successfully left the workspace"}
