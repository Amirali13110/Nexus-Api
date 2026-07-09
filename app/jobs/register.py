from app.core.scheduler import scheduler
from app.jobs.expire_workspace_invitations import (
    expire_workspace_invitations,
)


def register_jobs():
    scheduler.add_job(
        expire_workspace_invitations,
        trigger="interval",
        hours=1,
        id="expire_workspace_invitations",
        replace_existing=True,
    )
