from future.application import Future
from future.controllers import WebSocketController
from future.lifespan import Lifespan
from future.routing import RouteGroup, WebSocket
from future.testing import FutureTestClient


async def test_websocket_accepts_and_sends() -> None:
    routes = [
        RouteGroup(
            name="websockets",
            subdomain="api",
            routes=[
                WebSocket(path="/ws/<int:id>", endpoint=WebSocketController.websocket_handler, name="websocket_endpoint"),
            ],
        ),
    ]
    app = Future(lifespan=Lifespan(), config={"APP_DEBUG": False, "APP_DOMAIN": "example.com", "OPENAPI": {"enabled": False, "auto_routes": False}})
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        websocket = await client.websocket_connect("ws://127.0.0.1/ws/123", headers={"Host": "api.example.com"})
        assert websocket.accepted
        assert websocket._first == "Echo: Hello from WebSocket!"
        await websocket.close()


async def test_websocket_duplex_echo() -> None:
    routes = [
        RouteGroup(
            name="websockets",
            routes=[
                WebSocket(path="/ws/<int:id>", endpoint=WebSocketController.websocket_handler, name="ws"),
            ],
        ),
    ]
    app = Future(lifespan=Lifespan(), config={"APP_DEBUG": True, "APP_DOMAIN": "", "OPENAPI": {"enabled": False, "auto_routes": False}})
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        websocket = await client.websocket_connect("ws://127.0.0.1/ws/1", headers={"Host": "127.0.0.1"})
        assert websocket._first.startswith("Echo:")
        await websocket.send("ping")
        assert await websocket.recv() == "Echo: ping"
        await websocket.close()


async def test_websocket_path_params_register() -> None:
    routes = [
        RouteGroup(
            name="websockets",
            routes=[
                WebSocket(path="/ws/<int:id>", endpoint=WebSocketController.websocket_handler, name="ws"),
            ],
        ),
    ]
    app = Future(lifespan=Lifespan(), config={"APP_DEBUG": True, "APP_DOMAIN": "", "OPENAPI": {"enabled": False, "auto_routes": False}})
    app.add_routes(routes=routes)
    keys = list(next(iter(app.routes.values())).keys())
    assert any("WEBSOCKET" in key and "/ws/<int:id>" in key for key in keys)

    async with FutureTestClient(app) as client:
        websocket = await client.websocket_connect("ws://127.0.0.1/ws/456", headers={"Host": "127.0.0.1"})
        assert websocket._first.startswith("Echo:")
        await websocket.close()


async def test_websocket_not_found_closes() -> None:
    app = Future(lifespan=Lifespan(), config={"APP_DEBUG": True, "APP_DOMAIN": "", "OPENAPI": {"enabled": False, "auto_routes": False}})
    app.add_routes(routes=[])

    async with FutureTestClient(app) as client:
        try:
            await client.websocket_connect("ws://127.0.0.1/missing", headers={"Host": "127.0.0.1"})
            assert False, "expected ConnectionError"
        except ConnectionError as exc:
            assert "1008" in str(exc) or "Not Found" in str(exc)
