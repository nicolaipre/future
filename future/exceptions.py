from future.request import Request
from future.response import Response


class HTTPException(Exception):
    """Raise from controllers/middleware to return an HTTP error response."""

    def __init__(self, message: str = "Internal Server Error", status_code: int = 500, headers: dict[str, str] | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.headers = headers or {}


class ErrorHandler:
    def __init__(self, request: Request, response: Response):
        self.request = request
        self.response = response

    def handle(self, exception: Exception) -> Response:
        if isinstance(exception, HTTPException):
            return self.response.json(
                {"error": exception.message, "status_code": exception.status_code, "path": self.request.path},
                status=exception.status_code,
                headers=exception.headers or None,
            )
        return self.response.json({"error": "Internal Server Error", "status_code": 500, "path": self.request.path}, status=500)
