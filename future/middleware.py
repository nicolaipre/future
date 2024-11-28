from future.request import Request
from future.response import Response
import random

# CSRF: https://github.com/simonw/asgi-csrf
# CSP: Content Security Policy


class Middleware:
    name = None
    apply = True
    priority = 0
    attach_to = "request"

    def intercept(request: Request) -> Response | None:
        # return Response(b"Intercepted!")
        return None


class TestMiddlewareRequest(Middleware):
    name = "testReq"
    attach_to = "request"

    def intercept(request: Request) -> Response | None:
        return Response(body=b"req")
        # return None


class TestMiddlewareResponse(Middleware):
    name = "testResp"
    attach_to = "response"

    def intercept(request: Request, response: Response) -> Response | None:
        return Response(body=b"resp")
        # return None


# ----


class ResponseCodeConfuser(Middleware):
    name = "response code confuser"
    attach_to = "response"

    def intercept(request: Request, response: Response):
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

        # fuck with people using cURL to test
        if "curl" in request.headers["user-agent"]:
            random_code = random.choice(response_codes)
            # return EmptyResponse(status=random_code)
            return Response(status=random_code)


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
