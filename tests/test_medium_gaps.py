from future.application import Future
from future.controllers import Controller
from future.databases.Connections import Connections
from future.databases.SQLite import SQLite
from future.middleware import CSRFMiddleware, RateLimitMiddleware, SessionMiddleware
from future.middleware.SessionMiddleware import SESSION_COOKIE_NAME
from future.migrations.Blueprint import Blueprint
from future.models import Model
from future.openapi import openapi_routes, rebuild_spec_from_routes
from future.request import Request, UploadedFile
from future.response import Response
from future.routing import Get, Post, RouteGroup
from future.lifespan import Lifespan
from future.testing import FutureTestClient
from future.types import ASGIReceive, ASGIScope


class User(Model):
    __connection__ = "default"
    __table__ = "users"
    id: str
    name: str


class PostModel(Model):
    __connection__ = "default"
    __table__ = "posts"
    id: str
    user_id: str
    title: str


class UploadController(Controller):
    async def create(self) -> Response:
        form = await self.request.form()
        files = await self.request.files()
        upload = files.get("file")
        return self.response.json({
            "title": form.get("title"),
            "filename": getattr(upload, "filename", None),
            "size": len(upload.content) if upload else 0,
        })


class SessionController(Controller):
    async def login(self) -> Response:
        self.request.session["user"] = "alice"
        return self.response.json({"ok": True})


class CsrfOkController(Controller):
    async def index(self) -> Response:
        return self.response.json({"ok": True})

    async def write(self) -> Response:
        return self.response.json({"ok": True})


def _register_sqlite():
    Connections._connections = {}
    Connections._default = None
    databases = {"default": "sqlite", "sqlite": SQLite(database=":memory:")}
    Future(lifespan=Lifespan(), config={"APP_NAME": "t", "APP_DOMAIN": "", "APP_DEBUG": True, "APP_KEY": "test-secret", "DATABASES": databases, "OPENAPI": {"enabled": True}})
    connection = Connections().get_connection("default")
    users = Blueprint("users", "default", action="create")
    users.id()
    users.string("name")
    connection.schema_create(users)
    posts = Blueprint("posts", "default", action="create")
    posts.id()
    posts.string("user_id")
    posts.string("title")
    connection.schema_create(posts)
    return connection


def test_multipart_form_and_files():
    boundary = "----FutureBoundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="title"\r\n\r\n'
        f"Hello\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="a.txt"\r\n'
        f"Content-Type: text/plain\r\n\r\n"
        f"file-bytes\r\n"
        f"--{boundary}--\r\n"
    ).encode("utf-8")

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/upload",
        "headers": [(b"content-type", f"multipart/form-data; boundary={boundary}".encode()), (b"host", b"example.com")],
        "scheme": "http",
        "query_string": b"",
    }
    request = Request(scope, receive)
    import asyncio
    form = asyncio.run(request.form())
    files = asyncio.run(request.files())
    assert form["title"] == "Hello"
    assert isinstance(files["file"], UploadedFile)
    assert files["file"].filename == "a.txt"
    assert files["file"].content == b"file-bytes"


async def test_multipart_via_http():
    boundary = "----FutureBoundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="title"\r\n\r\n'
        f"Hello\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="a.txt"\r\n'
        f"Content-Type: text/plain\r\n\r\n"
        f"file-bytes\r\n"
        f"--{boundary}--\r\n"
    ).encode("utf-8")
    app = Future(lifespan=Lifespan(), config={"APP_NAME": "t", "APP_DOMAIN": "", "APP_DEBUG": True, "OPENAPI": {"enabled": False}})
    app.add_routes([RouteGroup(name="Main", routes=[Post("/upload", UploadController.create, "upload")])])
    async with FutureTestClient(app) as client:
        response = await client.post(
            "http://127.0.0.1/upload",
            data=body,
            headers={"content-type": f"multipart/form-data; boundary={boundary}"},
        )
        assert response.status_code == 200
        assert response.json() == {"title": "Hello", "filename": "a.txt", "size": 10}


async def test_signed_session_cookie():
    app = Future(lifespan=Lifespan(), config={"APP_NAME": "t", "APP_DOMAIN": "", "APP_DEBUG": True, "APP_KEY": "test-secret", "OPENAPI": {"enabled": False}})
    app.add_routes([RouteGroup(name="Auth", middlewares=[SessionMiddleware], routes=[Get("/login", SessionController.login, "login")])])
    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/login")
        cookie = [h for h in response.headers.get_list("set-cookie") if SESSION_COOKIE_NAME in h][0]
        value = cookie.split(";", 1)[0].split("=", 1)[1]
        assert "." in value


