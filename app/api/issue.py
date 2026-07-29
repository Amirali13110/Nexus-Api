from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.enums.issue import IssuePriority, IssueSortBy, IssueStatus, SortOrder
from app.enums.member import WorkspaceRole
from app.models.auth import User
from app.models.issue import Issue
from app.models.project import Project
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember

from app.schemas.issue import (
    IssueAssigneeResponse,
    IssueCreate,
    IssueResponse,
    IssueUpdate,
)

from app.core.security import get_current_user

router = APIRouter(prefix="/issues", tags=["Issues"])


@router.post(
    "/workspaces/{workspace_id}/projects/{project_id}",
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

    assignee = None

    if issue.assignee:
        assignee = IssueAssigneeResponse(
            id=issue.assignee.id,
            full_name=issue.assignee.profile.full_name,
        )

    return IssueResponse(
        id=issue.id,
        title=issue.title,
        description=issue.description,
        status=issue.status,
        priority=issue.priority,
        due_date=issue.due_date,
        created_by=issue.created_by,
        created_at=issue.created_at,
        updated_at=issue.updated_at,
        workspace_id=issue.workspace_id,
        project_id=issue.project_id,
        assignee=assignee,
    )


@router.get(
    "/workspaces/{workspace_id}/projects/{project_id}",
    response_model=list[IssueResponse],
    status_code=status.HTTP_200_OK,
)
async def get_issues(
    workspace_id: str,
    project_id: str,
    issue_status: IssueStatus | None = None,
    search: str | None = None,
    assignee_id: str | None = None,
    sort_by: IssueSortBy = IssueSortBy.CREATED_AT,
    sort_order: SortOrder = SortOrder.DESC,
    priority: IssuePriority | None = None,
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

    query = (
        select(Issue)
        .options(selectinload(Issue.assignee).selectinload(User.profile))
        .where(
            Issue.workspace_id == workspace_id,
            Issue.project_id == project_id,
        )
    )

    if search:
        query = query.where(
            or_(
                Issue.title.ilike(f"%{search}%"),
                Issue.description.ilike(f"%{search}%"),
            )
        )

    if issue_status:
        query = query.where(
            Issue.status == issue_status,
        )

    if priority:
        query = query.where(
            Issue.priority == priority,
        )
    if assignee_id:
        query = query.where(
            Issue.assignee_id == assignee_id,
        )

    sort_fields = {
        IssueSortBy.CREATED_AT: Issue.created_at,
        IssueSortBy.UPDATED_AT: Issue.updated_at,
        IssueSortBy.TITLE: Issue.title,
        IssueSortBy.PRIORITY: Issue.priority,
        IssueSortBy.STATUS: Issue.status,
        IssueSortBy.DUE_DATE: Issue.due_date,
    }

    sort_column = sort_fields[sort_by]

    if sort_order == SortOrder.ASC:
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    result = await db.execute(query)

    issues = result.scalars().all()

    response = []

    for issue in issues:
        assignee = None

        if issue.assignee:
            assignee = IssueAssigneeResponse(
                id=issue.assignee.id,
                full_name=issue.assignee.profile.full_name,
            )

        response.append(
            IssueResponse(
                id=issue.id,
                title=issue.title,
                description=issue.description,
                status=issue.status,
                priority=issue.priority,
                due_date=issue.due_date,
                created_at=issue.created_at,
                updated_at=issue.updated_at,
                workspace_id=issue.workspace_id,
                project_id=issue.project_id,
                created_by=issue.created_by,
                assignee=assignee,
            )
        )
    return response


@router.get(
    "/assigned",
    response_model=list[IssueResponse],
    status_code=status.HTTP_200_OK,
)
async def get_assigned_issues(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(Issue)
        .options(selectinload(Issue.assignee).selectinload(User.profile))
        .where(Issue.assignee_id == current_user.id)
        .order_by(Issue.created_at.desc())
    )

    issues = result.scalars().all()

    response = []

    for issue in issues:
        assignee = None

        if issue.assignee:
            assignee = IssueAssigneeResponse(
                id=issue.assignee.id,
                full_name=issue.assignee.profile.full_name,
            )

        response.append(
            IssueResponse(
                id=issue.id,
                title=issue.title,
                description=issue.description,
                status=issue.status,
                priority=issue.priority,
                due_date=issue.due_date,
                created_at=issue.created_at,
                updated_at=issue.updated_at,
                workspace_id=issue.workspace_id,
                project_id=issue.project_id,
                created_by=issue.created_by,
                assignee=assignee,
            )
        )

    return response


@router.get(
    "/workspaces/{workspace_id}/projects/{project_id}/issues/{issue_id}",
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

    assignee = None

    if issue.assignee:
        assignee = IssueAssigneeResponse(
            id=issue.assignee.id,
            full_name=issue.assignee.profile.full_name,
        )

    return IssueResponse(
        id=issue.id,
        title=issue.title,
        description=issue.description,
        status=issue.status,
        priority=issue.priority,
        due_date=issue.due_date,
        created_by=issue.created_by,
        created_at=issue.created_at,
        updated_at=issue.updated_at,
        workspace_id=issue.workspace_id,
        project_id=issue.project_id,
        assignee=assignee,
    )


@router.patch(
    "/workspaces/{workspace_id}/projects/{project_id}/issues/{issue_id}",
    response_model=IssueResponse,
    status_code=status.HTTP_200_OK,
)
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

    assignee = None

    if issue.assignee:
        assignee = IssueAssigneeResponse(
            id=issue.assignee.id,
            full_name=issue.assignee.profile.full_name,
        )

    return IssueResponse(
        id=issue.id,
        title=issue.title,
        description=issue.description,
        status=issue.status,
        priority=issue.priority,
        due_date=issue.due_date,
        created_by=issue.created_by,
        created_at=issue.created_at,
        updated_at=issue.updated_at,
        workspace_id=issue.workspace_id,
        project_id=issue.project_id,
        assignee=assignee,
    )


@router.delete(
    "/workspaces/{workspace_id}/projects/{project_id}/issues/{issue_id}",
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
