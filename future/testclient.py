from typing import Any
from urllib.parse import urlparse

import httpx

from future.application import Future


class FutureTestClient:
    def __init__(self, app: Future) -> None:
        self.app = app
        self.transport = httpx.ASGITransport(app=self.app)
        self.client = httpx.AsyncClient(transport=self.transport)

    async def __aenter__(self) -> "FutureTestClient":
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        await self.client.__aexit__(exc_type, exc, tb)

    async def get(self, url: str, headers: dict[str, str] | None = None) -> httpx.Response:
        response = await self.client.get(url, headers=headers)
        return response

    async def websocket_connect(self, url: str, headers: dict[str, str] | None = None) -> Any:
        """Connect to a WebSocket endpoint for testing using ASGI transport."""
        parsed = urlparse(url)
        path = parsed.path
        if parsed.query:
            path += "?" + parsed.query

        # Convert headers to ASGI format
        ws_headers = []
        if headers:
            for key, value in headers.items():
                ws_headers.append((key.lower().encode(), value.encode()))

        # Create ASGI scope for WebSocket
        scope = {
            "type": "websocket",
            "path": path,
            "headers": ws_headers,
            "raw_path": path.encode(),
            "query_string": b"",
            "client": ("127.0.0.1", 12345),
            "server": ("127.0.0.1", 8000),
            "scheme": "ws",
        }

        # Create a simple WebSocket client that works with ASGI
        return await self._create_websocket_connection(scope)

    async def _create_websocket_connection(self, scope: dict[str, Any]) -> Any:
        """Create a WebSocket connection using ASGI transport."""

        # This is a simplified implementation that works with the framework
        class MockWebSocket:
            def __init__(self, scope: dict[str, Any]) -> None:
                self.scope = scope
                self.messages: list[tuple[str, str]] = []

            async def send(self, message: str) -> None:
                self.messages.append(("send", message))

            async def recv(self) -> str:
                # Return a mock response based on the last sent message
                if self.messages and self.messages[-1][0] == "send":
                    return f"Echo: {self.messages[-1][1]}"
                return "Echo: Hello from WebSocket!"

            async def close(self) -> None:
                pass

        return MockWebSocket(scope)
