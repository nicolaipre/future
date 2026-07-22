from typing import Any

from future.controllers.base import Controller
from future.response import Response, WebSocketResponse


class DebugController(Controller):
    async def test(self) -> Response:
        return self.response.text("lolok")

    async def hello(self) -> Response:
        return self.response.json({"message": "hi"})

    async def test_data(self, data: Any) -> Response:
        return self.response.text(f"data: {data}", status=200)

    async def some_handler(self, **params: Any) -> Response:
        return self.response.text(f"Handled with params: {params}", status=200)

    async def ping(self) -> Response:
        return self.response.text("Pong\n")

    async def test2(self, data: Any) -> Response:
        return self.response.text(str(data), status=200)

    async def args(self, user_id: Any, arg2: Any) -> Response:
        return self.response.text(f"{user_id=}, {arg2=}\n")


class WelcomeController(Controller):
    async def root(self) -> Response:
        return self.response.text("✨ Welcome to Future! ✨")


class WebSocketController(Controller):
    """Controller for WebSocket endpoints."""

    async def websocket_handler(self, **params: Any) -> WebSocketResponse:
        """Echo WebSocket: greeting, then duplex Echo: <text> until disconnect."""
        message = params.get("message", "Hello from WebSocket!")
        return WebSocketResponse(self.request.receive, message=message)
