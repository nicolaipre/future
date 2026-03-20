from future.types import ASGIReceive, ASGIScope
from urllib.parse import parse_qs
from typing import Any
import json


class Request:
    def __init__(self, scope: ASGIScope, receive: ASGIReceive):
        self.scope = scope
        self.receive = receive
        self.method = scope["method"]
        self.path = scope["path"]
        self.headers = dict([(key.decode("utf-8"), value.decode("utf-8")) for key, value in scope["headers"]])  # FIXME: why decode?
        self.host = self.headers.get("host", "")
        # self.host = dict(scope['headers']).get(b'host', b'').decode()
        self.context: dict[str, Any] = {}  # for custom data we inject into the request
        self.scheme = scope["scheme"]
        self.session = {}

    async def body(self) -> bytes:
        more_body = True
        body: bytes = b""
        while more_body:
            message = await self.receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)
        return body

    async def json(self) -> dict[str, Any]:
        body = await self.body()
        return json.loads(body)
    
    async def form(self) -> dict[str, Any]:
        body = await self.body()
        return parse_qs(body.decode("utf-8"))
