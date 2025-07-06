# Quick Reference

A quick reference guide for common Future framework patterns and usage, matching the explicit, declarative style of example.py.

## Basic Setup

```python
from future.application import Future
from future.controllers import WelcomeController
from future.routing import Get

routes = [
    Get(path="/", endpoint=WelcomeController.root, name="Welcome")
]

app = Future()
app.add_routes(routes=routes)
app.run()
```

## Routes

### Basic Route
```python
from future.controllers import WelcomeController
from future.routing import Get

routes = [
    Get(path="/", endpoint=WelcomeController.root, name="Welcome")
]
```

### Route with Parameters
```python
from future.controllers import DebugController
from future.routing import Get

routes = [
    Get(path="/users/<int:user_id>", endpoint=DebugController.args, name="getUserInfo")
]
```

### Route with HTTP Methods
```python
from future.controllers import DebugController
from future.routing import Get

routes = [
    Get(path="/api/users", endpoint=DebugController.users, name="users"),
    Get(path="/api/users", endpoint=DebugController.create_user, name="create_user", methods=["POST"])
]
```

### Route with Middleware
```python
from future.middleware import TestMiddlewareRequest, TestMiddlewareResponse
from future.controllers import WelcomeController
from future.routing import Get, RouteGroup

api_routes = RouteGroup(
    name="API",
    prefix="/api",
    middlewares=[TestMiddlewareRequest, TestMiddlewareResponse],
    routes=[
        Get(path="/", endpoint=WelcomeController.root, name="Welcome"),
    ],
)

routes = [api_routes]
```

## Middleware

### Basic Middleware
```python
from future.middleware import TestMiddlewareRequest, TestMiddlewareResponse
from future.controllers import WelcomeController
from future.routing import Get, RouteGroup

api_routes = RouteGroup(
    name="API",
    prefix="/api",
    middlewares=[TestMiddlewareRequest, TestMiddlewareResponse],
    routes=[
        Get(path="/", endpoint=WelcomeController.root, name="Welcome"),
    ],
)

routes = [api_routes]
```

### Intercepting Middleware
```python
from future.middleware import AuthMiddleware
from future.controllers import WelcomeController
from future.routing import Get, RouteGroup

api_routes = RouteGroup(
    name="API",
    prefix="/api",
    routes=[
        Get(path="/", endpoint=WelcomeController.root, name="Welcome"),
    ],
    middlewares=[AuthMiddleware]
)

routes = [api_routes]
```

## Responses

### Text Response
```python
from future.controllers import WelcomeController
from future.routing import Get

routes = [
    Get(path="/", endpoint=WelcomeController.root, name="Welcome")
]
```

### JSON Response
```python
from future.controllers import DebugController
from future.routing import Get

routes = [
    Get(path="/api", endpoint=DebugController.api, name="api")
]
```

### Response with Status Code
```python
from future.controllers import DebugController
from future.routing import Get

routes = [
    Get(path="/api/users", endpoint=DebugController.created, name="created", status_code=201)
]
```

### Response with Headers
```python
from future.controllers import DebugController
from future.routing import Get

routes = [
    Get(path="/api/users", endpoint=DebugController.custom, name="custom", headers={"X-Custom": "value"})
]
```

## WebSocket

### WebSocket Route
```python
from future.controllers import WebSocketController
from future.routing import WebSocket, RouteGroup

ws_routes = RouteGroup(
    name="websockets",
    subdomain="api",
    routes=[
        WebSocket(path="/ws/<int:id>", endpoint=WebSocketController.websocket_handler, name="websocket_endpoint"),
    ],
)

routes = [ws_routes]
```

## Lifespan

### Startup, Shutdown, and Cron Tasks
```python
from future.lifespan import Lifespan
from future.scheduler import Task, Unit, check_dns
from datetime import datetime, timedelta

startup_tasks = [Task("init_database", func=None)]
shutdown_tasks = [Task("close_connections", func=None)]
cronjobs = [
    Task("dns_check", interval=5, unit=Unit.MINUTES, func=check_dns, args=("example.com",)),
]
lifespan = Lifespan(startup_tasks, shutdown_tasks, cronjobs)

app = Future(lifespan=lifespan)
```

## Scheduler

