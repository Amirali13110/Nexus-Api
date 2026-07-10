from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    description: str | None = Field(default=None, max_length=1000)

    slug: str = Field(min_length=1, max_length=255)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)

    description: str | None = Field(default=None, max_length=1000)

    slug: str | None = Field(default=None, min_length=1, max_length=255)


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    slug: str
    workspace_id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
