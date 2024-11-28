from future.middleware import Middleware
from future.request import Request
from future.response import Response


class ExampleMiddleware(Middleware):
    name = "example"
    attach_to = "request"
    priority = 0

    def intercept(request: Request):
        return Response("OK")
