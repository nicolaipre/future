# from future.middleware import Middleware
# from future.routing import Route, RouteGroup
from typing import Any, Awaitable, Callable, MutableMapping

# ASGI specific
ASGIScope = MutableMapping[str, Any]
ASGIMessage = MutableMapping[str, Any]
ASGISend = Callable[[ASGIMessage], Awaitable[None]]
ASGIReceive = Callable[[], Awaitable[ASGIMessage]]

## Middleware specific
# MiddlewareDict = dict[str, Middleware]

# Routing specific
# RouteList = list[Route | RouteGroup]
# RouteDict = dict[str, dict[str, Callable]]
