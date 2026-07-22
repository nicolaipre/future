from typing import Optional

from future.request import Request
from future.response import Response


# README - a note on the use of middlewares:
# if a middleware does not RETURN or hit any EXCEPTIONS, it means it passes (all checks ok)
# if it however RETURNS or hits an EXCEPTION, the middleware check will deny further processing of the request.


class Middleware:
    name: Optional[str] = None
    apply: bool = True
    priority: int = 0

    def __init__(self, request: Request, response: Response) -> None:
        self.request = request
        self.response = response

    async def before(self) -> Optional[Response]:
        return None

    async def after(self) -> Optional[Response]:
        return None


class TestMiddlewareRequest(Middleware):
    name = "testRequestMiddleware"

    async def before(self) -> Optional[Response]:
        if self.request.headers.get("x-interrupt") == "1":
            return self.response.text("Request intercepted!")
        return None


class TestMiddlewareResponse(Middleware):
    name = "testResponseMiddleware"

    async def after(self) -> Optional[Response]:
        if self.request.headers.get("x-interrupt-response") == "1":
            return self.response.text("Response intercepted!")
        return None


class ResponseCodeConfuser(Middleware):
    name = "response code confuser"

    async def after(self) -> Optional[Response]:
        import random

        response_codes = [
            100, 101, 102, 103, 200, 201, 202, 203, 204, 205, 206, 207, 208, 226,
            300, 301, 302, 303, 304, 305, 306, 307, 308,
            400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414,
            415, 416, 417, 418, 421, 422, 423, 424, 425, 426, 428, 429, 431, 451,
            500, 501, 502, 503, 504, 505, 506, 507, 508, 510, 511,
        ]
        if "curl" in self.request.headers.get("user-agent", ""):
            return self.response.empty(status=random.choice(response_codes))
        return None


class RateLimitMiddleware(Middleware):
    name = "RateLimitMiddleware"
    limit = 60
    window_seconds = 60
    _hits: dict[str, list[float]] = {}

    async def before(self) -> Optional[Response]:
        import time
        client = (self.request.scope.get("client") or ("unknown", 0))[0]
        now = time.time()
        bucket = self._hits.setdefault(client, [])
        cutoff = now - self.window_seconds
        self._hits[client] = [stamp for stamp in bucket if stamp >= cutoff]
        if len(self._hits[client]) >= self.limit:
            return self.response.json({"error": "Too Many Requests", "status_code": 429}, status=429)
        self._hits[client].append(now)
        return None


class CSRFMiddleware(Middleware):
    name = "CSRFMiddleware"
    cookie_name = "csrf_token"
    header_name = "x-csrf-token"
    safe_methods = {"GET", "HEAD", "OPTIONS"}

    async def before(self) -> Optional[Response]:
        import secrets
        token = self.request.cookies.get(self.cookie_name)
        if not token:
            token = secrets.token_urlsafe(32)
            self.request.context["csrf_token_new"] = token
        self.request.context["csrf_token"] = token
        if self.request.method in self.safe_methods:
            return None
        provided = self.request.headers.get(self.header_name) or self.request.headers.get("x-xsrf-token")
        if not provided:
            form = await self.request.form()
            value = form.get("csrf_token")
            provided = value if isinstance(value, str) else None
        if not provided or not secrets.compare_digest(str(provided), str(token)):
            return self.response.json({"error": "CSRF token missing or invalid", "status_code": 403}, status=403)
        return None

    async def after(self) -> Optional[Response]:
        token = self.request.context.get("csrf_token_new") or self.request.context.get("csrf_token")
        if token:
            self.response.set_cookie(self.cookie_name, token, httponly=False, samesite="Strict", secure=(self.request.scheme == "https"))
        return None


class WebServerConfuser(Middleware):
    pass


class BruteforcePrevention(Middleware):
    pass


class SQLiConfuser(Middleware):
    pass


class HTAccessConfuser(Middleware):
    pass


class HeaderConfuser(Middleware):
    pass


class GZipMiddleware(Middleware):
    name = "GZipMiddleware"

    async def after(self) -> Optional[Response]:
        accept = self.request.headers.get("accept-encoding", "")
        if "gzip" not in accept.lower():
            return None
        if not self.response.body:
            return None
        for key, _value in self.response.headers:
            if key.lower() == b"content-encoding":
                return None
        import gzip
        compressed = gzip.compress(self.response.body)
        self.response.body = compressed
        self.response.headers = [pair for pair in self.response.headers if pair[0].lower() != b"content-length"]
        self.response.headers.append([b"content-encoding", b"gzip"])
        self.response.headers.append([b"content-length", str(len(compressed)).encode("utf-8")])
        return None


class CORSMiddleware(Middleware):
    name = "CORSMiddleware"
    allow_origin = "*"
    allow_methods = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    allow_headers = "origin, content-type, accept, authorization, x-xsrf-token, x-request-id"
    allow_credentials = "false"

    def _apply_headers(self) -> None:
        self.response.headers.append([b"access-control-allow-origin", self.allow_origin.encode("utf-8")])
        self.response.headers.append([b"access-control-allow-methods", self.allow_methods.encode("utf-8")])
        self.response.headers.append([b"access-control-allow-headers", self.allow_headers.encode("utf-8")])
        if self.allow_origin != "*":
            self.response.headers.append([b"access-control-allow-credentials", self.allow_credentials.encode("utf-8")])

    async def before(self) -> Optional[Response]:
        if self.request.method == "OPTIONS":
            self.response.empty(status=204)
            self._apply_headers()
            return self.response
        return None

    async def after(self) -> Optional[Response]:
        self._apply_headers()
        return None


class ScopeValidationMiddleware(Middleware):
    name = "scopeValidation"
    priority = 10

    async def before(self) -> Optional[Response]:
        if self.request.path in ["/health", "/ping"]:
            return None
        route = getattr(self.request, "route", None)
        if not route:
            return None
        required_scopes = getattr(route, "scopes", [])
        if not required_scopes:
            return None
        user_id = self.request.context.get("user_id")
        if not user_id:
            return self.response.text("Unauthorized - no user ID found", status=401)
        user_scopes = ["read:posts", "write:posts", "admin", "read:public", "read:api", "user", "debug"]
        for required_scope in required_scopes:
            if required_scope not in user_scopes:
                return self.response.text("Insufficient permissions", status=403)
        return None
