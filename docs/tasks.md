# Tasks
`future.tasks.Task` is the unit you pass into `Lifespan` — once at startup, once at shutdown, or on a fixed interval (`cron_tasks`).

```python
from future.tasks import Task, Unit
```

## Task constructor
| Argument | Role |
|----------|------|
| `name` | Label in logs / scheduler |
| `func` | Sync or async callable to run |
| `args` | Positional args for `func` (tuple) |
| `kwargs` | Keyword args for `func` |
| `interval` | How often (required for `cron_tasks`) |
| `unit` | `Unit.SECONDS` / `MINUTES` / `HOURS` / `DAYS` |
| `start_time` | First run time (`datetime`); default is “now” when registered |
| `jitter` | Optional extra delay `0 … jitter` seconds on each next-run calculation |

Cron tasks need `func`, `interval`, and `unit`. Startup / shutdown tasks only need `name` and `func` (interval is ignored).

## Wire into Lifespan
```python
from datetime import datetime, timedelta
from future.application import Future
from future.lifespan import Lifespan
from future.tasks import Task, Unit
from app.tasks.Scrape import scraper
from app.tasks.Cleanup import run as cleanup

startup_tasks = [
    Task("boot_log", func=lambda: print("starting")),
]

shutdown_tasks = [
    Task("flush", func=cleanup),
]

cron_tasks = [
    Task("scrape", interval=1, unit=Unit.HOURS, func=scraper),
    Task("scrape_jitter", interval=1, unit=Unit.HOURS, func=scraper, jitter=60),
    Task(
        "daily_backup",
        interval=1,
        unit=Unit.DAYS,
        start_time=datetime.now().replace(hour=2, minute=0, second=0, microsecond=0) + timedelta(days=1),
        func=cleanup,
    ),
    Task("dns", interval=5, unit=Unit.MINUTES, func=check_dns, args=("example.com",)),
]

lifespan = Lifespan(
    startup_tasks=startup_tasks,
    shutdown_tasks=shutdown_tasks,
    cron_tasks=cron_tasks,
)
app = Future(lifespan=lifespan, config=config)
```

## Startup and shutdown
On ASGI lifespan enter, Future runs each `startup_tasks` entry in order (async `await`ed, sync in a thread pool), then starts the scheduler and registers `cron_tasks`.

On exit, the scheduler stops, then `shutdown_tasks` run the same way.

```python
async def connect_cache():
    ...

def close_files():
    ...

startup_tasks = [Task("cache", func=connect_cache)]
shutdown_tasks = [Task("files", func=close_files)]
```

## Interval (cron) tasks
Fixed intervals only — not crontab expressions. The scheduler checks about once per second and runs due tasks concurrently (`asyncio.create_task`). Errors are logged; `last_run` is not updated on failure so the task retries on the next cycle.

```python
Task("scrape", interval=1, unit=Unit.HOURS, func=scraper)
Task("ping", interval=30, unit=Unit.SECONDS, func=ping, kwargs={"url": "https://example.com"})
```

Each uvicorn **worker** runs its own scheduler (no cross-worker lock).

## Generate a task stub
```bash
future make:task Cleanup
```

Creates something under `app/tasks/` with a `run()` (or similar) callable — pass it as `func=`:

```python
from app.tasks.Cleanup import run

cron_tasks = [Task("cleanup", interval=1, unit=Unit.DAYS, func=run)]
```

## Built-in examples
`future.tasks` also exports small helpers (`check_dns`, `check_http_status`, `daily_backup`, …) useful as samples. Prefer app-specific modules under `app/tasks/` for real work.

See [Lifespan](lifespan.md) for the ASGI wrapper that runs these lists.
