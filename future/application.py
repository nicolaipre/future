from future.logger import setup_logging
from future.request import Request
from future.response import Response
from future.routing import Route, RouteGroup
from future.middleware import Middleware
from future.types import ASGIScope, ASGIReceive, ASGISend
from typing import TypedDict, Callable, Optional
from rich.console import Console
from re import Pattern
import logging
import uvicorn

setup_logging()


class RegexConfig(TypedDict):
    paths: list[Pattern]


class EndpointConfig(TypedDict):
    endpoint: Callable
    middleware_before: list[Middleware]
    middleware_after: list[Middleware]
    regex: Optional[RegexConfig]


class Future:
    def __init__(self, name: str = "Future", debug: bool = False, domain: str = ""):
        self.debug = debug  # Implement: https://asgi.readthedocs.io/en/stable/extensions.html#debug
        self.domain = domain
        self.logger = logging.getLogger(name)
        self.routes: dict[str, dict[str, EndpointConfig]] = {}

        # self.middleware_manager = MiddlewareManager(self.dispatch)
        # Add openAPI after all rotues are added with add_routes()
        # self._add_to_openapi(path, subdomain, methods, summary)

    """
    def _add_to_openapi(self, path: str, subdomain: str, methods: list[str], summary: str, description: str = "Successful Response"):
        if subdomain:
            full_path = f"/{subdomain}.{path.lstrip('/')}"
        else:
            full_path = path
        if full_path not in self.openapi_schema["paths"]:
            self.openapi_schema["paths"][full_path] = {}
        for method in methods:
            self.openapi_schema["paths"][full_path][method.lower()] = {
                "summary": summary,
                "responses": {"200": {"description": description}},
            }
    """

    def _add_route(
        self,
        path: str,
        endpoint: Callable,
        subdomain: str = None,
        methods: list[str] = ["GET"],
        name: str = "",
        middlewares: list[Middleware] = [],
    ):
        """Internal method to add single routes to the application.

        Args:
            path (str): URL path
            endpoint (Callable): Controller method
            subdomain (str, optional): The subdomain the route should (only) be available for. Defaults to None (all).
            methods (list[str], optional): HTTP method. Defaults to ["GET"].
            name (str, optional): A name for the route. Defaults to "".
            middlewares (Optional[list[Middleware]], optional): List of middlewares that the route should be protected by. Defaults to None.
        """

        if subdomain not in self.routes:
            self.routes[subdomain] = {}

        # TODO: do we want to be kind here and add a fail-safe that notifies the
        # user and exits if the user attempts to overwrite an existing entry?

        if path not in self.routes[subdomain]:
            self.routes[subdomain][path] = {}

        # Iterate over middlewares and put these in their respective before/after dicts
        before = []
        after = []
        for middleware in middlewares:
            if middleware.attach_to == "request":
                before.append(middleware)
            elif middleware.attach_to == "response":
                after.append(middleware)

        # Sort based on middleware priority # TODO: Check that the order is correct
        before.sort(key=lambda middleware: middleware.priority)
        after.sort(key=lambda middleware: middleware.priority)

        self.routes[subdomain][path]["endpoint"] = endpoint
        self.routes[subdomain][path]["middleware_before"] = before
        self.routes[subdomain][path]["middleware_after"] = after

        # TODO: Forbedre dicten over til nock sitt forslag:
        """
        {
            "<endpoint>": {
                "handler": "<route handler callable>",
                "middleware": {
                    "before_handlers": ["< sorted handlers callable>"] 
                    "after_handlers": ["< sorted handlers callable>"] 
                },
                "regex?": {
                    "paths": ["<compiled regex>", ...]
                }
            }
        }
        """

    def add_routes(self, routes: list[Route, RouteGroup]):
        for x in routes:
            if isinstance(x, Route):
                self._add_route(
                    path=x.path,
                    endpoint=x.endpoint,
                    subdomain=None,
                    middlewares=x.middlewares,
                )

            elif isinstance(x, RouteGroup):
                for route in x.routes:
                    full_path = f"{x.prefix}{route.path}"

                    # Combine route-specific middlewares with group middlewares
                    combined_middlewares = x.middlewares + route.middlewares

                    # Finally, add route with all middlewares
                    self._add_route(
                        path=full_path,
                        endpoint=route.endpoint,
                        subdomain=x.subdomain,
                        middlewares=combined_middlewares,
                    )

            else:
                raise NotImplementedError

    async def __call__(self, scope: ASGIScope, receive: ASGIReceive, send: ASGISend):
        # assert scope["type"] == "http"
        # path = scope["path"]
        # host = dict(scope["headers"]).get(b"host", b"").decode().split(":")[0]
        request = Request(scope, receive)

        # FIXME: Be aware of subdomain attacks! api.api.api.example.com will now
        # match: api.example.com, which we do not want to happen:
        # curl api.api.api.example.com:8000
        # curl api.nock.example.com:8000

        # TODO - nock: Direct match self.domain med subdomain på host-feltet

        host_header_parts = request.host.split(".") if request.host else []
        subdomain = host_header_parts[0] if len(host_header_parts) > 2 else ""
        print("Subdomain:", subdomain)
        # FIXME: Use regex for this lol
        domain = (
            host_header_parts[-2] + "." + host_header_parts[-1]
            if len(host_header_parts) > 1
            else ""
        )
        print("Domain:", domain)

        # Host header not matching domain, and NOT in debug mode
        if domain != self.domain and not self.debug:
            return Response(body=b"Not Found", status=404)

        path = request.path
        print("Path:", path)

        """
        # Custom openapi path
        if path == "/openapi.json":
            await self.serve_openapi(send)
            return
        """

        subdomain_routes = self.routes.get(subdomain, {})
        print("Sub routes:", subdomain_routes)

        endpoint = subdomain_routes.get(path).get("endpoint", None)  # FIXME: bug
        print("Endpoint:", endpoint)

        if endpoint is None:
            return Response(body=b"Not Found", status=404)

        # Ok, the endpoint exists and has a match. Check if it has any before or after middlewares
        middleware_before = subdomain_routes.get(path).get("middleware_before", None)
        middleware_after = subdomain_routes.get(path).get("middleware_after", None)
        print("middleware_before:", middleware_before)
        print("middleware_after:", middleware_after)

        # Process request middlewares (before)
        for b_middleware in middleware_before:
            response = b_middleware.intercept(request)
            if response is not None:
                # return response
                await response(send)
                return

        # If no middleware intercepts, call the endpoint with the request data
        response = await endpoint(
            request
        )  # TODO: THIS IS WHERE WE PASS VARIABLES TO CONTROLLER

        # Process response middlewares (after)
        for a_middleware in middleware_after:
            modified_response = a_middleware.intercept(request, response)
            if modified_response is not None:
                response = modified_response

        await response(send)


    def run(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        workers: int = 4,
        tls_key: str = None,
        tls_cert: str = None,
        tls_password: str = None,
    ) -> None:
        console = Console()
        
        # Slight rip from Blacksheep (sorry, it was too cool not to...)
        console.rule("[bold yellow]Running for local development", align="left")
        console.print(f"[bold yellow]Visit http://localhost:{port}/docs")
        uvicorn.run(
            app="__main__:app",  # other: "app.main:app",
            host=host,
            port=port,
            workers=workers,
            reload=self.debug,
            ssl_keyfile=tls_key,
            ssl_certfile=tls_cert,
            ssl_keyfile_password=tls_password,
        )

    """
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=port,
        lifespan="on",
        log_level="info",
        reload=True,
    )
    """
