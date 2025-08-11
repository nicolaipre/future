"""
Optimized Future Application with Fast Router
High-performance version of the Future framework.
"""

import asyncio
import logging
from collections.abc import Sequence
from typing import Any, Optional, Union

from future.application import Future
from future.controllers import DebugController, OpenAPIController, WebSocketController, WelcomeController
from future.lifespan import Lifespan
from future.middleware import Middleware
from future.requests import Request
from future.responses import JSONResponse, PlainTextResponse
from future.routing import Route, RouteGroup
from future.scheduler import Task, Unit, check_dns, check_system_uptime
from future.settings import APP_DOMAIN
from future.types import AsgiEventType, ASGIReceive, ASGIScope, ASGISend, RouteConfig

# Try to import the fast router, fallback to pure Python
try:
    from performance.fast_router import FastRouter
    FAST_ROUTER_AVAILABLE = True
except ImportError:
    from performance.fast_router import FastRouterFallback as FastRouter
    FAST_ROUTER_AVAILABLE = False
    log.warning("Fast router not available, using fallback")


class OptimizedFuture:
    def __init__(self, lifespan: Any, config: dict[str, Any] | None = None) -> None:
        self.lifespan = lifespan
        self.config = config or {}
        
        # Use fast router for route matching
        self.fast_router = FastRouter()
        self.routes_by_domain: dict[str, FastRouter] = {}
        
        domain = self.config.get("APP_DOMAIN", "")
        
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
            if not domain.replace(".", "").replace("-", "").isalnum():
                raise ValueError(f"Invalid domain format: {domain}. Domain must be alphanumeric with dots and hyphens only.")
            self.domain = domain
            self.domainless_mode = False

        # Performance monitoring
        self.route_count = 0
        self.max_nesting_depth = 0
        self.registered_domains: set[str] = set()
        
        # Optimization: Cache for domain validation
        self._domain_cache: dict[str, bool] = {}
        
        # Precomputed middleware chains
        self._middleware_chains: dict[str, dict] = {}

    def set_config(self, config: dict[str, Any]) -> None:
        self.config = config

    def _get_router_for_domain(self, domain: str) -> FastRouter:
        """Get or create a fast router for a specific domain."""
        if domain not in self.routes_by_domain:
            self.routes_by_domain[domain] = FastRouter()
        return self.routes_by_domain[domain]

    def _add_route(self, route: Route, subdomain: str = "", parent_middlewares: Optional[list[Middleware]] = None) -> None:
        """Add a route to the fast router."""
        key = "" if getattr(self, "domainless_mode", False) else subdomain
        router = self._get_router_for_domain(key)
        
        # Precompute middleware chain
        middleware_chain = self._build_middleware_chain(route, parent_middlewares)
        
        # Add route to fast router
        router.add_route(route.path, {
            'handler': route.endpoint,
            'middleware': middleware_chain
        })
        
        self.route_count += 1
        self.registered_domains.add(key)

    def _build_middleware_chain(self, route: Route, parent_middlewares: Optional[list[Middleware]] = None) -> dict:
        """Precompute the complete middleware chain for a route."""
        before_middleware = []
        after_middleware = []
        
        # Add parent middlewares
        if parent_middlewares:
            for middleware in parent_middlewares:
                if middleware.attach_to == "request":
                    before_middleware.append(middleware)
                elif middleware.attach_to == "response":
                    after_middleware.append(middleware)
        
        # Add route middlewares
        for middleware in route.middlewares:
            if middleware.attach_to == "request":
                before_middleware.append(middleware)
            elif middleware.attach_to == "response":
                after_middleware.append(middleware)
        
        # Sort by priority
        before_middleware.sort(key=lambda m: m.priority)
        after_middleware.sort(key=lambda m: m.priority)
        
        return {
            'before': before_middleware,
            'after': after_middleware
        }

    def add_routes(self, routes: Sequence[Union[Route, RouteGroup]]) -> None:
        for r in routes:
            if isinstance(r, Route):
                r.compile_pattern()
                subdomain = self.domain if not getattr(self, "domainless_mode", False) else ""
                self._add_route(route=r, subdomain=subdomain)
            elif isinstance(r, RouteGroup):
                self._add_route_group(r, parent_subdomain="", parent_middlewares=[], nesting_depth=0)
            else:
                raise NotImplementedError

    def _add_route_group(self, route_group: RouteGroup, parent_subdomain: str = "", parent_prefix: str = "", parent_middlewares: Optional[list[Middleware]] = None, nesting_depth: int = 0) -> None:
        """Recursively add RouteGroup and its nested RouteGroups."""
        self._validate_route_group(route_group)
        self.max_nesting_depth = max(self.max_nesting_depth, nesting_depth)

        current_subdomain = route_group.subdomain
        if parent_subdomain and current_subdomain:
            full_subdomain = f"{current_subdomain}.{parent_subdomain}"
        elif parent_subdomain:
            full_subdomain = parent_subdomain
        elif current_subdomain:
            full_subdomain = current_subdomain
        else:
            full_subdomain = ""

        full_prefix = self._build_prefix_path(parent_prefix, route_group.prefix)

        for r in route_group.routes:
            if isinstance(r, RouteGroup):
                self._add_route_group(
                    r, parent_subdomain=full_subdomain, parent_prefix=full_prefix, 
                    parent_middlewares=route_group.middlewares, nesting_depth=nesting_depth + 1
                )
            else:
                r.path = f"{full_prefix}{r.path}"
                r.compile_pattern()

                if getattr(self, "domainless_mode", False):
                    full_domain = ""
                else:
                    full_domain = f"{full_subdomain}.{self.domain}" if full_subdomain else self.domain

                self._check_route_conflicts(r, full_domain)
                self._add_route(route=r, subdomain=full_domain, parent_middlewares=route_group.middlewares)

    def _validate_route_group(self, route_group: RouteGroup) -> None:
        if not hasattr(route_group, "routes"):
            raise ValueError("RouteGroup must have a 'routes' attribute")

    def _build_prefix_path(self, parent_prefix: str, current_prefix: str) -> str:
        if not parent_prefix and not current_prefix:
            return ""
        elif not parent_prefix:
            return current_prefix
        elif not current_prefix:
            return parent_prefix
        else:
            return f"{parent_prefix.rstrip('/')}/{current_prefix.lstrip('/')}"

    def _check_route_conflicts(self, route: Route, domain: str) -> None:
        router = self._get_router_for_domain(domain)
        # Note: FastRouter doesn't have built-in conflict detection
        # This would need to be implemented if needed

    def _validate_domain_access(self, host_domain: str) -> bool:
        if host_domain in self._domain_cache:
            return self._domain_cache[host_domain]
        
        if not self.domain:
            self._domain_cache[host_domain] = True
            return True

        if host_domain == self.domain:
            self._domain_cache[host_domain] = True
            return True

        if host_domain.endswith(f".{self.domain}"):
            self._domain_cache[host_domain] = True
            return True

        self._domain_cache[host_domain] = False
        return False

    def get_performance_stats(self) -> dict[str, Any]:
        return {
            "total_routes": self.route_count,
            "registered_domains": len(self.registered_domains),
            "max_nesting_depth": self.max_nesting_depth,
            "domain_list": list(self.registered_domains),
            "fast_router_available": FAST_ROUTER_AVAILABLE,
            "domain_cache_size": len(self._domain_cache),
        }

    async def handle_http_request(self, scope: ASGIScope, receive: ASGIReceive, send: ASGISend) -> None:
        """Handle HTTP requests with optimized routing."""
        try:
            # Extract request details
            method = scope.get("method", "GET")
            path = scope.get("path", "/")
            headers = scope.get("headers", [])
            
            # Find host header
            host = "example.com"  # Default for testing
            for name, value in headers:
                if name == b"host":
                    host = value.decode("utf-8").split(":")[0]
                    break
            
            # Validate domain access
            if not self._validate_domain_access(host):
                await send({
                    "type": "http.response.start",
                    "status": 403,
                    "headers": [(b"content-type", b"text/plain")],
                })
                await send({
                    "type": "http.response.body",
                    "body": b"Forbidden",
                })
                return
            
            # Get router for this domain
            domain_key = "" if getattr(self, "domainless_mode", False) else host
            router = self._get_router_for_domain(domain_key)
            
            # Match route using fast router
            match_result = router.match(path.encode('utf-8'))
            
            if not match_result:
                # Route not found
                await send({
                    "type": "http.response.start",
                    "status": 404,
                    "headers": [(b"content-type", b"text/plain")],
                })
                await send({
                    "type": "http.response.body",
                    "body": b"Not Found",
                })
                return
            
            # Extract handler and middleware
            handler = match_result['handler']
            middleware_chain = match_result['middleware']
            params = match_result['params']
            
            # Create request object
            request = Request(scope, receive, send)
            request.params = params
            
            # Execute before middleware
            for middleware in middleware_chain['before']:
                response = middleware.intercept(request)
                if response is not None:
                    await response(scope, receive, send)
                    return
            
            # Execute handler
            if asyncio.iscoroutinefunction(handler):
                response = await handler(request)
            else:
                response = handler(request)
            
            # Execute after middleware
            for middleware in middleware_chain['after']:
                response = middleware.intercept(request, response)
                if response is not None:
                    break
            
            # Send response
            if response is None:
                response = PlainTextResponse("No response")
            
            await response(scope, receive, send)
            
        except Exception as e:
            log.error(f"Error handling request: {e}")
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [(b"content-type", b"text/plain")],
            })
            await send({
                "type": "http.response.body",
                "body": b"Internal Server Error",
            })

    async def handle_websocket_request(self, scope: ASGIScope, receive: ASGIReceive, send: ASGISend) -> None:
        """Handle WebSocket requests with optimized routing."""
        try:
            # Extract request details
            path = scope.get("path", "/")
            headers = scope.get("headers", [])
            
            # Find host header
            host = "example.com"  # Default for testing
            for name, value in headers:
                if name == b"host":
                    host = value.decode("utf-8").split(":")[0]
                    break
            
            # Validate domain access
            if not self._validate_domain_access(host):
                await send({
                    "type": "websocket.close",
                    "code": 1008,
                    "reason": "Forbidden",
                })
                return
            
            # Get router for this domain
            domain_key = "" if getattr(self, "domainless_mode", False) else host
            router = self._get_router_for_domain(domain_key)
            
            # Match route using fast router
            match_result = router.match(path.encode('utf-8'))
            
            if not match_result:
                await send({
                    "type": "websocket.close",
                    "code": 1008,
                    "reason": "Route not found",
                })
                return
            
            # Extract handler
            handler = match_result['handler']
            params = match_result['params']
            
            # Create request object
            request = Request(scope, receive, send)
            request.params = params
            
            # Execute handler
            if asyncio.iscoroutinefunction(handler):
                await handler(request)
            else:
                handler(request)
                
        except Exception as e:
            log.error(f"Error handling WebSocket: {e}")
            await send({
                "type": "websocket.close",
                "code": 1011,
                "reason": "Internal error",
            })

    async def __call__(self, scope: ASGIScope, receive: ASGIReceive, send: ASGISend) -> None:
        """ASGI application entry point."""
        event_type = scope.get("type")
        
        if event_type == "http":
            await self.handle_http_request(scope, receive, send)
        elif event_type == "websocket":
            await self.handle_websocket_request(scope, receive, send)
        else:
            await send({
                "type": "http.response.start",
                "status": 400,
                "headers": [(b"content-type", b"text/plain")],
            })
            await send({
                "type": "http.response.body",
                "body": b"Unsupported protocol",
            })

    def run(self, host: str = "127.0.0.1", port: int = 8000, workers: int = 4, tls_key: Optional[str] = None, tls_cert: Optional[str] = None, tls_password: Optional[str] = None, access_log: bool = True) -> None:
        """Run the optimized application."""
        import uvicorn
        
        # Configure logging
        if not access_log:
            logging.getLogger("uvicorn.access").setLevel(logging.CRITICAL)
        
        # Run with uvicorn
        uvicorn.run(
            self,
            host=host,
            port=port,
            workers=workers,
            ssl_keyfile=tls_key,
            ssl_certfile=tls_cert,
            ssl_password=tls_password,
            access_log=access_log,
        )

# Initialize logging
log = logging.getLogger(__name__) 