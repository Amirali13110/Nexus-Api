from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.core.config import settings
from app.core.security import get_current_user
from app.models.auth import User
from app.api.workspace import router as workspace_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(workspace_router)


@app.get("/")
async def root():
    return {"message": f"Welcome to the nexus"}
