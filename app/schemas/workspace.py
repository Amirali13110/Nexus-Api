import re
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.core.validators import (
    validate_workspace_description,
    validate_workspace_name,
    validate_workspace_slug,
)


class WorkspacePayload(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    slug: str = Field(min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return validate_workspace_name(v)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        return validate_workspace_slug(v)

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None):
        return validate_workspace_description(v)


class WorkspaceListItem(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class WorkspaceResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    slug: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)
