from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    API_PORT: int = 9000
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    RESEND_API_KEY: str
    FRONTEND_RESET_URL: str
    MAIL_FROM: str

    class Config:
        env_file = ".env"


settings = Settings()
