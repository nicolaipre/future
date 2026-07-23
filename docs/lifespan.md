# Lifespan
`future.lifespan.Lifespan` is the ASGI lifespan hook required by `Future`. You pass in lists of [Tasks](tasks.md) to run at startup, on a schedule while the app is up, and at shutdown.

```python
from future.lifespan import Lifespan
from future.tasks import Task, Unit
from future.application import Future

lifespan = Lifespan(
    startup_tasks=[
        Task("boot", func=on_boot),
    ],
    shutdown_tasks=[
        Task("teardown", func=on_shutdown),
    ],
    cron_tasks=[
        Task("scrape", interval=1, unit=Unit.HOURS, func=scraper),
    ],
)
app = Future(lifespan=lifespan, config=config)
```

## Slots
| List | When |
|------|------|
| `startup_tasks` | Once on ASGI startup, in order |
| `cron_tasks` | Registered with the interval scheduler after startup |
| `shutdown_tasks` | Once on ASGI shutdown, after the scheduler stops |

Empty lists are fine:

```python
Lifespan(startup_tasks=[], shutdown_tasks=[], cron_tasks=[])
```

## Lifecycle
1. Run `startup_tasks` (async awaited, sync in a thread pool).
2. Start `CronScheduler` and register `cron_tasks`.
3. App serves traffic; interval tasks fire in the background.
4. On shutdown: stop the scheduler, then run `shutdown_tasks`.

How to build a `Task` (name, `func`, interval, jitter, …): see [Tasks](tasks.md).
