from future.middleware.Middleware import (
    CORSMiddleware,
    CSRFMiddleware,
    GZipMiddleware,
    Middleware,
    RateLimitMiddleware,
    ScopeValidationMiddleware,
    TestMiddlewareRequest,
    TestMiddlewareResponse,
)
from future.middleware.SessionMiddleware import (
    SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_NAME,
    SESSION_COOKIE_PATH,
    SESSION_COOKIE_SAMESITE,
    SessionMiddleware,
)

# Back-compat aliases during migration
SessionRequestMiddleware = SessionMiddleware
SessionResponseMiddleware = SessionMiddleware
