# Gaps and roadmap
Honest inventory of what Future still lacks or only partially implements. Use this when deciding what to build next.

## Won’t do unless requested
| Item | Notes |
|------|-------|
| **Query / form → action kwargs** | Path params and `request.query` / cached `body()` / `json()` / `form()` / `files()` are enough. Auto-inject into action kwargs fights explicit style. |

## Database / ORM
MongoDB, ClickHouse, and Redis Active Record CRUD are usable (Redis has no schema/migrate). Remaining ORM gaps are driver-specific edge cases rather than stubs.

- **`where(..., "like", ...)` naming** — Pattern matching works on all drivers (`%` / `_`, mapped per backend), but the operator name is SQL-flavored. Later: review a more generic, cross-store name (e.g. `match` / `pattern` / `contains`-style) that stays understandable for SQL, Elasticsearch, MongoDB, etc., without breaking the agnostic Model API. Keep one portable pattern language; avoid driver-specific wording in app code.

## Middleware stock library
CORS, GZip, CSRF, and RateLimit are usable and exported. Confuser classes remain unfinished and are **not** exported from `future.middleware`.

## Authentication
`future.authentication.*` are stubs (`auth_type` only). `BaseAuthentication` is an alias of `Authentication` so placeholder subclasses import. No JWT / OIDC / session-login middleware ships yet.

## WebSockets
Usable duplex echo — see [WebSockets](websockets.md). `handle_websocket_request` mirrors HTTP for middleware, controller DI, and path params; errors close with 1011.

- `StreamingResponse` for HTTP chunked/stream bodies is still unimplemented

## HTTP/2 / ASGI server
- Outbound: prefer httpx (already used by the test client).
- Inbound HTTP/2: reverse proxy (nginx / Hypercorn in front) is fine.
- **`Future.run` stays on uvicorn.** Hypercorn is **not** a drop-in for `uvicorn.run(...)` (different API: `Config` + `asyncio.run(serve(app, config))`, different workers/reload). An optional Hypercorn backend can be a later feature, not a silent swap.

## GraphQL
`GraphQLController.query` accepts `POST` with `{query, variables?, operationName?}`. Schema from `config["GRAPHQL_SCHEMA"]`, else the in-repo demo schema. Docs must not claim `app.add_graphql_route`.

- **`strawberry.type(Model)` vs Active Record** — Strawberry’s `type(...)` dataclass-wraps the class in place, which breaks `ModelMeta` (`User.where` / `User.find` via empty `self()`). Apps must build separate GraphQL types from model `__annotations__` and return AR instances from resolvers. Later: see if models can become dataclass-compatible **without** `@dataclass` / decorator hacks so one class can serve ORM + GraphQL the way we want; design carefully and keep the no-decorator rule.

## Plugins
`Plugin` is a marker. Only `ElasticsearchPlugin` is substantial. No lifecycle hooks into `Future` boot.

## Testing
Most HTTP / middleware / path-syntax / DB coverage lives under `tests/`. Remaining gaps:

| Gap | Notes |
|-----|-------|
| `FutureTestClient` sync API | Prefer `from future.testing import FutureTestClient` (async). |

## Exploring (needs design — keep Future simple)
| Idea | Notes |
|------|-------|
| **Thin service container** | Optional Masonite-like `bind` / `singleton` / `make` for app services (mail, clients, `TradeService`), while controllers keep explicit `request` / `response` DI. Not a full auto-wire IoC for every dependency. Must stay optional and obvious — no hidden constructor magic by default. Compare Masonite’s container; design carefully before shipping. |

## Explicitly out of scope (for now)
- Full IoC / auto-wiring every constructor argument (Laravel/Spring-style for the whole app)
- Shipping Redocly paid JS without a customer license
- Revel / Reef portal products (not embeddable OpenAPI UIs)
- Replacing uvicorn with Hypercorn as a silent default

---

When closing a gap, update the relevant guide and delete the row here.