def test_openapi_path_params_servers_security():
    class Show(Controller):
        async def show(self, id: str) -> Response:
            return self.response.json({"id": id})

    app = Future(
        lifespan=Lifespan(),
        config={
            "APP_NAME": "t",
            "APP_DOMAIN": "api.example.com",
            "APP_DEBUG": True,
            "OPENAPI": {
                "enabled": True,
                "servers": [{"url": "https://api.example.com", "description": "Application"}],
                "security_schemes": {"bearerAuth": {"type": "http", "scheme": "bearer"}},
                "security": [{"bearerAuth": []}],
            },
        },
    )
    app.add_routes([RouteGroup(name="Main", routes=[Get("/items/<id>", Show.show, "item")])])
    spec = rebuild_spec_from_routes(app.routes, app.config)
    assert spec["paths"]["/items/{id}"]["get"]["parameters"][0]["name"] == "id"
    assert spec["servers"][0]["url"] == "https://api.example.com"
    assert "bearerAuth" in spec["components"]["securitySchemes"]
    assert spec["security"] == [{"bearerAuth": []}]


async def test_openapi_servers_from_request_and_subdomains():
    class Show(Controller):
        async def show(self) -> Response:
            return self.response.json({"ok": True})

    app = Future(
        lifespan=Lifespan(),
        config={
            "APP_NAME": "t",
            "APP_DOMAIN": "example.com",
            "APP_DEBUG": True,
            "OPENAPI": {"enabled": True, "auto_routes": False, "servers": None},
        },
    )
    app.add_routes(
        [
            RouteGroup(name="Docs", routes=openapi_routes(uis=["scalar"])),
            RouteGroup(name="Api", subdomain="api", routes=[Get("/items", Show.show, "items")]),
            RouteGroup(name="Apex", routes=[Get("/health", Show.show, "health")]),
        ]
    )
    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/openapi.json", headers={"Host": "example.com:8000"})
        assert response.status_code == 200
        body = response.json()
        assert body["servers"][0]["url"] == "http://api.example.com:8000"
        assert {s["url"] for s in body["servers"]} >= {"http://api.example.com:8000", "http://example.com:8000"}
        assert body["paths"]["/items"]["servers"][0]["url"] == "http://api.example.com:8000"
        assert body["paths"]["/health"]["servers"][0]["url"] == "http://example.com:8000"
        assert "x-future-hosts" not in body["paths"]["/items"]


async def test_csrf_and_rate_limit():
    RateLimitMiddleware._hits = {}
    RateLimitMiddleware.limit = 2
    RateLimitMiddleware.window_seconds = 60
    app = Future(lifespan=Lifespan(), config={"APP_NAME": "t", "APP_DOMAIN": "", "APP_DEBUG": True, "OPENAPI": {"enabled": False}})
    app.add_routes([
        RouteGroup(
            name="Main",
            middlewares=[CSRFMiddleware, RateLimitMiddleware],
            routes=[
                Get("/ok", CsrfOkController.index, "ok"),
                Post("/write", CsrfOkController.write, "write"),
            ],
        ),
    ])
    async with FutureTestClient(app) as client:
        first = await client.get("http://127.0.0.1/ok")
        assert first.status_code == 200
        csrf = [h for h in first.headers.get_list("set-cookie") if "csrf_token=" in h][0]
        token = csrf.split(";", 1)[0].split("=", 1)[1]
        denied = await client.post("http://127.0.0.1/write", json={})
        assert denied.status_code == 403
        allowed = await client.post("http://127.0.0.1/write", json={}, headers={"x-csrf-token": token, "cookie": f"csrf_token={token}"})
        assert allowed.status_code == 200
        RateLimitMiddleware.limit = 1
        RateLimitMiddleware._hits = {"127.0.0.1": []}
        await client.get("http://127.0.0.1/ok")
        limited = await client.get("http://127.0.0.1/ok")
        assert limited.status_code == 429


def test_relations_eager_load_and_transaction():
    _register_sqlite()
    User(id="u1", name="Ada").save()
    User(id="u2", name="Bob").save()
    PostModel(id="p1", user_id="u1", title="one").save()
    PostModel(id="p2", user_id="u1", title="two").save()
    user = User.find("u1")
    posts = user.has_many(PostModel)
    assert len(posts) == 2
    assert posts[0].belongs_to(User).name == "Ada"
    loaded = PostModel.eager_load(PostModel.all(), "author", User, kind="belongs_to")
    assert loaded[0].author.name in ("Ada", "Bob")
    with User.transaction():
        User(id="u3", name="Cara").save()
    assert User.find("u3").name == "Cara"
