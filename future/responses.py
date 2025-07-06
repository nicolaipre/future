import json

from collections.abc import Awaitable
from typing import Any, Callable, Optional, Union


class Response:
    def __init__(self, body: Union[str, bytes] = "", status: int = 200, headers: dict[str, str] | None = None, content_type: Optional[str] = None) -> None:
        self.status = status
        self.context: dict[str, Any] = {}  # for custom data we inject into the response

        # Handle body conversion based on type
        if isinstance(body, str):
            self.body = body.encode("utf-8")
            # Auto-detect content type for strings
            if content_type is None:
                content_type = "text/plain"
        elif isinstance(body, bytes):  # type: ignore[reportIncompatibleMethodOverride]
            self.body = body
            if content_type is None:
                content_type = "application/octet-stream"
        else:
            raise TypeError(f"Response body must be str or bytes, got {type(body)}")

        # Set up headers
        if not headers:
            headers = {}

        # Ensure content-type is set
        if "content-type" not in headers and content_type:
            headers["content-type"] = content_type

        self.headers = [[key.encode(), value.encode()] for key, value in headers.items()]

    async def __call__(self, send: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
        # assert type(self.body) == bytes, "Response body must be bytes"

        start_message = {
            "type": "http.response.start",
            "status": self.status,
            "headers": self.headers,
        }
        await send(start_message)

        body_message = {
            "type": "http.response.body",
            "body": self.body,
        }
        await send(body_message)


class WebSocketResponse:
    def __init__(self, message: str = "") -> None:
        self.message = message

    async def __call__(self, send: Any) -> None:
        """Handle WebSocket connection lifecycle."""
        # Accept the WebSocket connection
        await send({"type": "websocket.accept"})

        # Send the message back to the client
        await send({"type": "websocket.send", "text": f"Echo: {self.message}"})


class PlainTextResponse(Response):
    def __init__(self, body: str = "", status: int = 200, headers: dict[str, str] | None = None) -> None:
        super().__init__(body, status, headers or {}, content_type="text/plain")


class JSONResponse(Response):
    def __init__(self, data: Any, status: int = 200, headers: dict[str, str] | None = None) -> None:
        # Convert data to JSON string
        json_data = json.dumps(data, default=str, ensure_ascii=False)
        # Call parent with JSON content type
        super().__init__(body=json_data, status=status, headers=headers, content_type="application/json")


class EmptyResponse(Response):
    def __init__(self, status: int = 204, headers: dict[str, str] | None = None) -> None:
        super().__init__(body="", status=status, headers=headers)


class HTMLResponse(Response):
    def __init__(self, html: str, status: int = 200, headers: dict[str, str] | None = None) -> None:
        super().__init__(body=html, status=status, headers=headers, content_type="text/html")


class PNGResponse(Response):
    def __init__(self, body: bytes = b"", status: int = 200, headers: dict[str, str] | None = None) -> None:
        super().__init__(body, status, headers or {})
        self.headers = [[b"content-type", b"image/png"]]


class ImageResponse(Response):
    def __init__(
        self, body: bytes = b"", status: int = 200, headers: dict[str, str] | None = None, image_content_type: str = "image/png", file_path: str | None = None
    ) -> None:
        if file_path:
            with open(file_path, "rb") as f:
                body = f.read()
        final_headers = headers.copy() if headers else {}
        has_content_type = any(key.lower() == "content-type" for key in final_headers)
        if not has_content_type:
            final_headers["content-type"] = image_content_type
        super().__init__(body=body, status=status, headers=final_headers)


class RedirectResponse(Response):
    pass


class FileResponse(Response):
    def __init__(self, body: bytes = b"", status: int = 200, headers: dict[str, str] | None = None) -> None:
        final_headers = headers.copy() if headers else {}
        has_content_type = any(key.lower() == "content-type" for key in final_headers)
        if not has_content_type:
            final_headers["content-type"] = "application/octet-stream"
        super().__init__(body, status, final_headers)


class StreamingResponse(Response):
    pass
