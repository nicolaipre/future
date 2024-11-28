from future.types import ASGIScope, ASGIReceive
from future.utils import decode_header


class Request:
    def __init__(self, scope: ASGIScope, receive: ASGIReceive):
        self.scope = scope
        self.receive = receive
        self.method = scope["method"]
        self.path = scope["path"]
        self.headers = dict(decode_header(scope["headers"]))
        self.host = self.headers.get("host", "")
        # self.host = dict(scope['headers']).get(b'host', b'').decode()

    async def body(self) -> bytes:
        more_body = True
        body: bytes = b""
        while more_body:
            message = await self.receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)
        return body
