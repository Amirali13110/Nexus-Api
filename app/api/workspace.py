from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.auth import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember, WorkspaceRole
from app.schemas.workspace import WorkspacePayload, WorkspaceListItem, WorkspaceResponse

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace(
    workspace: WorkspacePayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Workspace).where(
            Workspace.owner_id == current_user.id,
            Workspace.slug == workspace.slug,
        )
    )

    existing_workspace = result.scalar_one_or_none()

    if existing_workspace:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a workspace with this slug.",
        )

    new_workspace = Workspace(
        owner_id=current_user.id,
        name=workspace.name,
        slug=workspace.slug,
        description=workspace.description,
    )
    db.add(new_workspace)

    await db.flush()

    owner_member = WorkspaceMember(
        workspace_id=new_workspace.id, user_id=current_user.id, role=WorkspaceRole.OWNER
    )

    db.add(owner_member)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create workspace.",
        )

    await db.refresh(new_workspace)

    return WorkspaceResponse.model_validate(new_workspace)


@router.get(
    "",
    response_model=list[WorkspaceListItem],
)
async def get_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Workspace)
        .join(Workspace.members)
        .where(WorkspaceMember.user_id == current_user.id)
        .order_by(Workspace.created_at.desc())
    )

    workspaces = result.scalars().all()

    return workspaces


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_200_OK,
)
async def get_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Workspace)
        .join(Workspace.members)
        .where(
            Workspace.id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )

    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found.",
        )

    return workspace


@router.patch(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
)
async def update_workspace(
    workspace_id: str,
    workspace: WorkspacePayload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.owner_id == current_user.id,
        )
    )

    existing_workspace = result.scalar_one_or_none()

    if not existing_workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found.",
        )

    result = await db.execute(
        select(Workspace).where(
            Workspace.owner_id == current_user.id,
            Workspace.slug == workspace.slug,
            Workspace.id != workspace_id,
        )
    )

    duplicate_slug = result.scalar_one_or_none()

    if duplicate_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a workspace with this slug.",
        )

    existing_workspace.name = workspace.name
    existing_workspace.slug = workspace.slug
    existing_workspace.description = workspace.description

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to update workspace.",
        )

    await db.refresh(existing_workspace)

    return WorkspaceResponse.model_validate(existing_workspace)


@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.owner_id == current_user.id,
        )
    )

    workspace = result.scalar_one_or_none()

    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found.",
        )

    await db.delete(workspace)
    await db.commit()
