from __future__ import annotations

import enum
import re

from collections.abc import Awaitable, MutableMapping
from typing import Any, Callable, TypedDict


# ASGI specific
ASGIScope = MutableMapping[str, Any]
ASGIMessage = MutableMapping[str, Any]
ASGISend = Callable[[ASGIMessage], Awaitable[None]]
ASGIReceive = Callable[[], Awaitable[ASGIMessage]]


class AsgiEventType(enum.StrEnum):
    LIFESPAN_STARTUP = "lifespan.startup"
    LIFESPAN_STARTUP_COMPLETE = "lifespan.startup.complete"
    LIFESPAN_STARTUP_FAILED = "lifespan.startup.failed"
    LIFESPAN_SHUTDOWN = "lifespan.shutdown"
    LIFESPAN_SHUTDOWN_COMPLETE = "lifespan.shutdown.complete"
    LIFESPAN_SHUTDOWN_FAILED = "lifespan.shutdown.failed"
    HTTP_REQUEST = "http.request"
    HTTP_RESPONSE_START = "http.response.start"
    HTTP_RESPONSE_BODY = "http.response.body"
    WEBSOCKET_CONNECT = "websocket.connect"
    WEBSOCKET_ACCEPT = "websocket.accept"
    WEBSOCKET_RECEIVE = "websocket.receive"
    WEBSOCKET_SEND = "websocket.send"
    WEBSOCKET_DISCONNECT = "websocket.disconnect"
    WEBSOCKET_CLOSE = "websocket.close"


class RegexConfig(TypedDict):
    paths: list[re.Pattern[str]]


class RouteConfig(TypedDict):
    handler: Callable[..., Any]
    middleware: dict[str, list[dict[str, list[Any]]]]  # type: ignore
    regex: dict[str, list[re.Pattern[str] | re.Pattern[bytes]]] | None
