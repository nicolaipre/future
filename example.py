from collections.abc import Sequence
from datetime import datetime, timedelta

from future.application import Future
from future.controllers import DebugController, GraphQLController, OpenAPIController, WebSocketController, WelcomeController
from future.lifespan import Lifespan
from future.middleware import TestMiddlewareRequest, TestMiddlewareResponse
from future.routing import Get, Route, RouteGroup, WebSocket
from future.scheduler import Task, Unit, check_dns, check_ssh_banner, check_system_uptime, daily_backup
from future.settings import APP_DEBUG, APP_DOMAIN, APP_LOG_LEVEL, APP_NAME


routes: Sequence[Route | RouteGroup] = [  # type: ignore
    Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # , middlewares=[TestMiddlewareRequest]),  # type: ignore[reportAttributeAccessIssue]
    Get(path="/test", endpoint=DebugController.test, name="test"),  # , scopes=["debug"]),  # type: ignore[reportAttributeAccessIssue]
    Get(path="/graphql", endpoint=GraphQLController.query, name="GraphQL"),  # , scopes=["user"]),   # type: ignore[reportAttributeAccessIssue]
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
            # ResponseCodeConfuser,  # type: ignore
            # ScopeValidationMiddleware,  # type: ignore
        ],
        routes=[
            Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # type: ignore[reportAttributeAccessIssue]
            Get(path="/users/<int:user_id>/<str:arg2>", endpoint=DebugController.args, name="getUserInfo"),  # type: ignore[reportAttributeAccessIssue]
            Get(path="/cats/<int:cat_id>", endpoint=DebugController.some_handler, name="get_cat"),  # type: ignore[reportAttributeAccessIssue]
            Get(path="/dogs/<uuid:dog_id>", endpoint=DebugController.some_handler, name="get_dog"),  # type: ignore[reportAttributeAccessIssue]
            # We can also use nested RouteGroups
            RouteGroup(  # type: ignore
                name="Nested",
                subdomain="nested",
                prefix="/nested",
                routes=[
                    Get(path="/ping", endpoint=DebugController.ping, name="Pong")  # , scopes=["read:api"]),  # type: ignore[reportAttributeAccessIssue]
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

# Startup tasks (run once when app starts)
startup_tasks = [
    Task("init_database", func=None),
    Task("load_config", func=None),
    Task("start_metrics", func=None),
]

# Shutdown tasks (run once when app stops)
shutdown_tasks = [
    Task("save_metrics", func=None),
    Task("close_connections", func=None),
]

# Cron jobs (run periodically)
cronjobs = [
    Task("dns_check", interval=5, unit=Unit.MINUTES, func=check_dns, args=("example.com",)),
    Task("ssh_banner_check", interval=10, unit=Unit.MINUTES, func=check_ssh_banner, args=("localhost", 22)),
    Task("system_uptime", interval=1, unit=Unit.HOURS, func=check_system_uptime),
    Task(
        "daily_backup",
        interval=1,
        unit=Unit.DAYS,
        start_time=datetime.now().replace(hour=2, minute=0, second=0, microsecond=0) + timedelta(days=1),
        func=daily_backup,
    ),
]

lifespan = Lifespan(startup_tasks, shutdown_tasks, cronjobs)
config = {
    "APP_NAME": APP_NAME,
    "APP_DOMAIN": APP_DOMAIN,
    "APP_DEBUG": APP_DEBUG,
    "APP_LOG_LEVEL": APP_LOG_LEVEL,
}

app = Future(lifespan=lifespan, config=config)
app.add_routes(routes=routes)
# print(app.routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, workers=1)
