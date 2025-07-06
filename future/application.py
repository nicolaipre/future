import platform
import sys
import traceback

from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Optional, Union

import uvicorn

from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from future.logger import log
from future.middleware import Middleware
from future.requests import Request
from future.responses import Response
from future.routing import Route, RouteGroup
from future.types import AsgiEventType, ASGIReceive, ASGIScope, ASGISend, RouteConfig


"""
# ASGI SPEC
async def application(scope, receive, send):
    event = await receive()
    ...
    await send({"type": "websocket.send", ...: ...})

example_http_event = {
    "type": "http.request",
    "body": b"Hello World",
    "more_body": False,
}

example_websocket_event = {
    "type": "websocket.send",
    "text": "Hello world!",
}

example_http_scope = {
    'type': 'http',
    'method': 'POST',
    'path': '/echo',
    'headers': [...],
    ...: ...,
}


...


except BaseException:
    event_type = "lifespan.shutdown.failed" if started else "lifespan.startup.failed"
    await send({"type": event_type, "message": traceback.format_exc()})
    raise
await send({"type": "lifespan.shutdown.complete"})

# Custom openapi path
if path == "/openapi.json":
    await self.serve_openapi(send)
    return
while True:
    message = await receive()
    print(f"Got message:", message)
"""


class Future:
    def __init__(self, lifespan: Any, config: dict[str, Any] | None = None) -> None:
        # spawn background tasks in the lifespan startup process... or database connections etc...
        # on shutdown, save shit, send info about shutdown etc...
        self.lifespan = lifespan
        self.routes: dict[str, dict[str, RouteConfig]] = {}
        self.config = config or {}

        domain = self.config.get("APP_DOMAIN", "")

        # Domainless mode: if no domain is set, subdomains are ignored, only prefixes work
        # Domain defaults to empty string, so this will always be true
        if domain == "":
            warning_msg = (
                "[WARNING] No domain specified!\n"
                "Subdomains in RouteGroups will be IGNORED.\n"
                "All routes will be accessible regardless of Host header.\n"
                "Prefixes will still work as expected.\n"
                "To enable subdomain routing, set the 'domain' parameter (e.g., domain='example.com')."
            )
            log.warning(warning_msg)
            self.domain = ""
            self.domainless_mode = True
        else:
            # Validate domain format (basic check)
            if not domain.replace(".", "").replace("-", "").isalnum():
                raise ValueError(f"Invalid domain format: {domain}. Domain must be alphanumeric with dots and hyphens only.")
            self.domain = domain
            self.domainless_mode = False

        # Performance monitoring
        self.route_count = 0
        self.max_nesting_depth = 0
        self.registered_domains: set[str] = set()

    def set_config(self, config: dict[str, Any]) -> None:
        self.config = config

    def _add_route(self, route: Route, subdomain: str = "", parent_middlewares: Optional[list[Middleware]] = None) -> None:
        """Internal method to add single routes to the application.

        Args:
            route (Route): The actual route object
            subdomain (str): The full domain the route should be available for (e.g., "dev.api.example.com").
        """
        # In domainless mode, always use the empty string key
        key = "" if getattr(self, "domainless_mode", False) else subdomain
        if key not in self.routes:
            self.routes[key] = {}
        self.route_count += 1
        self.registered_domains.add(key)

        # Build hierarchical middleware structure
        middleware_levels = []

        # Add parent middlewares first (if any)
        if parent_middlewares:
            parent_before = []
            parent_after = []
            for middleware in parent_middlewares:
                if middleware.attach_to == "request":
                    parent_before.append(middleware)
                elif middleware.attach_to == "response":
                    parent_after.append(middleware)

            # Sort parent middlewares by priority
            parent_before.sort(key=lambda m: m.priority)  # type: ignore[reportUnknownMemberType]
            parent_after.sort(key=lambda m: m.priority)  # type: ignore[reportUnknownMemberType]

            middleware_levels.append(
                {
                    "before": parent_before,
                    "after": parent_after,
                }
            )

        # Add route-specific middlewares
        route_before = []
        route_after = []
        for middleware in route.middlewares:
            if middleware.attach_to == "request":
                route_before.append(middleware)
            elif middleware.attach_to == "response":
                route_after.append(middleware)

        # Sort route middlewares by priority
        route_before.sort(key=lambda m: m.priority)  # type: ignore[reportUnknownMemberType]
        route_after.sort(key=lambda m: m.priority)  # type: ignore[reportUnknownMemberType]

        middleware_levels.append({"before": route_before, "after": route_after})

        # Create route config with hierarchical middleware structure
        route_config = RouteConfig(
            handler=route.endpoint,
            middleware={"levels": middleware_levels},
            regex={"paths": [route._rx]} if hasattr(route, "_rx") else None,  # type: ignore[reportGeneralTypeIssues]
        )

        # Use route path as key for direct lookup
        self.routes[key][route.path] = route_config

    def add_routes(self, routes: Sequence[Union[Route, RouteGroup]]) -> None:
        for r in routes:
            if isinstance(r, Route):
                r.compile_pattern()
                # Use the actual domain for individual routes, just like RouteGroups
                subdomain = self.domain if not getattr(self, "domainless_mode", False) else ""
                self._add_route(route=r, subdomain=subdomain)
            elif isinstance(r, RouteGroup):  # type: ignore[reportUnnecessaryIsInstance]
                self._add_route_group(r, parent_subdomain="", parent_middlewares=[], nesting_depth=0)
            else:
                raise NotImplementedError

    def _add_route_group(
        self,
        route_group: RouteGroup,
        parent_subdomain: str = "",
        parent_prefix: str = "",
        parent_middlewares: Optional[list[Middleware]] = None,
        nesting_depth: int = 0,
    ) -> None:
        """Recursively add RouteGroup and its nested RouteGroups."""
        # Validate RouteGroup configuration
        self._validate_route_group(route_group)

        # Track nesting depth for performance monitoring
        self.max_nesting_depth = max(self.max_nesting_depth, nesting_depth)

        # Build the full subdomain path for this group
        current_subdomain = route_group.subdomain
        if parent_subdomain and current_subdomain:
            full_subdomain = f"{current_subdomain}.{parent_subdomain}"
        elif parent_subdomain:
            full_subdomain = parent_subdomain
        elif current_subdomain:
            full_subdomain = current_subdomain
        else:
            full_subdomain = ""

        # Build the full prefix path for this group with validation
        full_prefix = self._build_prefix_path(parent_prefix, route_group.prefix)

        # Process all routes in this group
        for r in route_group.routes:
            if isinstance(r, RouteGroup):
                # Nested RouteGroup - recurse with updated parent subdomain and prefix
                # Pass parent middlewares as a separate parameter to maintain hierarchy
                self._add_route_group(
                    r, parent_subdomain=full_subdomain, parent_prefix=full_prefix, parent_middlewares=route_group.middlewares, nesting_depth=nesting_depth + 1
                )
            else:
                # Regular Route - add with full subdomain path and accumulated prefix
                r.path = f"{full_prefix}{r.path}"  # Convert route.path to full path (accumulated prefix AND route.path)
                r.compile_pattern()

                # Build full domain path for dictionary lookup
                if getattr(self, "domainless_mode", False):
                    full_domain = ""
                else:
                    full_domain = f"{full_subdomain}.{self.domain}" if full_subdomain else self.domain

                # Check for route conflicts before adding
                self._check_route_conflicts(r, full_domain)

                # Pass parent middlewares to maintain hierarchy
                self._add_route(route=r, subdomain=full_domain, parent_middlewares=route_group.middlewares)

    def _validate_route_group(self, route_group: RouteGroup) -> None:
        """Validate RouteGroup configuration."""
        # Validate subdomain format
        if route_group.subdomain and not route_group.subdomain.replace(".", "").replace("-", "").isalnum():
            raise ValueError(f"Invalid subdomain format: {route_group.subdomain}. Must be alphanumeric with dots and hyphens only.")

        # Validate prefix format
        if route_group.prefix:
            if not route_group.prefix.startswith("/"):
                raise ValueError(f"Invalid prefix format: {route_group.prefix}. Must start with '/'.")
            if "//" in route_group.prefix:
                raise ValueError(f"Invalid prefix format: {route_group.prefix}. Cannot contain consecutive slashes.")

    def _build_prefix_path(self, parent_prefix: str, current_prefix: str) -> str:
        """Build and validate accumulated prefix path."""
        if parent_prefix and current_prefix:
            full_prefix = f"{parent_prefix}{current_prefix}"
        elif parent_prefix:
            full_prefix = parent_prefix
        elif current_prefix:
            full_prefix = current_prefix
        else:
            full_prefix = ""

        # Validate final prefix
        if full_prefix and not full_prefix.startswith("/"):
            raise ValueError(f"Invalid accumulated prefix: {full_prefix}. Must start with '/'.")

        return full_prefix

    def _check_route_conflicts(self, route: Route, domain: str) -> None:
        """Check for route conflicts within the same domain."""
        existing_routes = self.routes.get(domain, {})
        if route.path in existing_routes:
            raise ValueError(f"Route conflict detected: {route.path} already exists in domain {domain}")

    def _validate_domain_access(self, host_domain: str) -> bool:
        """Validate if the host domain is allowed to access routes."""
        # Check if domain matches our configured domain or any subdomain
        if not self.domain:
            return True  # No domain restriction

        # Allow exact domain match
        if host_domain == self.domain:
            return True

        # Allow subdomains of our domain
        if host_domain.endswith(f".{self.domain}"):
            return True

        return False

    def get_performance_stats(self) -> dict[str, Any]:
        """Get performance statistics for the application."""
        return {
            "total_routes": self.route_count,
            "registered_domains": len(self.registered_domains),
            "max_nesting_depth": self.max_nesting_depth,
            "domain_list": list(self.registered_domains),
            "memory_usage": {"routes_dict_size": len(self.routes), "total_route_configs": sum(len(configs) for configs in self.routes.values())},
        }

    async def handle_lifespan_request(self, scope: ASGIScope, receive: ASGIReceive, send: ASGISend) -> None:
        # initialize_scheduler for cronjobs
        assert scope["type"] == "lifespan"
        message = await receive()
        assert message["type"] == AsgiEventType.LIFESPAN_STARTUP
        app = scope.get("app")

        started = False
        try:
            # async with self.lifespan(app) as state:
            self.lifespan.app = app
            async with self.lifespan as state:
                if state is not None:
                    scope["state"].update(state)
                await send({"type": AsgiEventType.LIFESPAN_STARTUP_COMPLETE})
                started = True
                message = await receive()
                assert message["type"] == AsgiEventType.LIFESPAN_SHUTDOWN

        except BaseException:
            event_type = AsgiEventType.LIFESPAN_SHUTDOWN_FAILED if started else AsgiEventType.LIFESPAN_STARTUP_FAILED
            await send({"type": event_type, "message": traceback.format_exc()})
            raise

        await send({"type": AsgiEventType.LIFESPAN_SHUTDOWN_COMPLETE})

        """
        while True:
            message = await receive()
            print(f"Got message:", message)

            if message["type"] == "lifespan.startup":
                # scope["state"]["GlobalKey"] = "Value"
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                break
        """

    async def handle_http_request(self, scope: ASGIScope, receive: ASGIReceive, send: ASGISend) -> None:
        request = Request(scope, receive)
        request_path = request.path.encode()
        host_domain = request.host.split("/")[0] if "/" in request.host else request.host
        if not self._validate_domain_access(host_domain):
            response = Response(body="Forbidden", status=403)
            await response(send)
            return
        # In domainless mode, always use the empty string key for lookup
        key = "" if getattr(self, "domainless_mode", False) else host_domain
        domain_routes = self.routes.get(key, {})
        matched_route = None
        route_params = None
        for route_path, route_config in domain_routes.items():
            route = route_config.get("route", None)
            if route and hasattr(route, "match"):
                route_match = route.match(request_path)
                if route_match:
                    matched_route = route_config
                    route_params = route_match.params
                    break
            else:
                if route_path == request.path:
                    matched_route = route_config
                    break
        if not matched_route:
            response = Response(body="Not Found", status=404)
            await response(send)
            return
        handler = matched_route["handler"]
        middleware_levels = matched_route["middleware"]["levels"]
        for level in middleware_levels:
            for m in level["before"]:
                response = await m.intercept(request)  # type: ignore[reportUnknownMemberType]
                if response is not None:
                    await response(send)
                    return
        if route_params:
            response = await handler(request, **route_params)
        else:
            response = await handler(request)
        for level in reversed(middleware_levels):
            for m in level["after"]:
                modified_response = await m.intercept(request, response)  # type: ignore[reportUnknownMemberType]
                if modified_response is not None:
                    response = modified_response
        await response(send)

    async def handle_websocket_request(self, scope: ASGIScope, receive: ASGIReceive, send: ASGISend) -> None:
        """Handle WebSocket requests following the same pattern as HTTP requests."""
        request_path = scope["path"].encode()
        host_domain = ""

        # Extract host from headers
        headers = dict(scope.get("headers", []))
        host_header = headers.get(b"host", b"").decode()
        if host_header:
            host_domain = host_header.split("/")[0] if "/" in host_header else host_header

        if not self._validate_domain_access(host_domain):
            await send({"type": "websocket.close", "code": 1008, "reason": "Forbidden"})
            return

        # In domainless mode, always use the empty string key for lookup
        key = "" if getattr(self, "domainless_mode", False) else host_domain
        domain_routes = self.routes.get(key, {})
        matched_route = None
        route_params = None

        for route_path, route_config in domain_routes.items():
            route = route_config.get("route", None)
            if route and hasattr(route, "match"):
                route_match = route.match(request_path)
                if route_match:
                    matched_route = route_config
                    route_params = route_match.params
                    break
            else:
                if route_path == scope["path"]:
                    matched_route = route_config
                    break

        if not matched_route:
            await send({"type": "websocket.close", "code": 1008, "reason": "Not Found"})
            return

        handler = matched_route["handler"]
        middleware_levels = matched_route["middleware"]["levels"]

        # Create a mock request for middleware compatibility
        request = Request(scope, receive)

        # Run request middleware
        for level in middleware_levels:
            for m in level["before"]:
                response = await m.intercept(request)  # type: ignore[reportUnknownMemberType]
                if response is not None:
                    # Middleware decided to close the connection
                    await send({"type": "websocket.close", "code": 1008, "reason": "Middleware rejected"})
                    return

        # Call the WebSocket handler to get the response
        if route_params:
            response = await handler(request, **route_params)
        else:
            response = await handler(request)

        # Run after middleware (same as HTTP)
        for level in reversed(middleware_levels):
            for m in level["after"]:
                modified_response = await m.intercept(request, response)  # type: ignore[reportUnknownMemberType]
                if modified_response is not None:
                    response = modified_response

        # Send the WebSocket response (same pattern as HTTP)
        await response(send)

    async def __call__(self, scope: ASGIScope, receive: ASGIReceive, send: ASGISend) -> None:
        # Inject ourselves into the chain for later convenience
        scope["app"] = self

        # Check scope type and handle accordingly...
        if scope["type"] == "lifespan":
            log.debug("Handling lifespan stuff...")
            await self.handle_lifespan_request(scope, receive, send)
        elif scope["type"] == "http":
            await self.handle_http_request(scope, receive, send)
        elif scope["type"] == "websocket":
            await self.handle_websocket_request(scope, receive, send)
        else:
            raise NotImplementedError

    # FIXME: should this also be async?
    def run(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        workers: int = 4,
        tls_key: Optional[str] = None,
        tls_cert: Optional[str] = None,
        tls_password: Optional[str] = None,
    ) -> None:
        # Dynamically get system information
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        platform_info = platform.platform()
        arch = platform.machine()
        platform_str = f"{platform_info}-{arch}"
        try:
            future_version = version("future")
        except PackageNotFoundError:
            future_version = "not installed"
        except Exception:
            future_version = "unknown"

        debug = self.config.get("APP_DEBUG", False) if self.config else False

        # ASCII-art "F" made with ✨ sparkles
        left = Text()
        left.append("     ✨✨✨✨✨      \n", style="bold yellow")
        left.append("     ✨              \n", style="yellow")
        left.append("     ✨✨✨✨        \n", style="bold yellow")
        left.append("     ✨              \n", style="yellow")
        left.append("     ✨              \n", style="yellow")
        left.append("                     \n", style="yellow")
        left.append(" ASGI based Web API    ", style="bold green")

        # Right info column
        right = Table.grid(padding=(0, 1))
        right.add_column(justify="left", no_wrap=True)
        right.add_column(justify="left")
        right.add_row("[red]app:[/]", f"{ self.config['APP_NAME'] }")  # APP_NAME  # TODO: add APP_DOMAIN
        right.add_row("[red]mode:[/]", f"{ "debug" if debug else "prod"} / { workers } worker(s)")  # FIXME
        right.add_row("[red]domain:[/]", f"{ self.config["APP_DOMAIN"] if self.config else "N/A" }")  # FIXME
        right.add_row("[red]server:[/]", "future, HTTP/1.1")
        right.add_row("[red]python:[/]", f"{ python_version }")
        right.add_row("[red]platform:[/]", f"{ platform_str }")
        right.add_row("[red]packages[/]:", f"future=={ future_version }")
        # right.add_row("[red]docs:[/]", f"http://localhost:{port}/docs")

        # Combined layout
        layout = Table.grid(expand=False)
        layout.add_column(ratio=1)
        layout.add_column(ratio=2)
        layout.add_row(left, right)

        main_panel = Panel(layout, box=ROUNDED, padding=(1, 2), expand=False)
        console = Console()
        # console.print(title_panel)
        console.print(main_panel)

        uvicorn.run(
            app="__main__:app",  # "app.main.app"
            host=host,
            port=port,
            workers=workers,
            reload=debug,
            ssl_keyfile=tls_key,
            ssl_certfile=tls_cert,
            ssl_keyfile_password=tls_password,
            timeout_graceful_shutdown=3,
            log_level="info",
            lifespan="on",
        )
