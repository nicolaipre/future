# OpenAPI
Future builds an OpenAPI 3 document from registered routes and serves interactive UIs.

## Mount docs
Keep docs in a `RouteGroup` so you can attach middleware:

```python
from future.openapi import openapi_routes
from future.routing import RouteGroup

ROUTES = [
    RouteGroup(
        name="Docs",
        # middlewares=[AuthMiddleware],
        routes=openapi_routes(uis=["swagger", "redoc", "scalar", "rapidoc"]),
    ),
]
```

Or set `"auto_routes": True` in config to append docs if `/openapi.json` is not already registered.

## Config
```python
"OPENAPI": {
    "enabled": True,
    "uis": ["swagger", "redoc", "scalar", "rapidoc"],
    "auto_routes": False,
    "path_prefix": "",
    # Optional: model classes → components.schemas via Model.openapi_schema()
    "models": [],
    # Paid Redocly Reference Docs (Try it). Empty = OSS ReDoc.
    # "redocly_license_key": "your-license-key",
}
```

| Path | UI |
|------|-----|
| `/openapi.json` | Schema |
| `/docs` | Swagger UI (Try it out) |
| `/redoc` | ReDoc, or Redocly Reference Docs if `redocly_license_key` is set |
| `/scalar` | Scalar |
| `/rapidoc` | RapiDoc (`allow-try`) |

OSS ReDoc has **no** Try button. Use Swagger, Scalar, RapiDoc, or a paid Redocly license.

## Docstrings → schema
Handler / action docstrings feed the spec (FastAPI-style):

- First line → `summary`
- Remainder → `description` (Markdown OK)

```python
async def get_trades(self) -> Response:
    """List all trades.

    Returns every trade in the configured store.
    """
```

## Models
Register model classes in config so they appear under `components.schemas`:

```python
"OPENAPI": {
    "models": [Trade],
}
```

Each entry is instantiated and calls `Model.openapi_schema()`. Schemas are documentation-only; they are not wired to route responses or request bodies.

Path params use richer types when the path has `<int:id>`, `<float:x>`, `<uuid:id>`, etc. (`int` → integer, `float` → number, `uuid` → string+format uuid, else string).

## What the spec includes
Paths (OpenAPI `{param}` form), methods, `operationId`, summary/description from handler docstrings, typed path parameters, optional `tags` from `RouteGroup.name`, `servers`, security schemes, generic object `requestBody` on POST/PUT/PATCH, and JSON Schema from `OPENAPI.models` via `Model.openapi_schema()`.
