# OpenAPI
Future builds an OpenAPI 3 document from registered routes and serves UIs.

## Mount docs
```python
from future.openapi import openapi_routes
from future.routing import RouteGroup

routes = [
    RouteGroup(
        name="Docs",
        routes=openapi_routes(uis=["swagger", "redoc", "scalar", "rapidoc"]),
    ),
]
```

## Config
```python
"OPENAPI": {
    "enabled": True,
    "uis": ["swagger", "redoc", "scalar", "rapidoc"],
    "auto_routes": False,
    "path_prefix": "",
}
```

| Path | UI |
|------|-----|
| `/openapi.json` | Schema |
| `/docs` | Swagger UI |
| `/redoc` | ReDoc |
| `/scalar` | Scalar |
| `/rapidoc` | RapiDoc |

## Docstrings
First line → `summary`; rest → `description`:

```python
async def get_stocks(self) -> Response:
    """List stocks, optionally filtered by instrument_id or ticker.

    Query params: `instrument_id`, `ticker` (symbol).
    """
```
