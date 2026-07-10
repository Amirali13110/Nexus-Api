from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr
from app.models.workspace_invitation import InvitationStatus
from app.enums.member import WorkspaceRole


class WorkspaceInvitationPayload(BaseModel):
    email: EmailStr
    role: WorkspaceRole = WorkspaceRole.MEMBER

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.strip().lower()


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str | None
    avatar_url: str | None = None


class WorkspaceInvitationWorkspace(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str


class WorkspaceInvitationInvitedBy(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    profile: UserProfileResponse


class WorkspaceInvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str

    workspace: WorkspaceInvitationWorkspace
    invited_by: WorkspaceInvitationInvitedBy

    email: EmailStr
    role: WorkspaceRole
    status: InvitationStatus

    expires_at: datetime
    created_at: datetime


class SentWorkspaceInvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    workspace: WorkspaceInvitationWorkspace
    role: WorkspaceRole
    status: InvitationStatus
    expires_at: datetime
    created_at: datetime