### Basic Scheduler
```python
from future.scheduler import TaskScheduler

class TaskScheduler(TaskScheduler):
    def daily_backup(self):
        print("Daily backup")
    def hourly_cleanup(self):
        print("Hourly cleanup")

app.set_scheduler(TaskScheduler())
```

### Custom Schedules
```python
from future.scheduler import CustomScheduler

class CustomScheduler(CustomScheduler):
    def setup_schedules(self):
        return [
            (60, self.minute_task),      # Every 60 seconds
            (3600, self.hourly_task),    # Every hour
        ]
    def minute_task(self):
        print("Minute task")
    def hourly_task(self):
        print("Hourly task")
```

## Route Groups

### Creating Route Groups
```python
from future.controllers import DebugController
from future.routing import Get, RouteGroup

api_routes = RouteGroup(
    name="API",
    prefix="/api",
    routes=[
        Get(path="/users/<int:user_id>", endpoint=DebugController.args, name="getUserInfo"),
        Get(path="/cats/<int:cat_id>", endpoint=DebugController.some_handler, name="get_cat"),
    ],
)

routes = [api_routes]
```

### Adding Middleware to Route Groups
```python
from future.middleware import TestMiddlewareRequest, TestMiddlewareResponse
from future.controllers import WelcomeController
from future.routing import Get, RouteGroup

api_routes = RouteGroup(
    name="API",
    prefix="/api",
    middlewares=[TestMiddlewareRequest, TestMiddlewareResponse],
    routes=[
        Get(path="/", endpoint=WelcomeController.root, name="Welcome"),
    ],
)

routes = [api_routes]
```

## GraphQL

### Basic GraphQL Setup
```python
from future.controllers import GraphQLController
import strawberry

@strawberry.type
class User:
    id: int
    name: str

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: int) -> User:
        return User(id=id, name="John")

schema = strawberry.Schema(query=Query)
app.add_graphql_route("/graphql", GraphQLController(schema))
```

## Testing

### Test Client
```python
from future.testing import FutureTestClient

client = FutureTestClient(app)

# Test HTTP route
response = client.get("/")
assert response.status_code == 200

# Test WebSocket
with client.websocket_connect("/ws/chat") as ws:
    ws.send("Hello")
    message = ws.receive()
    assert message == "Echo: Hello"
```

## Error Handling

### Custom Exceptions
```python
from future.exceptions import FutureException, Response

class UserNotFoundError(FutureException):
    def __init__(self, user_id: str):
        super().__init__(f"User {user_id} not found", 404)

def get_user(user_id: str):
    if user_id == "999":
        raise UserNotFoundError(user_id)
    return Response(f"User {user_id}")

routes = [
    Get(path="/users/<int:user_id>", endpoint=get_user, name="getUserInfo")
]
```

## Configuration

### Settings Class
```python
from future.settings import APP_NAME, APP_DOMAIN, APP_DEBUG, APP_LOG_LEVEL

config = {
    "APP_NAME": APP_NAME,
    "APP_DOMAIN": APP_DOMAIN,
    "APP_DEBUG": APP_DEBUG,
    "APP_LOG_LEVEL": APP_LOG_LEVEL,
}

app = Future(config=config)
```

## CLI Commands

```bash
# Initialize project
future init my_project

# List routes
future routes

# Run with uvicorn
python -m uvicorn app.main:app --reload
```

## Common Patterns

### Route with Query Parameters
```python
from future.controllers import DebugController
from future.routing import Get

routes = [
    Get(path="/search", endpoint=DebugController.search, name="search")
]
```

### Route with Request Body
```python
from future.controllers import DebugController
from future.routing import Get

routes = [
    Get(path="/api/users", endpoint=DebugController.create_user, name="create_user", methods=["POST"])
]
```

### Middleware with Response Modification
```python
from future.middleware import CORSMiddleware
from future.controllers import WelcomeController
from future.routing import Get, RouteGroup

api_routes = RouteGroup(
    name="API",
    prefix="/api",
    routes=[
        Get(path="/", endpoint=WelcomeController.root, name="Welcome"),
    ],
    middlewares=[CORSMiddleware]
)

routes = [api_routes]
```

## Registering All Routes
```python
app = Future()
app.add_routes(routes=routes)
``` 