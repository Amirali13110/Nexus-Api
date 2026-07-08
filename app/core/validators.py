import re


def validate_username(v: str) -> str:
    v = v.strip()

    if not v:
        raise ValueError("Username cannot be empty")

    if len(v) < 3 or len(v) > 30:
        raise ValueError("Username must be between 3 and 30 characters")

    if not re.fullmatch(r"[a-zA-Z0-9_]+", v):
        raise ValueError("Username can only contain letters, numbers, and underscores")

    if v[0].isdigit():
        raise ValueError("Username cannot start with a number")

    return v.lower()


def validate_password(v: str) -> str:
    if v != v.strip():
        raise ValueError("Password must not start or end with whitespace")

    if len(v) < 8 or len(v) > 128:
        raise ValueError("Password must be between 8 and 128 characters")

    if not re.search(r"[A-Z]", v):
        raise ValueError("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", v):
        raise ValueError("Password must contain at least one lowercase letter")

    if not re.search(r"\d", v):
        raise ValueError("Password must contain at least one digit")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\[\];'`~]", v):
        raise ValueError("Password must contain at least one special character")

    return v


def validate_full_name(v: str | None) -> str | None:
    if v is None:
        return None

    v = v.strip()

    if v == "":
        return None

    if len(v) < 3:
        raise ValueError("Full name must be at least 3 characters long")

    if len(v) > 100:
        raise ValueError("Full name cannot exceed 100 characters")

    return v


def validate_workspace_name(v: str) -> str:
    v = v.strip()

    if len(v) < 3:
        raise ValueError("Workspace name must be at least 3 characters long")

    return v


def validate_workspace_slug(v: str) -> str:
    v = v.strip().lower()

    if not re.fullmatch(r"[a-z0-9-]+", v):
        raise ValueError(
            "Slug can only contain lowercase letters, numbers, and hyphens"
        )

    if "--" in v:
        raise ValueError("Slug cannot contain consecutive hyphens")

    if v.startswith("-") or v.endswith("-"):
        raise ValueError("Slug cannot start or end with a hyphen")

    return v


def validate_workspace_description(v: str | None) -> str | None:
    if v is None:
        return None

    v = v.strip()

    if v == "":
        return None

    if len(v) > 500:
        raise ValueError("Description cannot exceed 500 characters")

    return v
