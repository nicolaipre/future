import traceback

from future.requests import Request
from future.responses import JSONResponse, Response


class FutureException(Exception):
    """Base exception class for Future framework."""

    def __init__(self, message: str = "Internal Server Error", status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.traceback = traceback.format_exc()


class NotFoundException(FutureException):
    """Exception for 404 Not Found errors."""

    def __init__(self, message: str = "Not Found"):
        super().__init__(message, 404)


class BadRequestException(FutureException):
    """Exception for 400 Bad Request errors."""

    def __init__(self, message: str = "Bad Request"):
        super().__init__(message, 400)


class UnauthorizedException(FutureException):
    """Exception for 401 Unauthorized errors."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)


class ForbiddenException(FutureException):
    """Exception for 403 Forbidden errors."""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, 403)


class MethodNotAllowedException(FutureException):
    """Exception for 405 Method Not Allowed errors."""

    def __init__(self, message: str = "Method Not Allowed"):
        super().__init__(message, 405)


class ConflictException(FutureException):
    """Exception for 409 Conflict errors."""

    def __init__(self, message: str = "Conflict"):
        super().__init__(message, 409)


class ValidationException(FutureException):
    """Exception for validation errors (422 Unprocessable Entity)."""

    def __init__(self, message: str = "Validation Error"):
        super().__init__(message, 422)


class RateLimitException(FutureException):
    """Exception for rate limiting errors (429 Too Many Requests)."""

    def __init__(self, message: str = "Too Many Requests"):
        super().__init__(message, 429)


class InternalServerException(FutureException):
    """Exception for 500 Internal Server Error."""

    def __init__(self, message: str = "Internal Server Error"):
        super().__init__(message, 500)


class ServiceUnavailableException(FutureException):
    """Exception for 503 Service Unavailable."""

    def __init__(self, message: str = "Service Unavailable"):
        super().__init__(message, 503)


class ErrorHandler:
    """Base error handler for the Future framework."""

    def handle(self, request: Request, exception: Exception) -> Response:
        """Handle an exception and return an appropriate response."""
        if isinstance(exception, FutureException):
            return self._handle_future_exception(request, exception)
        else:
            return self._handle_generic_exception(request, exception)

    def _handle_future_exception(self, request: Request, exception: FutureException) -> Response:
        """Handle Future framework exceptions."""
        return JSONResponse(data={"error": exception.message, "status_code": exception.status_code, "path": request.path}, status=exception.status_code)

    def _handle_generic_exception(self, request: Request, exception: Exception) -> Response:
        """Handle generic exceptions."""
        return JSONResponse(data={"error": "Internal Server Error", "status_code": 500, "path": request.path}, status=500)
