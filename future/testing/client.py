from typing import Any
from urllib.parse import urlparse

import asyncio
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

    async def post(self, url: str, json: dict[str, Any] | None = None, data: str | bytes | None = None, headers: dict[str, str] | None = None) -> httpx.Response:
        if json is not None:
            response = await self.client.post(url, json=json, headers=headers)
        elif data is not None:
            response = await self.client.post(url, content=data, headers=headers)
        else:
            response = await self.client.post(url, headers=headers)
        return response

    async def websocket_connect(self, url: str, headers: dict[str, str] | None = None) -> Any:
        """Connect via real ASGI websocket handshake against the Future app."""
        parsed = urlparse(url)
        path = parsed.path
        if parsed.query:
            path += "?" + parsed.query

        ws_headers = []
        if headers:
            for key, value in headers.items():
                ws_headers.append((key.lower().encode(), value.encode()))

        scope = {
            "type": "websocket",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "path": path,
            "headers": ws_headers,
            "raw_path": path.encode(),
            "query_string": b"",
            "client": ("127.0.0.1", 12345),
            "server": ("127.0.0.1", 8000),
            "scheme": "ws",
            "root_path": "",
            "subprotocols": [],
            "extensions": {},
            "state": {},
        }

        send_queue: asyncio.Queue = asyncio.Queue()
        recv_queue: asyncio.Queue = asyncio.Queue()
        await recv_queue.put({"type": "websocket.connect"})

        async def receive() -> dict[str, Any]:
            return await recv_queue.get()

        async def send(message: dict[str, Any]) -> None:
            await send_queue.put(message)

        task = asyncio.create_task(self.app(scope, receive, send))

        class AsgiWebSocket:
            def __init__(self) -> None:
                self.accepted = False
                self.closed = False
                self.close_code = None
                self.close_reason = None
                self._task = task

            async def _next_server_message(self) -> dict[str, Any]:
                while True:
                    try:
                        return await asyncio.wait_for(send_queue.get(), timeout=2.0)
                    except asyncio.TimeoutError:
                        if self._task.done():
                            exc = self._task.exception()
                            if exc:
                                raise exc
                            raise TimeoutError("WebSocket app ended without a message")
                        raise

            async def wait_accepted(self) -> None:
                message = await self._next_server_message()
                if message["type"] == "websocket.close":
                    self.closed = True
                    self.close_code = message.get("code")
                    self.close_reason = message.get("reason")
                    raise ConnectionError(f"WebSocket closed: {self.close_code} {self.close_reason}")
                if message["type"] != "websocket.accept":
                    raise AssertionError(f"Expected websocket.accept, got {message}")
                self.accepted = True

            async def send(self, message: str) -> None:
                await recv_queue.put({"type": "websocket.receive", "text": message})

            async def recv(self) -> str:
                message = await self._next_server_message()
                if message["type"] == "websocket.send":
                    if "text" in message:
                        return message["text"]
                    return message.get("bytes", b"").decode("utf-8")
                if message["type"] == "websocket.close":
                    self.closed = True
                    self.close_code = message.get("code")
                    self.close_reason = message.get("reason")
                    raise ConnectionError(f"WebSocket closed: {self.close_code} {self.close_reason}")
                raise AssertionError(f"Unexpected message: {message}")

            async def close(self) -> None:
                await recv_queue.put({"type": "websocket.disconnect", "code": 1000})
                try:
                    await asyncio.wait_for(self._task, timeout=2.0)
                except asyncio.TimeoutError:
                    self._task.cancel()

        socket = AsgiWebSocket()
        await socket.wait_accepted()
        # Greeting frame from WebSocketResponse (duplex send/recv available after)
        first = await socket.recv()
        socket._first = first  # type: ignore[attr-defined]
        return socket
