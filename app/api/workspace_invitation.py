from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.auth import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.models.workspace_invitation import (
    WorkspaceInvitation,
    InvitationStatus,
)
from app.schemas.workspace_invitation import (
    SentWorkspaceInvitationResponse,
    WorkspaceInvitationPayload,
    WorkspaceInvitationResponse,
)

router = APIRouter(
    prefix="/workspace-invitations",
    tags=["Workspace Invitations"],
)


@router.post(
    "/{workspace_id}/invitations",
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace_invitation(
    workspace_id: str,
    payload: WorkspaceInvitationPayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Workspace).where(
            Workspace.id == workspace_id,
        )
    )
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found.",
        )

    if workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to invite members.",
        )

    if payload.email == current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot invite yourself.",
        )

    result = await db.execute(select(User).where(User.email == payload.email))
    invited_user = result.scalar_one_or_none()

    if invited_user:
        result = await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace.id,
                WorkspaceMember.user_id == invited_user.id,
            )
        )

        existing_member = result.scalar_one_or_none()

        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this workspace.",
            )

    result = await db.execute(
        select(WorkspaceInvitation).where(
            WorkspaceInvitation.workspace_id == workspace.id,
            WorkspaceInvitation.email == payload.email,
            WorkspaceInvitation.status == InvitationStatus.PENDING,
        )
    )

    existing_invitation = result.scalar_one_or_none()

    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending invitation already exists.",
        )

    invitation = WorkspaceInvitation(
        workspace_id=workspace.id,
        invited_by_id=current_user.id,
        email=payload.email,
        role=payload.role,
        status=InvitationStatus.PENDING,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    db.add(invitation)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create invitation.",
        )

    return {"message": "Invitation sent successfully."}


@router.get(
    "",
    response_model=list[WorkspaceInvitationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_workspace_invitations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkspaceInvitation)
        .options(
            joinedload(WorkspaceInvitation.workspace),
            joinedload(WorkspaceInvitation.invited_by).joinedload(User.profile),
        )
        .where(
            WorkspaceInvitation.email == current_user.email,
            WorkspaceInvitation.status == InvitationStatus.PENDING,
            WorkspaceInvitation.expires_at > datetime.now(timezone.utc),
        )
        .order_by(
            WorkspaceInvitation.created_at.desc(),
        )
    )

    invitations = result.scalars().all()

    return invitations


@router.post(
    "/{invitation_id}/accept",
    status_code=status.HTTP_200_OK,
)
async def accept_workspace_invitation(
    invitation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkspaceInvitation).where(
            WorkspaceInvitation.id == invitation_id,
        )
    )

    invitation = result.scalar_one_or_none()

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found.",
        )

    if invitation.email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to accept this invitation.",
        )

    if invitation.status != InvitationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation is no longer valid.",
        )

    if invitation.expires_at <= datetime.now(timezone.utc):
        invitation.status = InvitationStatus.EXPIRED

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Invitation has expired.",
        )

    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == invitation.workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )

    existing_member = result.scalar_one_or_none()

    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of this workspace.",
        )

    member = WorkspaceMember(
        workspace_id=invitation.workspace_id,
        user_id=current_user.id,
        role=invitation.role,
    )

    db.add(member)

    invitation.status = InvitationStatus.ACCEPTED
    invitation.accepted_at = datetime.now(timezone.utc)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to accept invitation.",
        )

    return {
        "message": "Invitation accepted successfully.",
    }


@router.post(
    "/{invitation_id}/decline",
    status_code=status.HTTP_200_OK,
)
async def decline_workspace_invitation(
    invitation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkspaceInvitation).where(
            WorkspaceInvitation.id == invitation_id,
        )
    )

    invitation = result.scalar_one_or_none()

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found.",
        )

    if invitation.email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to decline this invitation.",
        )

    if invitation.status != InvitationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation is no longer valid.",
        )

    if invitation.expires_at <= datetime.now(timezone.utc):
        invitation.status = InvitationStatus.EXPIRED

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Invitation has expired.",
        )

    invitation.status = InvitationStatus.DECLINED

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to decline invitation.",
        )

    return {
        "message": "Invitation declined successfully.",
    }


@router.post(
    "/{invitation_id}/cancel",
    status_code=status.HTTP_200_OK,
)
async def cancel_workspace_invitation(
    invitation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkspaceInvitation).where(
            WorkspaceInvitation.id == invitation_id,
        )
    )

    invitation = result.scalar_one_or_none()

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found.",
        )

    if invitation.invited_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel this invitation.",
        )

    if invitation.status != InvitationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation is no longer valid.",
        )

    if invitation.expires_at <= datetime.now(timezone.utc):
        invitation.status = InvitationStatus.EXPIRED

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Invitation has expired.",
        )

    invitation.status = InvitationStatus.CANCELED

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to cancel invitation.",
        )

    return {
        "message": "Invitation canceled successfully.",
    }


@router.get(
    "/sent",
    response_model=list[SentWorkspaceInvitationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_sent_workspace_invitations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkspaceInvitation)
        .options(
            joinedload(WorkspaceInvitation.workspace),
        )
        .where(
            WorkspaceInvitation.invited_by_id == current_user.id,
        )
        .order_by(
            WorkspaceInvitation.created_at.desc(),
        )
    )

    invitations = result.scalars().all()

    return invitations
