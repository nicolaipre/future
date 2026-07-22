# Examples
Working patterns only. Invented APIs (JWT middleware, `app.add_graphql_route`, sync test clients) are omitted — see [Gaps](gaps.md).

## Hello JSON
```python
from future.application import Future
from future.controllers import Controller
from future.lifespan import Lifespan
from future.response import Response
from future.routing import Get, RouteGroup

class HomeController(Controller):
    async def index(self) -> Response:
        return self.response.json({"ok": True})

app = Future(lifespan=Lifespan([], [], []), config={"APP_DOMAIN": "", "APP_NAME": "Hello"})
app.add_routes([
    RouteGroup(name="Main", routes=[Get("/", HomeController.index, "home")]),
])
```

## Path params + query string
```python
class SearchController(Controller):
    async def user(self, user_id: str) -> Response:
        return self.response.json({"user_id": user_id, "q": self.request.query})

Get("/users/<int:user_id>", SearchController.user, "user")
# GET /users/42?verbose=1  → query {"verbose": "1"}
```

## Middleware short-circuit
```python
from typing import Optional
from future.middleware import Middleware
from future.exceptions import HTTPException

class RequireAuth(Middleware):
    async def before(self) -> Optional[Response]:
        if not self.request.headers.get("authorization"):
            raise HTTPException("unauthorized", 401)
        return None

RouteGroup(name="Api", middlewares=[RequireAuth], routes=[...])
```

## Nested RouteGroup middleware
```python
RouteGroup(
    name="Api",
    middlewares=[RequireAuth],
    routes=[
        RouteGroup(
            name="Admin",
            prefix="/admin",
            middlewares=[AdminOnly],
            routes=[Get("/ping", AdminController.ping, "admin.ping")],
        ),
    ],
)
# before: RequireAuth → AdminOnly → controller; after: reverse
```

## Session cookie
```python
from future.middleware.SessionMiddleware import SessionMiddleware

class MeController(Controller):
    async def login(self) -> Response:
        self.request.session["user"] = "alice"
        return self.response.json({"logged_in": True})

    async def me(self) -> Response:
        return self.response.json({"session": self.request.session})

RouteGroup(
    name="Auth",
    middlewares=[SessionMiddleware],
    routes=[
        Post("/login", MeController.login, "login"),
        Get("/me", MeController.me, "me"),
    ],
)
```

## OpenAPI group
```python
from future.openapi import openapi_routes

RouteGroup(
    name="Docs",
    routes=openapi_routes(uis=["swagger", "redoc", "scalar", "rapidoc"]),
)
```

## Active Record (any registered driver)
```python
from app.config.Database import DATABASES  # dict only; Future registers Connections
from app.models.Trade import Trade

# Future(..., config={"DATABASES": DATABASES})
trades = Trade.order_by("timestamp", "desc").get()
return self.response.json([t.to_dict() for t in trades])
```

## Lifespan + hourly task
```python
from future.lifespan import Lifespan
from future.tasks import Task, Unit

def scrape():
    ...

lifespan = Lifespan(
    startup_tasks=[],
    shutdown_tasks=[],
    cron_tasks=[Task("scrape", interval=1, unit=Unit.HOURS, func=scrape)],
)
```

## More
- README Demo section (full routing / lifespan sketch)
- [Getting started](getting-started.md)
- Nordnet app under the monorepo `backend/` (trades, webhook, OpenAPI)
- [HTTP guide](http.md) · [Database](database.md) · [Gaps](gaps.md)
