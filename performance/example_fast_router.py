from collections.abc import Sequence
import logging

from performance.optimized_application import OptimizedFuture
from future.controllers import DebugController, OpenAPIController, WebSocketController, WelcomeController
from future.lifespan import Lifespan
from future.middleware import TestMiddlewareRequest, TestMiddlewareResponse
from future.routing import Get, Route, RouteGroup, WebSocket
from future.scheduler import Task, Unit, check_dns, check_system_uptime
from future.settings import APP_DOMAIN

# DISABLE ALL LOGGING FOR MAXIMUM PERFORMANCE
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger("future").setLevel(logging.CRITICAL)
logging.getLogger("uvicorn").setLevel(logging.CRITICAL)
logging.getLogger("uvicorn.access").setLevel(logging.CRITICAL)
logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)

# Optimized routes - minimal set for performance testing
routes: Sequence[Route | RouteGroup] = [  # type: ignore
    Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # type: ignore[reportAttributeAccessIssue]
    Get(path="/test", endpoint=DebugController.test, name="test"),  # type: ignore[reportAttributeAccessIssue]
    Get(path="/health", endpoint=DebugController.ping, name="health"),  # type: ignore[reportAttributeAccessIssue]
    Get(path="/json", endpoint=DebugController.hello, name="json"),  # type: ignore[reportAttributeAccessIssue]
    # OpenAPI Documentation Routes
    Get(path="/openapi.json", endpoint=OpenAPIController.openapi, name="OpenAPI Schema"),  # type: ignore[reportAttributeAccessIssue]
    Get(path="/swagger-config", endpoint=OpenAPIController.swagger_config, name="Swagger Config"),  # type: ignore[reportAttributeAccessIssue]
    Get(path="/docs", endpoint=OpenAPIController.swagger, name="Swagger UI"),  # type: ignore[reportAttributeAccessIssue]
    Get(path="/redoc", endpoint=OpenAPIController.redoc, name="ReDoc"),  # type: ignore[reportAttributeAccessIssue]
    RouteGroup(  # type: ignore
        name="API",
        subdomain="dev",
        prefix="/api",
        middlewares=[
            TestMiddlewareRequest,  # type: ignore
            TestMiddlewareResponse,  # type: ignore
        ],
        routes=[
            Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # type: ignore[reportAttributeAccessIssue]
            Get(path="/users/<int:user_id>/<str:arg2>", endpoint=DebugController.args, name="getUserInfo"),  # type: ignore[reportAttributeAccessIssue]
            Get(path="/cats/<int:cat_id>", endpoint=DebugController.some_handler, name="get_cat"),  # type: ignore[reportAttributeAccessIssue]
            Get(path="/dogs/<uuid:dog_id>", endpoint=DebugController.some_handler, name="get_dog"),  # type: ignore[reportAttributeAccessIssue]
            RouteGroup(  # type: ignore
                name="Nested",
                subdomain="nested",
                prefix="/nested",
                routes=[
                    Get(path="/ping", endpoint=DebugController.ping, name="Pong")  # type: ignore[reportAttributeAccessIssue]
                ],
            ),  # type: ignore
        ],
    ),  # type: ignore
    RouteGroup(  # type: ignore
        name="websockets",
        subdomain="api",
        routes=[
            WebSocket(path="/ws/<int:id>", endpoint=WebSocketController.websocket_handler, name="websocket_endpoint"),  # type: ignore[reportAttributeAccessIssue]
        ],
    ),  # type: ignore
]

# Minimal startup tasks for performance
startup_tasks = [
    Task("init_database", func=None),
    Task("load_config", func=None),
]

# Minimal shutdown tasks for performance
shutdown_tasks = [
    Task("save_metrics", func=None),
    Task("close_connections", func=None),
]

# Reduced cron jobs for performance
cronjobs = [
    Task("dns_check", interval=5, unit=Unit.MINUTES, func=check_dns, args=("example.com",)),
    Task("system_uptime", interval=1, unit=Unit.HOURS, func=check_system_uptime),
]

lifespan = Lifespan(startup_tasks, shutdown_tasks, cronjobs)
config = {
    "APP_NAME": "Future Fast Router",
    "APP_DOMAIN": APP_DOMAIN,
    "APP_DEBUG": False,  # Disable debug for performance
    "APP_LOG_LEVEL": "CRITICAL",  # Only critical errors
    "APP_ACCESS_LOG": False,  # Disable access logging
}

app = OptimizedFuture(lifespan=lifespan, config=config)
app.add_routes(routes=routes)

if __name__ == "__main__":
    # Run with maximum performance settings
    app.run(
        host="0.0.0.0", 
        port=5000, 
        workers=1,  # Use 1 worker for testing
        access_log=False  # Disable access logging
    ) 