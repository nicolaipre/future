# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Fixed
- `Future.run` passes the app instance when `workers=1` and reload is off; uses `config["APP_ASGI"]` (default `run:app`) for reload / multi-worker so `future run` works
- `BaseAuthentication` alias on `Authentication` so Azure AD / Kerberos stubs import cleanly
- `Database.transaction()` guards missing/`begin`-less clients with `NotImplementedError`
- `strict_slashes=True` no longer appends optional trailing `/`
- Env bools (`APP_ACCESS_LOG`, `APP_SSO`, `APP_REGISTRATION`) parse `"true"`/`"false"` correctly
- CORS no longer sends `Allow-Credentials` with `Allow-Origin: *` (default credentials off)
- OpenAPI paths normalize to `{param}` form; MySQL id-only upsert; Elasticsearch `where(..., "in", ...)`; Postgres URL-encodes credentials
- WebSocket handler errors close with 1011; lifespan tolerates missing `scope["state"]`
- `request.route` set for matched routes (`ScopeValidationMiddleware`); UUID route pattern is hex-only

### Changed
- Moved Lifespan to `future.lifespan` (ASGI lifecycle; tasks stay in `future.tasks`)
- Removed the unused per-status exception subclasses (`NotFoundException`, …)
- 404 / 403 / 405 from the router now return the same JSON error shape as raised `HTTPException`s
- Package layout: `controllers/`, `tasks/`, `testing/`, `cli/`, `models/`, `graphql/`; HTTP primitives stay top-level modules
- Imports: `future.tasks` (was `lifespan`/`scheduler`), `future.testing` (was `testclient`); removed `__main__.py` (`future` console script only)
- Folded `TODO.md` into `docs/gaps.md`; demo from `example.py` moved into README; deleted both files
- `APP_DEBUG` strips `:port` from `Host` for domain checks and route lookup; prod stays explicit
- WebSocket dispatch uses `Route.match("WEBSOCKET", path)`; `Request` tolerates websocket scopes; test client drives real ASGI
- Dropped debug `print` in `Route.match`
- Nested `RouteGroup` middleware accumulates outer → inner → route (was dropping parent group middleware)
- `future` logger level follows `APP_DEBUG`; no root `basicConfig`; library HTTP client noise is not wired into the framework
- CLI `migrate` / `seed` import `future.migrations` / `future.seeds` (package layout fix)
- `future make:migration <Model>` / `make:migrations`; `future make:seed <Model>` / `make:seeds` (singular requires a model; plural generates all)
- `future seed` with no name runs every seeder in `database/seeds/` (no `DatabaseSeeder` orchestrator)
- Controllers must return `Response` or `None` (bare `dict` raises `TypeError` → 500)
- Empty session clears the session cookie (`Max-Age=0`); `set_cookie` supports `max_age` / `domain` / `expires`
- `DATABASES` register on `Future` boot from config (no import-time `Connections` side effect); CLI migrate/seed load `run.py`
- Session cookies are HMAC-signed with `APP_KEY` (legacy unsigned cookies still readable once)

### Added
- OpenAPI model schemas via `OPENAPI.models` + `Model.openapi_schema()`, and typed path params (`<int:id>`, `<uuid:…>`, …)
- WebSocket duplex receive loop
- MongoDB / ClickHouse / Redis Active Record CRUD
- MkDocs Material theme; redis dependency
- SQLite driver (`future.databases.SQLite`) with schema, migrations tracking, and Active Record CRUD; scaffold defaults to SQLite
- Postgres Active Record CRUD (aligned with SQLite/MySQL); `where(..., "in", [...])`; `Model.transaction()` / `connection.transaction()`
- `belongs_to` / `has_many` / `eager_load` on models
- Multipart `form()` / `files()` with `UploadedFile`; CSRF + RateLimit middleware (exported)
- OpenAPI path parameters, servers (from `APP_DOMAIN` or config), security schemes / security
- `CORSMiddleware` and `GZipMiddleware` implementations; OpenAPI `tags` from `RouteGroup.name`
- `future run` CLI
- Same path with different HTTP methods (`Get("/x")` + `Post("/x")`); registration conflicts only on overlapping methods
- **405 Method Not Allowed** with `Allow` when the path matches but the method does not
- Route configs store `group` metadata (`name`, `prefix`, `subdomain`) for nested RouteGroups
- `future routes` lists routes in rich tables grouped by domain / group / prefix / middleware (includes path param **Args**)
- Single `HTTPException` + `ErrorHandler(request, response)` wired into HTTP dispatch (`self.response.json(...)`)
- Mocked tests for Model / Elasticsearch / MySQL; path-param styles; HTTPException / multi-method; ASGI websocket smoke tests
- Middleware tests for nested `RouteGroup` accumulation, before/after order, and before short-circuit

## [1.0.0] - 2026-07-22
First major release. The HTTP stack (controllers, middleware, request/response) is intentionally redesigned; apps written against 0.3.x need updates. See [docs/](docs/index.md) and [gaps.md](docs/gaps.md).

