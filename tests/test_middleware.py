from typing import Optional

from future.application import Future
from future.controllers import Controller
from future.middleware import Middleware
from future.response import Response
from future.routing import Get, RouteGroup
from future.lifespan import Lifespan
from future.testing import FutureTestClient


class TagA(Middleware):
    name = "A"
    tag = "A"

    async def before(self) -> Optional[Response]:
        self.request.context.setdefault("order", []).append(f"{self.tag}-before")
        return None

    async def after(self) -> Optional[Response]:
        self.request.context.setdefault("order", []).append(f"{self.tag}-after")
        return self.response.json({"order": list(self.request.context["order"])})


class TagB(Middleware):
    name = "B"
    tag = "B"

    async def before(self) -> Optional[Response]:
        self.request.context.setdefault("order", []).append(f"{self.tag}-before")
        return None

    async def after(self) -> Optional[Response]:
        self.request.context.setdefault("order", []).append(f"{self.tag}-after")
        return self.response.json({"order": list(self.request.context["order"])})


class TagC(Middleware):
    name = "C"
    tag = "C"

    async def before(self) -> Optional[Response]:
        self.request.context.setdefault("order", []).append(f"{self.tag}-before")
        return None

    async def after(self) -> Optional[Response]:
        self.request.context.setdefault("order", []).append(f"{self.tag}-after")
        return self.response.json({"order": list(self.request.context["order"])})


class InterruptMiddleware(Middleware):
    name = "interrupt"

    async def before(self) -> Optional[Response]:
        if self.request.headers.get("x-interrupt") == "1":
            return self.response.text("Request intercepted!")
        return None


class MwController(Controller):
    async def ok(self) -> Response:
        return self.response.json({"order": list(self.request.context.get("order", []))})


def _config():
    return {"APP_NAME": "t", "APP_DOMAIN": "", "APP_DEBUG": True, "OPENAPI": {"enabled": False, "auto_routes": False}}


def test_nested_routegroup_middleware_classes():
    app = Future(lifespan=Lifespan(), config=_config())
    app.add_routes([
        RouteGroup(
            name="outer",
            middlewares=[TagA],
            routes=[
                RouteGroup(
                    name="inner",
                    middlewares=[TagB],
                    routes=[Get("/x", MwController.ok, "x", middlewares=[TagC])],
                ),
            ],
        )
    ])
    cfg = next(iter(app.routes[""].values()))
    names = [m.name for m in cfg["middleware"]["classes"]]
    assert names == ["A", "B", "C"]


async def test_nested_middleware_before_after_http():
    app = Future(lifespan=Lifespan(), config=_config())
    app.add_routes([
        RouteGroup(
            name="outer",
            middlewares=[TagA],
            routes=[
                RouteGroup(
                    name="inner",
                    middlewares=[TagB],
                    routes=[Get("/nested", MwController.ok, "nested", middlewares=[TagC])],
                ),
            ],
        )
    ])
    async with FutureTestClient(app) as client:
        r = await client.get("http://127.0.0.1/nested")
        assert r.status_code == 200
        assert r.json()["order"] == [
            "A-before",
            "B-before",
            "C-before",
            "C-after",
            "B-after",
            "A-after",
        ]


async def test_middleware_before_short_circuit():
    app = Future(lifespan=Lifespan(), config=_config())
    app.add_routes([
        RouteGroup(
            name="Main",
            middlewares=[InterruptMiddleware],
            routes=[Get("/secure", MwController.ok, "secure")],
        )
    ])
    async with FutureTestClient(app) as client:
        blocked = await client.get("http://127.0.0.1/secure", headers={"x-interrupt": "1"})
        assert blocked.status_code == 200
        assert blocked.text == "Request intercepted!"
        ok = await client.get("http://127.0.0.1/secure")
        assert ok.status_code == 200
        assert ok.json() == {"order": []}
