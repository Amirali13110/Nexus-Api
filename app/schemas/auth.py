import re
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from app.core.validators import validate_full_name
from app.core.validators import validate_password, validate_username


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=100)
    username: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        return validate_username(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password(v)

    @field_validator("full_name")
    @classmethod
    def validate_fullname(cls, v: str) -> str:
        return validate_full_name(v)


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class UserResponse(BaseModel):
    id: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password(v)


class UpdatePasswordRequest(BaseModel):
    password: str
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password(v)


class UpdateEmailRequest(BaseModel):
    password: str
    new_email: EmailStr

    @field_validator("new_email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.strip().lower()


class ConfirmEmailUpdateRequest(BaseModel):
    token: str
