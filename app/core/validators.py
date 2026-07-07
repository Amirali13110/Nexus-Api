import re


def validate_username(username: str) -> str:
    username = username.strip()

    if not username:
        raise ValueError("Username cannot be empty")

    if len(username) < 3 or len(username) > 30:
        raise ValueError("Username must be between 3 and 30 characters")

    if not re.fullmatch(r"[a-zA-Z0-9_]+", username):
        raise ValueError("Username can only contain letters, numbers, and underscores")

    if username[0].isdigit():
        raise ValueError("Username cannot start with a number")

    return username.lower()


def validate_password(password: str) -> str:
    if password != password.strip():
        raise ValueError("Password must not start or end with whitespace")

    if len(password) < 8 or len(password) > 128:
        raise ValueError("Password must be between 8 and 128 characters")

    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\[\];'`~]", password):
        raise ValueError("Password must contain at least one special character")

    return password


def validate_full_name(full_name: str | None) -> str | None:
    if full_name is None:
        return None

    full_name = full_name.strip()

    if full_name == "":
        return None

    if len(full_name) < 3:
        raise ValueError("Full name must be at least 3 characters long")

    if len(full_name) > 100:
        raise ValueError("Full name cannot exceed 100 characters")

    return full_name
