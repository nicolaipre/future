# ✨ Future ✨
[ASGI](https://asgi.readthedocs.io/) framework for minimal web APIs — routing, middleware, Active Record, migrations, seeds, OpenAPI, and interval tasks. Explicit and decorator-free.

[![Build Status](https://github.com/nicolaipre/future/actions/workflows/ci.yml/badge.svg)](https://github.com/nicolaipre/future/actions)
[![Package version](https://badge.fury.io/py/star.svg)](https://pypi.org/project/future-api/)
[![codecov](https://codecov.io/gh/nicolaipre/future/branch/master/graph/badge.svg)](https://codecov.io/gh/nicolaipre/future)
[![Changelog](https://img.shields.io/badge/changelog-v1.0.0-green.svg)](https://github.com/nicolaipre/future/blob/master/CHANGELOG.md)

## Documentation
Full guides live under **[docs/](docs/index.md)** (also `poetry run mkdocs serve`):

| Guide | Topic |
|-------|--------|
| [Installation](docs/installation.md) | Poetry / path dep / `future init` |
| [Getting started](docs/getting-started.md) | Boot, controllers, config |
| [HTTP](docs/http.md) | Request, Response, middleware, sessions |
| [Routing](docs/routing.md) | Path params, groups |
| [Database](docs/database.md) | Connections, Active Record, migrate/seed |
| [OpenAPI](docs/openapi.md) | Swagger / ReDoc / Scalar / RapiDoc |
| [Lifespan & tasks](docs/lifespan-tasks.md) | Startup / cron intervals |
| [CLI](docs/cli.md) | `init`, `routes`, `make:*`, `migrate` |
| [Quick reference](docs/quick-reference.md) | Cheat sheet |
| [Examples](docs/examples.md) | Working snippets |
| [Gaps](docs/gaps.md) | What’s missing / next |

## Install
```shell
# In an app next to this repo:
# future = { path = "../future", develop = true }
poetry install
poetry run future --help
```

Details: [docs/installation.md](docs/installation.md).

## Hello
```python
from future.application import Future
from future.controllers import Controller
from future.lifespan import Lifespan
from future.response import Response
from future.routing import Get, RouteGroup

class HomeController(Controller):
    async def index(self) -> Response:
        return self.response.json({"ok": True})

app = Future(lifespan=Lifespan([], [], []), config={"APP_DOMAIN": "", "APP_NAME": "Demo"})
app.add_routes([RouteGroup(name="Main", routes=[Get("/", HomeController.index, "home")])])
app.run(host="127.0.0.1", port=8000)
```

## Demo
Larger sketch of routing, groups, OpenAPI, websockets, and interval tasks (same ideas that used to live in `example.py`):

```python
from datetime import datetime, timedelta
from future.application import Future
from future.controllers import DebugController, GraphQLController, OpenAPIController, WebSocketController, WelcomeController
from future.middleware import TestMiddlewareRequest, TestMiddlewareResponse
from future.routing import Get, Post, RouteGroup, WebSocket
from future.settings import APP_DEBUG, APP_DOMAIN, APP_LOG_LEVEL, APP_NAME
from future.lifespan import Lifespan
from future.tasks import Task, Unit, check_dns, check_system_uptime, daily_backup

routes = [
    Get("/users/<int:user_id>/<str:arg2>", DebugController.args, "getUserInfo"),
    Get("/", WelcomeController.root, "Welcome"),
    Get("/test", DebugController.test, "test"),
    Post("/graphql", GraphQLController.query, "GraphQL"),
    Get("/openapi.json", OpenAPIController.openapi, "OpenAPI Schema"),
    Get("/docs", OpenAPIController.swagger, "Swagger UI"),
    Get("/redoc", OpenAPIController.redoc, "ReDoc"),
    RouteGroup(
        name="API",
        subdomain="dev",
        prefix="/api",
        middlewares=[TestMiddlewareRequest, TestMiddlewareResponse],
        routes=[
            Get("/", WelcomeController.root, "Welcome"),
            Get("/cats/<int:cat_id>", DebugController.some_handler, "get_cat"),
            Get("/dogs/<uuid:dog_id>", DebugController.some_handler, "get_dog"),
            RouteGroup(
                name="Nested",
                subdomain="nested",
                prefix="/nested",
                routes=[Get("/ping", DebugController.ping, "Pong")],
            ),
        ],
    ),
    RouteGroup(
        name="websockets",
        subdomain="api",
        routes=[WebSocket("/ws/<int:id>", WebSocketController.websocket_handler, "websocket_endpoint")],
    ),
]

lifespan = Lifespan(
    startup_tasks=[Task("init_database", func=None)],
    shutdown_tasks=[Task("close_connections", func=None)],
    cron_tasks=[
        Task("dns_check", interval=5, unit=Unit.MINUTES, func=check_dns, args=("example.com",)),
        Task("system_uptime", interval=1, unit=Unit.HOURS, func=check_system_uptime),
        Task(
            "daily_backup",
            interval=1,
            unit=Unit.DAYS,
            start_time=datetime.now().replace(hour=2, minute=0, second=0, microsecond=0) + timedelta(days=1),
            func=daily_backup,
        ),
    ],
)

app = Future(
    lifespan=lifespan,
    config={"APP_NAME": APP_NAME, "APP_DOMAIN": APP_DOMAIN, "APP_DEBUG": APP_DEBUG, "APP_LOG_LEVEL": APP_LOG_LEVEL},
)
app.add_routes(routes=routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, workers=1, access_log=True)
```

Put this in your app’s `run.py` (or keep developing against a project that has one). `poetry run future routes` loads `app` from `run.py`.

## Versioning
[Semantic Versioning](https://semver.org/) via git tags (`make version`). See [CHANGELOG.md](CHANGELOG.md).

## License
See [LICENSE](LICENSE).
