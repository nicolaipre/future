# Routing
## Route helpers
```python
from future.routing import (
    Get, Post, Put, Patch, Delete, Head, Options, WebSocket, RouteGroup,
)
```

Each helper takes `path`, `endpoint`, `name`, and optional `middlewares` / `scopes`.

```python
Get("/health", HealthController.ping, "health")
Post("/webhook", WebhookController.dump, "webhook")
```

`endpoint` is normally `SomeController.action` (unbound method). Future instantiates the controller per request.

## Path parameters
```python
Get("/users/<int:user_id>/<str:arg2>", DebugController.args, "user")
Get("/items/<uuid:item_id>", ItemController.show, "item")
```

Values are passed as kwargs to the action. Types use `Route.value_patterns` (`int`, `str`/`string`, `uuid`, …).

Also supported:

- `/users/:user_id`
- `/users/{user_id}`
- catch-all `*` (see `Route.compile_pattern`)

## HTTP methods
Use the matching helper (`Get`, `Post`, …). Same path with different methods is fine:

```python
Get("/items", ItemController.index, "items.index")
Post("/items", ItemController.create, "items.create")
```

Wrong method on a registered path returns **405** with an `Allow` header. Duplicate path **and** method still conflicts at registration.

## Route groups
```python
RouteGroup(
    name="Api",
    prefix="/api",
    # subdomain="api",   # requires APP_DOMAIN to be set
    middlewares=[AuthMiddleware],
    routes=[
        Get("/trades", TradeController.get_trades, "trades"),
        RouteGroup(
            name="Admin",
            prefix="/admin",
            middlewares=[AdminMiddleware],
            routes=[Get("/ping", AdminController.ping, "admin.ping")],
        ),
    ],
)
```

- `prefix` concatenates for nested groups.
- `subdomain` is ignored in **domainless** mode (`APP_DOMAIN=""`).
- Middleware accumulates outer → inner → route. For `/api/admin/ping` above, `AuthMiddleware` then `AdminMiddleware` run `before` in that order; `after` runs in reverse.

## WebSockets
`WebSocket("/ws/<int:id>", …)` mirrors HTTP for middleware, controller DI, and path params. `WebSocketResponse` accepts, sends an optional greeting, then runs a duplex receive/echo loop until disconnect (errors close with 1011). Treat as a usable echo-style session, not a full WebSocket framework — see [Gaps](gaps.md) / [HTTP](http.md) for the overall stack.

## Listing routes
```bash
poetry run future routes
```

Expects an `app` in `run.py`.
