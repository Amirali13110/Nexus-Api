from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from app.enums.member import WorkspaceRole
from app.schemas.profile import ProfileResponse


class WorkspaceMemberUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    profile: ProfileResponse


class WorkspaceMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: WorkspaceRole
    created_at: datetime

    user: WorkspaceMemberUserResponse


class WorkspaceMemberRoleUpdate(BaseModel):
    role: WorkspaceRole

    @field_validator("role")
    @classmethod
    def validate_role(cls, value):
        if value == WorkspaceRole.OWNER:
            raise ValueError("Owner role cannot be assigned.")
        return value