### Breaking
- **Controller DI** — Controllers are no longer static-only. Base `Controller.__init__(request, response)` injects `self.request` / `self.response`. Actions are instance methods.
- **Middleware API** — Base `Middleware` uses the same DI plus async `before()` / `after()` (no `attach_to` / class-level `intercept`). Returning a `Response` from `before` short-circuits; `after` runs in reverse on the same instances.
- **Module renames** — Use `future.request` and `future.response` only. Plural shims (`future.requests` / `future.responses`) are gone.
- **Sessions** — Cookie session load/save is opt-in via `SessionMiddleware`, not implicit on every request.
- **Wrong HTTP method** — Matching lives in `Route.match(method, path)`. Wrong method on an existing path currently returns **404** (no match), not **405**.

### Added
- **`Request.query`** — Query string parsed at construction (single value → `str`, repeated keys → `list`).
- **Cached request body** — First `body()` caches bytes; `json()` / `form()` reuse that cache.
- **Task jitter** — Optional `Task(..., jitter=60)` adds `random.uniform(0, jitter)` seconds to each `next_run` (default off).
- **`SessionMiddleware`** — Cookie ↔ `request.session` (unsigned base64 JSON) under `future.middleware`.
- **Unified `Response` builder** — `json()`, `html()`, `text()`, `empty()`, `redirect()`, `file()`, `image()`, plus `set_cookie` / `delete_cookie`.
- **OpenAPI UIs** — Swagger, Scalar, RapiDoc, and ReDoc; optional `redocly_license_key` for paid Redocly Reference Docs CDN.
- **Handler docstrings → OpenAPI** — First line → `summary`, remainder → `description`.
- **Path params on all verbs** — `Get` / `Post` / `Put` / … share `Route` + `match` → `await method(**route_params)`.
- **MkDocs guides** — Rewritten `docs/` (HTTP, routing, database, OpenAPI, lifespan/tasks, CLI, examples, gaps) plus a slim README landing page.

### Changed
- Middleware and controllers are instantiated once per request; path params still pass as action kwargs.
- Interval scheduler remains fixed-interval (not crontab); jitter is the only spread control.
- Documentation no longer claims unfinished features (auth, full WS, GraphQL HTTP endpoint, etc.); gaps are listed explicitly.

### Fixed
- Duplicate HTTP method checks consolidated into `Route.match` only (post-match 405 path removed).
- Session cookie plumbing cleaned up (no nested helpers inside the ASGI handler).

### Migration notes (0.3 → 1.0)
```python
# Controllers
class TradeController(Controller):
    async def index(self) -> Response:
        return self.response.json({"ok": True})

# Middleware
class Auth(Middleware):
    async def before(self) -> Optional[Response]:
        if not self.request.headers.get("authorization"):
            return self.response.json({"error": "unauthorized"}, status=401)
        return None

# Imports
from future.request import Request
from future.response import Response
from future.middleware.SessionMiddleware import SessionMiddleware

# Query / body
q = self.request.query.get("q")
data = await self.request.json()  # safe after body()

# Tasks
Task("scrape", interval=1, unit=Unit.HOURS, func=scraper, jitter=60)
```

## [0.3.1] - 2025-01-06
### Added
- Initial release of the Future framework
- Basic ASGI application structure
- Core routing and middleware systems
- GraphQL support with Strawberry
- WebSocket support
- CLI tool for project management

### Changed
- Complete architectural overhaul
- Removed all decorators for minimal design
- Implemented static method patterns
- Centralized configuration management

### Removed
- Legacy database integration
- Complex dependency chains
- Decorator-based patterns
- Boilerplate files

## [0.3.0] - 2025-01-06
### Added
- Foundation of the Future framework
- Basic routing system
- Middleware infrastructure
- Type safety throughout

## [0.2.0] - 2025-01-06
### Added
- Initial project structure
- Core ASGI application
- Basic routing capabilities

## [0.1.0] - 2025-01-06
### Added
- Project initialization
- Basic framework structure
- Development environment setup

---

## Versioning
This project uses [Semantic Versioning](https://semver.org/) for version numbers.

### Version Increment Rules:
- **Patch releases** (1.0.0 → 1.0.1): Bug fixes and minor improvements
- **Minor releases** (1.0.0 → 1.1.0): New features, backward compatible
- **Major releases** (1.0.0 → 2.0.0): Breaking changes

### GitHub Workflows
All releases and publishing are handled automatically by GitHub workflows:
- **CI**: Runs on every push/PR (linting, type checking, tests, building)
- **Publish**: Automatically publishes to PyPI when tags are pushed
- **Versioning**: Uses `poetry-dynamic-versioning` for automatic version management

The version is automatically incremented based on git commit messages:
- `feat:` → minor version bump
- `BREAKING CHANGE:` → major version bump
- Default → patch version bump
