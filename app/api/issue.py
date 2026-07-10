from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.enums.member import WorkspaceRole
from app.models.auth import User
from app.models.issue import Issue
from app.models.project import Project
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember

from app.schemas.issue import IssueCreate, IssueResponse, IssueUpdate

from app.core.security import get_current_user

router = APIRouter(prefix="/workspaces", tags=["Issues"])


@router.post(
    "/{workspace_id}/projects/{project_id}/issues",
    response_model=IssueResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_issue(
    workspace_id: str,
    project_id: str,
    payload: IssueCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )

    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )

    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.workspace_id == workspace_id,
        )
    )

    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if payload.assignee_id:

        result = await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == payload.assignee_id,
            )
        )

        assignee_member = result.scalar_one_or_none()

        if not assignee_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee must be a member of this workspace",
            )

    create_data = payload.model_dump()

    if create_data.get("assignee_id") == "":
        create_data["assignee_id"] = None

    issue = Issue(
        **create_data,
        workspace_id=workspace_id,
        project_id=project_id,
        created_by=current_user.id,
    )

    db.add(issue)

    await db.commit()

    await db.refresh(issue)

    return issue


@router.get(
    "/{workspace_id}/projects/{project_id}/issues",
    response_model=list[IssueResponse],
    status_code=status.HTTP_200_OK,
)
async def get_issues(
    workspace_id: str,
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )

    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this workspace",
        )

    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.workspace_id == workspace_id,
        )
    )

    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    result = await db.execute(
        select(Issue)
        .where(
            Issue.project_id == project_id,
            Issue.workspace_id == workspace_id,
        )
        .order_by(Issue.created_at.desc())
    )

    issues = result.scalars().all()

    return issues


@router.patch(
    "/{workspace_id}/projects/{project_id}/issues/{issue_id}",
    response_model=IssueResponse,
    status_code=status.HTTP_200_OK,
)
@router.get(
    "/{workspace_id}/projects/{project_id}/issues/{issue_id}",
    response_model=IssueResponse,
    status_code=status.HTTP_200_OK,
)
async def get_issue(
    workspace_id: str,
    project_id: str,
    issue_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    # Check workspace membership
    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )

    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this workspace",
        )

    # Check project belongs to workspace
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.workspace_id == workspace_id,
        )
    )

    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Get issue
    result = await db.execute(
        select(Issue).where(
            Issue.id == issue_id,
            Issue.project_id == project_id,
            Issue.workspace_id == workspace_id,
        )
    )

    issue = result.scalar_one_or_none()

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )

    return issue


async def update_issue(
    workspace_id: str,
    project_id: str,
    issue_id: str,
    payload: IssueUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )

    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this workspace",
        )

    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.workspace_id == workspace_id,
        )
    )

    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    result = await db.execute(
        select(Issue).where(
            Issue.id == issue_id,
            Issue.project_id == project_id,
            Issue.workspace_id == workspace_id,
        )
    )

    issue = result.scalar_one_or_none()

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )

    if payload.assignee_id:

        result = await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == payload.assignee_id,
            )
        )

        assignee_member = result.scalar_one_or_none()

        if not assignee_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee must be a member of this workspace",
            )

    update_data = payload.model_dump(exclude_unset=True)

    if "assignee_id" in update_data and update_data["assignee_id"] == "":
        update_data["assignee_id"] = None

    for field, value in update_data.items():
        setattr(issue, field, value)

    await db.commit()

    await db.refresh(issue)

    return issue


@router.delete(
    "/{workspace_id}/projects/{project_id}/issues/{issue_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_issue(
    workspace_id: str,
    project_id: str,
    issue_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )

    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this workspace",
        )

    result = await db.execute(
        select(Workspace).where(
            Workspace.id == workspace_id,
        )
    )

    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.workspace_id == workspace_id,
        )
    )

    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    result = await db.execute(
        select(Issue).where(
            Issue.id == issue_id,
            Issue.project_id == project_id,
            Issue.workspace_id == workspace_id,
        )
    )

    issue = result.scalar_one_or_none()

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )

    is_workspace_owner = workspace.owner_id == current_user.id

    is_admin = member.role == WorkspaceRole.ADMIN

    is_creator = issue.created_by == current_user.id

    if not (is_workspace_owner or is_admin or is_creator):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this issue",
        )

    await db.delete(issue)

    await db.commit()

    return {"message": "Issue deleted successfully"}
