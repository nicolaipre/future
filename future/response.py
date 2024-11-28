from typing import Callable


class Response:
    def __init__(self, body: bytes = b"", status: int = 200, headers=None):
        self.body = body
        self.status = status
        self.headers = headers or [[b"content-type", b"text/plain"]]

    async def __call__(self, send: Callable) -> None:
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


class PlainTextResponse(Response):
    pass


class JSONResponse(Response):
    pass
