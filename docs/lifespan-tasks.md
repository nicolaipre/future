# Lifespan and tasks
ASGI lifecycle (`Lifespan`) lives in `future.lifespan`. Interval `Task` / `Unit` stay in `future.tasks`.

## Lifespan
```python
from future.lifespan import Lifespan
from future.tasks import Task, Unit

startup_tasks = [
    # Task("boot", func=my_startup),
]
shutdown_tasks = [
    # Task("flush", func=my_shutdown),
]
cron_tasks = [
    # Task("scrape", interval=1, unit=Unit.HOURS, func=scraper),
]

lifespan = Lifespan(
    startup_tasks=startup_tasks,
    shutdown_tasks=shutdown_tasks,
    cron_tasks=cron_tasks,
)
app = Future(lifespan=lifespan, config=config)
```

ASGI lifespan startup runs `startup_tasks`, starts the interval scheduler for `cron_tasks`, and shutdown runs `shutdown_tasks`.

## Interval scheduler
`Unit`: `SECONDS`, `MINUTES`, `HOURS`, `DAYS`.

This is **not** crontab syntax — fixed intervals only. Multi-worker deployments do not share locks; each worker runs its own scheduler.

Optional `jitter` (seconds) adds a random delay of `0 … jitter` on each next-run calculation (default off):

```python
Task("scrape", interval=1, unit=Unit.HOURS, func=scraper, jitter=60)
```

## App tasks
Generate a stub:

```bash
poetry run future make:task Cleanup
```

Wire the callable into a `Task(..., func=...)`.
