from future.application import Future
from future.controllers import Controller
from future.exceptions import HTTPException
from future.response import Response
from future.routing import Get, Post, RouteGroup
from future.lifespan import Lifespan
from future.testing import FutureTestClient


class ParamController(Controller):
    async def angle(self, item_id: str) -> Response:
        return self.response.json({"style": "angle", "item_id": item_id})

    async def mustache(self, item_id: str) -> Response:
        return self.response.json({"style": "mustache", "item_id": item_id})

    async def colon(self, item_id: str) -> Response:
        return self.response.json({"style": "colon", "item_id": item_id})

    async def boom(self) -> Response:
        raise HTTPException("nope", 422)

    async def ok(self) -> Response:
        return self.response.text("ok")


def _app():
    app = Future(lifespan=Lifespan(), config={"APP_NAME": "t", "APP_DOMAIN": "", "APP_DEBUG": True, "OPENAPI": {"enabled": False, "auto_routes": False}})
    app.add_routes([
        RouteGroup(
            name="Main",
            routes=[
                Get("/angle/<int:item_id>", ParamController.angle, "angle"),
                Get("/mustache/{item_id}", ParamController.mustache, "mustache"),
                Get("/colon/:item_id", ParamController.colon, "colon"),
                Get("/same", ParamController.ok, "same.get"),
                Post("/same", ParamController.ok, "same.post"),
                Get("/boom", ParamController.boom, "boom"),
            ],
        )
    ])
    return app


async def test_path_param_styles():
    async with FutureTestClient(_app()) as client:
        r = await client.get("http://127.0.0.1/angle/7")
        assert r.status_code == 200 and r.json() == {"style": "angle", "item_id": "7"}
        r = await client.get("http://127.0.0.1/mustache/abc")
        assert r.status_code == 200 and r.json()["style"] == "mustache"
        r = await client.get("http://127.0.0.1/colon/xyz")
        assert r.status_code == 200 and r.json()["item_id"] == "xyz"


async def test_multi_method_and_405():
    async with FutureTestClient(_app()) as client:
        assert (await client.get("http://127.0.0.1/same")).status_code == 200
        assert (await client.post("http://127.0.0.1/same")).status_code == 200
        r = await client.client.put("http://127.0.0.1/same")
        assert r.status_code == 405
        assert "GET" in r.headers.get("allow", "")


async def test_http_exception_json():
    async with FutureTestClient(_app()) as client:
        r = await client.get("http://127.0.0.1/boom")
        assert r.status_code == 422
        assert r.json()["error"] == "nope"


async def test_debug_strips_host_port():
    app = Future(lifespan=Lifespan(), config={"APP_NAME": "t", "APP_DOMAIN": "localhost", "APP_DEBUG": True, "OPENAPI": {"enabled": False, "auto_routes": False}})
    app.add_routes([RouteGroup(name="Main", routes=[Get("/x", ParamController.ok, "x")])])
    # domainless false — routes keyed under localhost
    assert "localhost" in app.routes or any("localhost" in d for d in app.routes)
    async with FutureTestClient(app) as client:
        r = await client.get("http://127.0.0.1/x", headers={"host": "localhost:8000"})
        # With APP_DEBUG, Host port stripped so domain check passes
        assert r.status_code in (200, 404)
        # If 404, domain key mismatch for registration — registration uses APP_DOMAIN without port
        # Re-check: routes registered under subdomain "" + domain localhost = "localhost"
        r2 = await client.get("http://127.0.0.1/x", headers={"host": "localhost"})
        assert r2.status_code == 200
        r3 = await client.get("http://127.0.0.1/x", headers={"host": "localhost:8000"})
        assert r3.status_code == 200
