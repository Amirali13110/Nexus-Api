from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


def start_scheduler():
    scheduler.start()


def stop_scheduler():
    scheduler.shutdown(wait=False)
