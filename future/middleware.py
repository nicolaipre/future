import random

from typing import Optional

from future.requests import Request
from future.responses import EmptyResponse, Response


# CSRF: https://github.com/simonw/asgi-csrf
# CSP: Content Security Policy


# README - a note on the use of middlewares:
# if a middleware does not RETURN or hit any EXCEPTIONS, it means it passes (all checks ok)
# if it however RETURNS or hits an EXCEPTION, the middleware check will deny further processing of the request.


class Middleware:
    name: Optional[str] = None
    apply: bool = True
    priority: int = 0
    attach_to: str = "request"

    def intercept(request: Request, response: Optional[Response] = None) -> Optional[Response]:  # type: ignore[reportAttributeAccessIssue,reportSelfClsParameterName]
        """Intercept the request/response.

        To allow the request to continue: don't return anything (fall through)
        To interrupt the request: return any Response (including None)
        """
        # Don't return anything to allow continuation
        return None


class TestMiddlewareRequest(Middleware):
    name = "testRequestMiddleware"
    attach_to = "request"

    def intercept(request: Request, response: Optional[Response] = None) -> Optional[Response]:  # type: ignore[reportAttributeAccessIssue,reportSelfClsParameterName]
        # Example: interrupt if a certain header is present
        # Inject user info into the request context
        # user_info = get_user_info(request.headers...)
        # if user_info:
        # request.context["user_info"] = user_info
        if request.headers.get("x-interrupt") == "1":
            return Response(body=b"Request intercepted!")
        # Don't return anything to allow continuation
        return None


class TestMiddlewareResponse(Middleware):
    name = "testResponseMiddleware"
    attach_to = "response"

    def intercept(request: Request, response: Optional[Response] = None) -> Optional[Response]:  # type: ignore[reportAttributeAccessIssue,reportSelfClsParameterName]
        # Example: interrupt if a certain header is present
        # Inject user info into the response context
        # user_info = get_user_info(request.headers...)
        # if user_info:
        # response.context["user_info"] = user_info
        if request.headers.get("x-interrupt-response") == "1":
            return Response(body=b"Response intercepted!")
        # Don't return anything to allow continuation
        return None


class ResponseCodeConfuser(Middleware):
    name = "response code confuser"
    attach_to = "response"

    def intercept(request: Request, response: Optional[Response] = None) -> Optional[Response]:  # type: ignore[reportAttributeAccessIssue,reportSelfClsParameterName]
        response_codes = [
            100,
            101,
            102,
            103,
            200,
            201,
            202,
            203,
            204,
            205,
            206,
            207,
            208,
            226,
            300,
            301,
            302,
            303,
            304,
            305,
            306,
            307,
            308,
            400,
            401,
            402,
            403,
            404,
            405,
            406,
            407,
            408,
            409,
            410,
            411,
            412,
            413,
            414,
            415,
            416,
            417,
            418,
            421,
            422,
            423,
            424,
            425,
            426,
            428,
            429,
            431,
            451,
            500,
            501,
            502,
            503,
            504,
            505,
            506,
            507,
            508,
            510,
            511,
        ]
        # Interrupt if user-agent is curl
        if "curl" in request.headers.get("user-agent", ""):
            random_code = random.choice(response_codes)
            return EmptyResponse(status=random_code)
        # Don't return anything to allow continuation
        return None


class RateLimitMiddleware(Middleware):
    pass


class CSRFMiddleware(Middleware):
    pass


class WebServerConfuser(Middleware):
    pass


class BruteforcePrevention(Middleware):
    # if login_attempt == 1 and password == correct
    # return "Invalid username or password"
    pass


class SQLiConfuser(Middleware):
    pass


class HTAccessConfuser(Middleware):
    pass


class HeaderConfuser(Middleware):
    pass


class GZipMiddleware(Middleware):
    # from starlette.applications import Starlette
    # from starlette.middleware import Middleware
    # from starlette.middleware.gzip import GZipMiddleware

    # routes = ...

    # middleware = [
    #    Middleware(GZipMiddleware, minimum_size=1000)
    # ]

    # app = Starlette(routes=routes, middleware=middleware)
    pass


class CORSMiddleware(Middleware):
    # from starlette.applications import Starlette
    # from starlette.middleware import Middleware
    # from starlette.middleware.cors import CORSMiddleware

    # middleware = [
    #    Middleware(CORSMiddleware, allow_origins=['*'])
    # ]

    # app = Starlette(routes=routes, middleware=middleware)

    CORS: dict[str, str] = {
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Headers": ("origin, content-type, accept, authorization, x-xsrf-token, x-request-id"),
    }
    pass


class ScopeValidationMiddleware(Middleware):
    name = "scopeValidation"
    attach_to = "request"
    priority = 10  # High priority to run early

    # https://sanic-jwt.readthedocs.io/en/latest/pages/scoped.html

    def intercept(request: Request, response: Optional[Response] = None) -> Optional[Response]:  # type: ignore[reportAttributeAccessIssue,reportSelfClsParameterName]
        # Skip validation for certain paths (like health checks)
        if request.path in ["/health", "/ping"]:
            # Don't return anything to allow continuation
            return None

        # Get the matched route from request context
        # The route should be available in the request context after routing
        route = getattr(request, "route", None)
        if not route:
            return None

        # Get required scopes for this route
        required_scopes = getattr(route, "scopes", [])

        # If no scopes required, allow access
        if not required_scopes:
            return None

        # Get user ID from request context
        user_id = request.context.get("user_id")
        if not user_id:
            return Response(body="Unauthorized - no user ID found", headers={"Content-Type": "text/plain"}, status=401)

        # TODO: Implement your token validation logic here
        # For now, return mock scopes - replace with actual JWT validation
        user_scopes = ["read:posts", "write:posts", "admin", "read:public", "read:api", "user", "debug"]

        # Check if user has required scopes
        for required_scope in required_scopes:
            if required_scope not in user_scopes:
                return Response(body="Insufficient permissions", headers={"Content-Type": "text/plain"}, status=403)

        # Don't return anything to allow continuation
        return None
