from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from app.enums.issue import IssueStatus, IssuePriority


class IssueCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    assignee_id: str | None = None

    due_date: datetime | None = None

    priority: IssuePriority = IssuePriority.NOPRIORITY

    status: IssueStatus = IssueStatus.BACKLOG


class IssueUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    assignee_id: str | None = None

    due_date: datetime | None = None

    priority: IssuePriority | None = None

    status: IssueStatus | None = None


class IssueResponse(BaseModel):
    id: str

    title: str

    description: str | None

    workspace_id: str

    project_id: str

    created_by: str

    assignee_id: str | None

    due_date: datetime | None

    priority: IssuePriority

    status: IssueStatus

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
