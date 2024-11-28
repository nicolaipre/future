from future.request import Request
from future.response import Response


class Exception(BaseException):  # ASGIException????
    pass


# custom exception handler - FIXME: Does ASGI have anything standard for this?
class RouteExceptionHandler: # ErrorHandler
    # Taken straight from https://sanic.dev/en/guide/best-practices/exceptions.html#custom-error-handling
    def default(self, request: Request, exception: Exception) -> Response:  # type: ignore[override]
        status_code = getattr(exception, "status_code", 500)
        error_messages = {
            403: "Unauthorized",
            404: "Not found",
            # custom error handler to fuck with people snooping on your shit
            # put in some Apache, nginx, litespeed, etc. return strings 4 the lulz
            # https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
        }
        error = error_messages.get(status_code, str(exception))
        return Response(body=error, status=status_code)
