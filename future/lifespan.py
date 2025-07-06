import asyncio

from typing import Any

from future.logger import log
from future.scheduler import CronScheduler, Task


class Lifespan:
    """Application lifespan manager with integrated cron scheduler."""

    def __init__(self, startup_tasks: list[Task] | None = None, shutdown_tasks: list[Task] | None = None, cron_tasks: list[Task] | None = None) -> None:
        self.app = None
        self.startup_tasks = startup_tasks or []
        self.shutdown_tasks = shutdown_tasks or []
        self.cron_tasks = cron_tasks or []
        self.scheduler = CronScheduler()
        self.db = None
        self.s3_client = None
        self.redis_client = None
        self.settings = None

    async def __aenter__(self) -> dict[str, Any]:
        """Application startup."""
        async with asyncio.timeout(30):
            log.info("Starting application...")
            await self._run_startup_tasks()
            await self.scheduler.start()
            await self._register_cron_jobs()
            log.info("Application startup complete")
            return {
                "db": self.db,
                "s3_client": self.s3_client,
                "redis_client": self.redis_client,
                "settings": self.settings,
            }

    async def __aexit__(self, exc_type: type | None, exc_value: Exception | None, tb: Any) -> bool | None:
        """Application shutdown."""
        async with asyncio.timeout(30):
            log.info("Shutting down application...")
            await self.scheduler.stop()
            await self._run_shutdown_tasks()
            log.info("Shutdown complete")
        return None

    async def _run_startup_tasks(self) -> None:
        for task in self.startup_tasks:
            if task.func is not None:
                if asyncio.iscoroutinefunction(task.func):
                    await task.func(*task.args, **task.kwargs)
                else:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, task.func, *task.args, **task.kwargs)

    async def _run_shutdown_tasks(self) -> None:
        for task in self.shutdown_tasks:
            if task.func is not None:
                if asyncio.iscoroutinefunction(task.func):
                    await task.func(*task.args, **task.kwargs)
                else:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, task.func, *task.args, **task.kwargs)

    async def _register_cron_jobs(self) -> None:
        """Register cron jobs with the scheduler."""
        for task in self.cron_tasks:
            self.scheduler.add_task(task)

        log.info(f"Registered {len(self.scheduler.tasks)} cron jobs")
