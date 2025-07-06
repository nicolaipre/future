import asyncio

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional

from future.logger import log


class Unit(Enum):
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"


class Task:
    def __init__(
        self,
        name: str,
        interval: Optional[int] = None,
        unit: Optional[Unit] = None,
        start_time: Optional[datetime] = None,
        kwargs: Optional[dict[str, Any]] = None,
        func: Optional[Callable[..., Any]] = None,
        args: tuple[Any, ...] = (),
    ) -> None:
        self.name = name
        self.interval = interval
        self.unit = unit
        self.start_time = start_time
        self.kwargs = kwargs or {}
        self.func = func
        self.args = args


class ScheduledTask:
    """Represents a scheduled task with its timing configuration."""

    def __init__(
        self,
        name: str,
        func: Callable[..., Any],
        interval: int,
        unit: Unit,
        start_time: Optional[datetime] = None,
        last_run: Optional[datetime] = None,
        next_run: Optional[datetime] = None,
        args: tuple[Any, ...] = (),
        kwargs: Optional[dict[str, Any]] = None,
    ) -> None:
        self.name = name
        self.func = func
        self.interval = interval
        self.unit = unit
        self.start_time = start_time
        self.last_run = last_run
        self.next_run = next_run
        self.args = args
        self.kwargs = kwargs if kwargs is not None else {}

        if self.start_time is None:
            self.start_time = datetime.now()
        self.calculate_next_run()

    def calculate_next_run(self) -> None:
        """Calculate when this task should run next."""
        if self.last_run is None:
            self.next_run = self.start_time
        else:
            if self.unit == Unit.SECONDS:
                self.next_run = self.last_run + timedelta(seconds=self.interval)
            elif self.unit == Unit.MINUTES:
                self.next_run = self.last_run + timedelta(minutes=self.interval)
            elif self.unit == Unit.HOURS:
                self.next_run = self.last_run + timedelta(hours=self.interval)
            elif self.unit == Unit.DAYS:
                self.next_run = self.last_run + timedelta(days=self.interval)


class CronScheduler:
    """A cron-like scheduler for running background tasks."""

    def __init__(self) -> None:
        self.tasks: dict[str, ScheduledTask] = {}
        self.running = False
        self.check_interval = 1.0  # Check every second for tasks to run

    def add_task(self, task: Task) -> None:
        if task.func is None or task.interval is None or task.unit is None:
            log.warning(f"Skipping task '{task.name}' - missing required parameters")
            return

        scheduled = ScheduledTask(
            name=task.name,
            func=task.func,
            interval=task.interval,
            unit=task.unit,
            start_time=task.start_time,
            args=task.args,
            kwargs=task.kwargs,
        )
        self.tasks[task.name] = scheduled
        log.info(f"Added scheduled task '{task.name}' to run every {task.interval} {task.unit.value}")

    def remove_task(self, name: str) -> bool:
        """Remove a scheduled task."""
        if name in self.tasks:
            del self.tasks[name]
            log.info(f"Removed scheduled task '{name}'")
            return True
        return False

    def get_task(self, name: str) -> Optional[ScheduledTask]:
        """Get a scheduled task by name."""
        return self.tasks.get(name)

    def list_tasks(self) -> list[str]:
        """List all scheduled task names."""
        return list(self.tasks.keys())

    async def _run_task(self, task: ScheduledTask) -> None:
        """Run a single task."""
        try:
            log.debug(f"Running scheduled task '{task.name}'")
            if asyncio.iscoroutinefunction(task.func):
                # Run async functions directly
                await task.func(*task.args, **task.kwargs)
            else:
                # Run sync functions in thread pool
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, task.func, *task.args, **task.kwargs)

            task.last_run = datetime.now()
            task.calculate_next_run()
            if task.next_run:
                log.debug(f"Completed scheduled task '{task.name}', next run at {task.next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                log.debug(f"Completed scheduled task '{task.name}'")

        except Exception as e:
            log.error(f"Error running scheduled task '{task.name}': {e}")
            # Don't update last_run on error, so it will retry next cycle

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop that checks for tasks to run."""
        log.info("Starting cron scheduler...")

        while self.running:
            now = datetime.now()
            tasks_to_run = []

            # Check which tasks need to run
            for task in self.tasks.values():
                if task.next_run and now >= task.next_run:
                    tasks_to_run.append(task)

            # Run tasks that are due
            if tasks_to_run:
                log.debug(f"Running {len(tasks_to_run)} scheduled tasks")
                for task in tasks_to_run:
                    asyncio.create_task(self._run_task(task))

            # Wait before next check
            await asyncio.sleep(self.check_interval)

        log.info("Cron scheduler stopped")

    async def start(self) -> None:
        """Start the scheduler."""
        if not self.running:
            self.running = True
            asyncio.create_task(self._scheduler_loop())

    async def stop(self) -> None:
        """Stop the scheduler."""
        self.running = False


# --- Minimal cron task functions ---
async def check_dns(domain: str = "example.com") -> None:
    import socket

    try:
        ip = socket.gethostbyname(domain)
        log.info(f"DNS: {domain} -> {ip}")
    except socket.gaierror as e:
        log.error(f"DNS lookup failed for {domain}: {e}")


async def check_http_status(url: str = "https://httpbin.org/status/200") -> None:
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            log.info(f"HTTP: {url} -> {response.status_code}")
    except Exception as e:
        log.error(f"HTTP check failed for {url}: {e}")


async def check_ssh_banner(host: str = "localhost", port: int = 22) -> None:
    try:
        reader, writer = await asyncio.open_connection(host, port)
        banner = await reader.read(1024)
        log.info(f"SSH banner for {host}:{port}: {banner.decode(errors='ignore').strip()}")
        writer.close()
        await writer.wait_closed()
    except Exception as e:
        log.error(f"SSH banner check failed for {host}:{port}: {e}")


def check_system_uptime() -> None:
    import subprocess

    try:
        result = subprocess.run(["uptime"], capture_output=True, text=True, timeout=5.0)
        if result.returncode == 0:
            log.info(f"System uptime: {result.stdout.strip()}")
        else:
            log.error(f"Uptime command failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        log.error("Uptime command timed out")
    except Exception as e:
        log.error(f"Error checking system uptime: {e}")


def check_disk_usage(path: str = "/") -> None:
    import shutil

    try:
        total, used, _ = shutil.disk_usage(path)
        used_percent = (used / total) * 100
        log.info(f"Disk usage for {path}: {used_percent:.1f}% used ({used // (1024**3)}GB / {total // (1024**3)}GB)")
    except Exception as e:
        log.error(f"Error checking disk usage for {path}: {e}")


def check_memory_usage() -> None:
    import psutil

    try:
        memory = psutil.virtual_memory()
        log.info(f"Memory usage: {memory.percent}% used ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)")
    except ImportError:
        log.warning("psutil not available, skipping memory check")
    except Exception as e:
        log.error(f"Error checking memory usage: {e}")


def sync_task_example() -> None:
    log.info(f"Running sync task at {datetime.now()}")


async def daily_backup() -> None:
    log.info(f"Running daily backup at {datetime.now()}")
    # TODO: Implement actual backup logic
    # Example: backup database, files, etc.
