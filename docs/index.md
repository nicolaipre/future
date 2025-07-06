# Future Framework Documentation

Welcome to the Future framework documentation. Future is a minimalist, decorator-free ASGI web framework for Python that emphasizes clarity and explicit code patterns.

## What is Future?

Future is a modern Python web framework built on ASGI that:

- **Avoids decorators** - Uses explicit, clear code patterns
- **Minimalist design** - Focuses on simplicity and readability
- **Type-safe** - Full mypy support with comprehensive type hints
- **Modern features** - WebSocket support, GraphQL, scheduled tasks, and more
- **Developer-friendly** - Built-in testing, CLI tools, and comprehensive documentation

## Key Features

- **HTTP Routing** - Simple, parameterized routes with full HTTP method support
- **Middleware System** - Flexible middleware for cross-cutting concerns
- **WebSocket Support** - Real-time communication with WebSocket routes
- **GraphQL Integration** - Built-in GraphQL support with Strawberry
- **Scheduled Tasks** - Native cron-like scheduler for background tasks
- **Lifespan Management** - Startup and shutdown task coordination
- **Testing Tools** - Built-in test client for HTTP and WebSocket testing
- **CLI Tools** - Project scaffolding and route listing utilities

## Quick Start

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

## Documentation Sections

### [Installation](installation.md)
Complete installation guide including dependencies, development setup, and configuration.

### [Usage Guide](usage.md)
Comprehensive guide covering all framework features:
- Basic application setup and configuration
- Routing with parameters and HTTP methods
- Middleware creation and registration
- Lifespan management for startup/shutdown tasks
- WebSocket implementation and real-time communication
- Scheduled tasks and background job management
- JSON responses and error handling
- GraphQL integration with Strawberry
- Testing with the built-in test client
- Project structure and best practices

### [Quick Reference](quick-reference.md)
Fast reference for common patterns and code examples:
- Basic setup and configuration
- Route definitions and patterns
- Middleware implementation
- Response types and status codes
- WebSocket handlers
- Lifespan and scheduler setup
- Route groups and organization
- GraphQL schema definition
- Testing patterns
- Error handling
- CLI commands

### [Examples](examples.md)
Complete working examples demonstrating:
- Basic API server with user management
- Real-time chat application with WebSockets
- GraphQL API with user and post management
- Scheduled task manager with background jobs
- Authentication system with JWT middleware

## Framework Philosophy

Future follows these core principles:

1. **Explicit over Implicit** - Clear, readable code without magic
2. **No Decorators** - Avoids decorator patterns in favor of explicit method calls
3. **Type Safety** - Comprehensive type hints and mypy support
4. **Minimalism** - Focus on essential features with clean APIs
5. **Developer Experience** - Excellent tooling and documentation

## Getting Help

- **GitHub Issues** - Report bugs and request features
- **Documentation** - Comprehensive guides and examples
- **Examples** - Check the `example.py` file for working examples
- **Tests** - Browse test files for usage patterns

## Contributing

We welcome contributions! Please see our contributing guidelines and ensure all code follows our style guide with proper type hints and no decorators.

## 🛠️ Development

```bash
# Run tests
poetry run pytest

# Check code quality
poetry run ruff check .
poetry run mypy .

# Build documentation
poetry run mkdocs build
poetry run mkdocs serve
```

## 📦 Installation

```bash
pip install future-api
```

Or with Poetry:

```bash
poetry add future-api
```

## 🤝 Contributing

We welcome contributions! Please see our GitHub repository for contribution guidelines.

## 📄 License

This project is licensed under the MIT License. 