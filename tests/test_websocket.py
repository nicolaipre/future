from future.application import Future
from future.controllers import WebSocketController
from future.lifespan import Lifespan
from future.routing import RouteGroup, WebSocket
from future.testclient import FutureTestClient


async def test_websocket_basic() -> None:
    """Test basic WebSocket functionality."""
    routes = [
        RouteGroup(
            name="websockets",
            subdomain="api",
            routes=[
                WebSocket(path="/ws/<int:id>", endpoint=WebSocketController.websocket_handler, name="websocket_endpoint"),  # type: ignore[reportAttributeAccessIssue]
            ],
        ),
    ]

    lifespan = Lifespan()
    app = Future(lifespan=lifespan, config={"APP_DEBUG": False, "APP_DOMAIN": "example.com"})
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        # Test WebSocket connection through ASGI
        websocket = await client.websocket_connect("ws://127.0.0.1/ws/123", headers={"Host": "api.example.com"})
        await websocket.send("hello")
        reply = await websocket.recv()
        assert reply == "Echo: hello"
        await websocket.close()


async def test_websocket_with_params() -> None:
    """Test WebSocket with URL parameters."""
    routes = [
        RouteGroup(
            name="websockets",
            subdomain="api",
            routes=[
                WebSocket(path="/ws/<int:id>", endpoint=WebSocketController.websocket_handler, name="websocket_endpoint"),  # type: ignore[reportAttributeAccessIssue]
            ],
        ),
    ]

    lifespan = Lifespan()
    app = Future(lifespan=lifespan, config={"APP_DEBUG": False, "APP_DOMAIN": "example.com"})
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        # Test WebSocket connection with different ID
        websocket = await client.websocket_connect("ws://127.0.0.1/ws/456", headers={"Host": "api.example.com"})
        await websocket.send("test message")
        reply = await websocket.recv()
        assert reply == "Echo: test message"
        await websocket.close()


async def test_websocket_empty_message() -> None:
    """Test WebSocket with empty message."""
    routes = [
        RouteGroup(
            name="websockets",
            subdomain="api",
            routes=[
                WebSocket(path="/ws/<int:id>", endpoint=WebSocketController.websocket_handler, name="websocket_endpoint"),  # type: ignore[reportAttributeAccessIssue]
            ],
        ),
    ]

    lifespan = Lifespan()
    app = Future(lifespan=lifespan, config={"APP_DEBUG": False, "APP_DOMAIN": "example.com"})
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        # Test WebSocket connection
        websocket = await client.websocket_connect("ws://127.0.0.1/ws/789", headers={"Host": "api.example.com"})
        await websocket.send("")
        reply = await websocket.recv()
        assert reply == "Echo: "
        await websocket.close()
