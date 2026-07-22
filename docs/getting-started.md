# Getting started
## Minimal app
```python
from future.application import Future
from future.controllers import Controller
from future.lifespan import Lifespan
from future.response import Response
from future.routing import Get, RouteGroup

class HomeController(Controller):
    async def index(self) -> Response:
        return self.response.json({"message": "hello"})

ROUTES = [
    RouteGroup(
        name="Main",
        routes=[Get("/", HomeController.index, "home")],
    )
]

config = {
    "APP_DOMAIN": "",      # empty = domainless mode (ignore Host / subdomains)
    "APP_NAME": "MyApp",
    "APP_DEBUG": True,     # uvicorn reload when run()
    "OPENAPI": {
        "enabled": True,
        "uis": ["swagger", "redoc", "scalar", "rapidoc"],
        "auto_routes": False,
    },
}

app = Future(lifespan=Lifespan([], [], []), config=config)
app.add_routes(ROUTES)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
```

## Controllers
Inherit `Controller`. Do **not** write your own `__init__` unless you need extra deps — the base class injects request/response:

```python
from future.controllers import Controller
from future.response import Response

class TradeController(Controller):
    async def get_trades(self) -> Response:
        return self.response.json([])

    async def get_trade(self, id: str) -> Response:
        # id comes from /trades/<id>
        return self.response.json({"id": id})
```

Register with a **class method reference** (not an instance):

```python
Get("/trades", TradeController.get_trades, "trades")
Get("/trades/<id>", TradeController.get_trade, "trade")
```

Future resolves the class, constructs `TradeController(request, response)`, and calls the action.

## Config keys the core uses
| Key | Role |
|-----|------|
| `APP_DOMAIN` | Host/subdomain routing; `""` = domainless |
| `APP_NAME` | Banner / OpenAPI title fallback |
| `APP_DEBUG` | Uvicorn reload; `future` logger DEBUG vs INFO; strip `:port` from `Host` |
| `OPENAPI` | Docs enablement, UIs, license key, etc. |

Pass `DATABASES` in `Future(config={...})` so connections register at boot (see [Database](database.md)). CLI `migrate` / `seed` load `run.py` for the same registration path.

App code should log with `from future.logger import log` (level follows `APP_DEBUG`).

## Project layout (`future init`)
```text
myproject/
  run.py
  app/
    config/          # Settings, Database
    controllers/
    middleware/
    models/
    plugins/
    tasks/
    routes.py
  database/
    migrations/
    seeds/
```

## OpenAPI docs in routes
```python
from future.openapi import openapi_routes
from future.routing import RouteGroup

ROUTES = [
    RouteGroup(
        name="Docs",
        routes=openapi_routes(uis=["swagger", "redoc", "scalar", "rapidoc"]),
    ),
    # ...
]
```

Then open `/docs`, `/redoc`, `/scalar`, or `/rapidoc`. Details: [OpenAPI](openapi.md).

## Learn next
- [HTTP: Request, Response, Middleware](http.md)
- [Routing](routing.md)
- [Database and models](database.md)
- [Lifespan and tasks](lifespan-tasks.md)
