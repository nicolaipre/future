# WebSockets
Register with `WebSocket` from `future.routing`. Dispatch mirrors HTTP: middleware `before` / `after`, controller DI, path params. Unhandled errors close with code **1011**.

## Route
```python
from future.routing import RouteGroup, WebSocket
from future.controllers import WebSocketController

routes = [
    RouteGroup(
        name="websockets",
        routes=[
            WebSocket("/ws/<int:id>", WebSocketController.websocket_handler, "ws"),
        ],
    ),
]
```

## Controller
Return a `WebSocketResponse` (not a normal HTTP `Response`):

```python
from typing import Any
from future.controllers import Controller
from future.response import WebSocketResponse

class WebSocketController(Controller):
    async def websocket_handler(self, **params: Any) -> WebSocketResponse:
        message = params.get("message", "Hello from WebSocket!")
        return WebSocketResponse(self.request.receive, message=message)
```

Built-in `WebSocketController.websocket_handler` is an echo: optional greeting, then `Echo: <text>` until disconnect.

## WebSocketResponse
```python
ws = WebSocketResponse(self.request.receive, message="hi")
# ASGI runner calls ws(send): accept → optional greeting → duplex loop
await ws.accept()
await ws.send_text("hello")
await ws.send_bytes(b"...")
text = await ws.receive_text()   # None on disconnect
await ws.close(code=1000)
```

Path params from the route (e.g. `id`) are passed as kwargs like HTTP actions.
