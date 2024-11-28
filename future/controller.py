from future.request import Request
from future.response import Response
import json


class Controller:
    pass


class WelcomeController(Controller):
    async def root(request: Request) -> Response:
        # return Response(body="✨ Welcome to Future! ✨")
        return Response(body=b"Welcome to Future!\n")

    async def ping(request: Request) -> Response:
        return Response(body=b"Pong\n")

    async def test(request: Request, data) -> Response:
        return Response(body=data, status=200)

    async def openapi(request: Request) -> Response:
        openapi_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "Simple ASGI App",
                "version": "1.0.0",
            },
            "paths": {},
        }
        return Response(
            body=json.dumps(openapi_schema).encode("utf-8"),
            headers=[[b"content-type", b"application/json"]],
            status=200,
        )
