import re

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.core.validators import validate_full_name, validate_username


class ProfileUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=30)
    full_name: str | None = Field(default=None, max_length=100)
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: HttpUrl | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None):
        return validate_username(v)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str | None):
        return validate_full_name(v)

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, v: str | None):
        if v is None:
            return None

        v = v.strip()

        if v == "":
            return None

        if len(v) < 3:
            raise ValueError("Bio must be at least 3 characters long")

        return v


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    username: str
    full_name: str | None
    bio: str | None
    avatar_url: HttpUrl | None

    model_config = ConfigDict(from_attributes=True)
