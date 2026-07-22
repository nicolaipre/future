# Quick reference
Cheat sheet aligned with the current codebase. Prefer the longer guides for detail.

## Boot
```python
from future.application import Future
from future.lifespan import Lifespan

app = Future(lifespan=Lifespan([], [], []), config={"APP_DOMAIN": "", "APP_NAME": "App"})
app.add_routes(ROUTES)
app.run(host="127.0.0.1", port=8000)
```

## Controller
```python
from future.controllers import Controller
from future.response import Response

class ItemController(Controller):
    async def index(self) -> Response:
        return self.response.json([])

    async def show(self, id: str) -> Response:
        return self.response.json({"id": id})
```

## Routes
```python
from future.routing import Get, Post, RouteGroup

RouteGroup(
    name="Main",
    prefix="/api",
    middlewares=[SomeMiddleware],
    routes=[
        Get("/items", ItemController.index, "items"),
        Get("/items/<id>", ItemController.show, "item"),
        Post("/webhook", WebhookController.dump, "webhook"),
    ],
)
```

## Request reads
```python
self.request.method
self.request.path
self.request.headers.get("authorization")
self.request.cookies.get("session")
self.request.session["k"] = "v"
self.request.query.get("q")          # str, or list if key repeated
await self.request.body()            # cached after first read
await self.request.json()
await self.request.form()
```

## Response writes
```python
self.response.json(data, status=200)
self.response.html(html)
self.response.text("ok")
self.response.empty(status=204)
self.response.redirect("/x")
self.response.set_cookie("a", "b", max_age=3600, domain="example.com")
```

## Errors
```python
from future.exceptions import HTTPException
raise HTTPException("Not Found", 404)
```

## Middleware
```python
from typing import Optional
from future.middleware import Middleware

class M(Middleware):
    priority = 0
    async def before(self) -> Optional[Response]:
        return None  # or raise HTTPException("...", 401)
    async def after(self) -> Optional[Response]:
        return None
```

```python
from future.middleware.SessionMiddleware import SessionMiddleware
middlewares=[SessionMiddleware]
```

Nested `RouteGroup` middleware accumulates outer → inner → route; `after` runs in reverse.

## OpenAPI
```python
from future.openapi import openapi_routes
openapi_routes(uis=["swagger", "redoc", "scalar", "rapidoc"])
```

```python
"OPENAPI": {
    "enabled": True,
    "uis": ["swagger", "redoc", "scalar", "rapidoc"],
    "redocly_license_key": "",  # optional paid Try-it on /redoc
}
```

## Models
```python
# app/config/Database.py defines DATABASES; pass into Future(config={"DATABASES": DATABASES})
# Future registers Connections at boot — do not call set_connection_details at import time.

Trade.where("price", ">", 10).order_by("price", "desc").get()
Trade.order_by("timestamp", "desc").first()
trade.save()
```

## CLI
```bash
future init myproject
future run
future routes
future make:controller Order
future make:middleware Auth
future make:model Order
future make:migration Order
future make:migrations
future make:seed Order
future make:seeds
future migrate
future seed
future seed OrderSeeder
```

## Test client
```python
from future.testing import FutureTestClient
# async get/post against your Future app
```
