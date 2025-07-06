# Usage Guide

This guide covers how to use the Future framework to build ASGI web applications in the explicit, declarative style shown in `example.py`.

## Basic Application Setup

### Creating a Simple Application

```python
from future.application import Future
from future.controllers import WelcomeController
from future.routing import Get

routes = [
    Get(path="/", endpoint=WelcomeController.root, name="Welcome")
]

app = Future()
app.add_routes(routes=routes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

### Configuration

You can configure your application using a config dictionary:

```python
from future.application import Future
from future.settings import APP_NAME, APP_DOMAIN, APP_DEBUG, APP_LOG_LEVEL

config = {
    "APP_NAME": APP_NAME,
    "APP_DOMAIN": APP_DOMAIN,
    "APP_DEBUG": APP_DEBUG,
    "APP_LOG_LEVEL": APP_LOG_LEVEL,
}

app = Future(config=config)
```

## Routing

### Basic Routes

```python
from future.controllers import WelcomeController, DebugController
from future.routing import Get

routes = [
    Get(path="/", endpoint=WelcomeController.root, name="Welcome"),
    Get(path="/test", endpoint=DebugController.test, name="test"),
]
```

### Route with Parameters

```python
from future.controllers import DebugController
from future.routing import Get

routes = [
    Get(path="/users/<int:user_id>", endpoint=DebugController.args, name="getUserInfo"),
]
```

### Route Groups

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

## Middleware

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

## Lifespan Management

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

## WebSocket Support

### WebSocket Routes

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

## Registering All Routes

```python
app = Future()
app.add_routes(routes=routes)
```

## Project Structure

A typical Future project structure:

```
my_future_app/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── settings.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── user_controller.py
│   │   └── api_controller.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth_middleware.py
│   │   └── logging_middleware.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   └── lifespan.py
├── tests/
│   ├── __init__.py
│   ├── test_routes.py
│   └── test_middleware.py
├── pyproject.toml
└── README.md
```

## CLI Commands

### Using the Future CLI

```bash
# Initialize a new project
future init my_project

# List all routes
future routes

# Run the application
python -m uvicorn app.main:app --reload
```

## Best Practices

1. **Keep routes simple**: Use controller classes and static methods
2. **Use middleware for cross-cutting concerns**: Attach to RouteGroups
3. **Organize code with route groups**: Group related routes together
4. **Handle errors gracefully**: Use custom exceptions and proper error responses
5. **Test your application**: Use the built-in test client for comprehensive testing
6. **Use type hints**: Future supports full type checking with mypy
7. **Follow the explicit, declarative pattern**: No decorators, no magic 