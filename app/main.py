from fastapi import Depends, FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.core.config import settings
from app.core.scheduler import start_scheduler, stop_scheduler
from app.core.security import get_current_user
from app.jobs.register import register_jobs
from app.models.auth import User
from app.api.workspace import router as workspace_router
from app.api.issue import router as issue_router
from app.api.project import router as project_router
from app.api.workspace_member import router as workspace_member_router
from app.api.workspace_invitation import router as workspace_invitation_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    register_jobs()
    start_scheduler()

    yield

    stop_scheduler()


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
app.include_router(workspace_invitation_router)
app.include_router(workspace_member_router)
app.include_router(project_router)
app.include_router(issue_router)


@app.get("/")
async def root():
    return {"message": f"Welcome to the nexus"}
