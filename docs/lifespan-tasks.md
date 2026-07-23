# Lifespan and tasks
```python
from future.lifespan import Lifespan
from future.tasks import Task, Unit

def scrape():
    ...

lifespan = Lifespan(
    startup_tasks=[],
    shutdown_tasks=[],
    cron_tasks=[
        Task("scrape", interval=1, unit=Unit.HOURS, func=scrape),
    ],
)
app = Future(lifespan=lifespan, config=config)
```

ASGI lifespan runs `startup_tasks`, starts the interval scheduler for `cron_tasks`, and on shutdown runs `shutdown_tasks`.

`Unit`: `SECONDS`, `MINUTES`, `HOURS`, `DAYS`. Fixed intervals only (not crontab). Each worker runs its own scheduler.

```bash
future make:task Cleanup
```

Wire the generated callable into `Task(..., func=...)`.
