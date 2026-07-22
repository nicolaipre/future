from future.application import Future
from future.controllers import WelcomeController
from future.lifespan import Lifespan
from future.routing import Get, RouteGroup
from future.testing import FutureTestClient


async def test_application_subdomains_single_subdomain() -> None:
    routes = [
        RouteGroup(
            name="test_application_routes",
            subdomain="api",
            routes=[
                Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # type: ignore[reportAttributeAccessIssue]
            ],
        ),
    ]

    test_domain = "example.com"
    config = {
        "APP_NAME": "test_application_subdomains",
        "APP_DOMAIN": test_domain,
        "APP_DEBUG": False,
    }
    lifespan = Lifespan()
    app = Future(lifespan=lifespan, config=config)
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/", headers={"Host": f"api.{test_domain}"})
        assert response.status_code == 200
        assert response.text == "✨ Welcome to Future! ✨"


async def test_application_subdomains_double_subdomain_2() -> None:
    routes = [
        RouteGroup(
            name="test_application_routes",
            subdomain="api",
            routes=[
                Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # type: ignore[reportAttributeAccessIssue]
            ],
        ),
    ]

    test_domain = "api.example.com"
    config = {
        "APP_NAME": "test_application_subdomains",
        "APP_DOMAIN": test_domain,
        "APP_DEBUG": False,
    }
    lifespan = Lifespan()
    app = Future(lifespan=lifespan, config=config)
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/", headers={"Host": f"api.{test_domain}"})
        assert response.status_code == 200
        assert response.text == "✨ Welcome to Future! ✨"


async def test_application_subdomains_double_subdomain() -> None:
    routes = [
        RouteGroup(
            name="test_application_routes",
            subdomain="api",
            routes=[
                Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # type: ignore[reportAttributeAccessIssue]
            ],
        ),
    ]

    test_domain = "api.api.example.com"
    config = {
        "APP_NAME": "test_application_subdomains",
        "APP_DOMAIN": test_domain,
        "APP_DEBUG": False,
    }
    lifespan = Lifespan()
    app = Future(lifespan=lifespan, config=config)
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/", headers={"Host": f"api.{test_domain}"})
        assert response.status_code == 200
        assert response.text == "✨ Welcome to Future! ✨"


async def test_route_single_without_domain() -> None:
    routes = [
        Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # type: ignore[reportAttributeAccessIssue]
    ]

    config = {
        "APP_NAME": "test",
        "APP_DEBUG": False,
    }
    lifespan = Lifespan()
    app = Future(lifespan=lifespan, config=config)
    app.add_routes(routes=routes)

    # You should use `FutureTestClient` as a context manager, to ensure that the lifespan is called.
    async with FutureTestClient(app) as client:
        # Application's lifespan is called on entering the block.
        response = await client.get("http://127.0.0.1/")
        assert response.status_code == 200
        assert response.text == "✨ Welcome to Future! ✨"
    # And the lifespan's teardown is run when exiting the block.


async def test_route_single_with_domain() -> None:
    routes = [
        Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # type: ignore[reportAttributeAccessIssue]
    ]

    config = {
        "APP_NAME": "test",
        "APP_DOMAIN": "example.com",
        "APP_DEBUG": False,
    }
    lifespan = Lifespan()
    app = Future(lifespan=lifespan, config=config)
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/", headers={"Host": "example.com"})
        assert response.status_code == 200
        assert response.text == "✨ Welcome to Future! ✨"


async def test_route_group() -> None:
    routes = [
        RouteGroup(
            subdomain="api",
            name="test",
            routes=[
                Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # type: ignore[reportAttributeAccessIssue]
            ],
        ),
    ]

    config = {
        "APP_NAME": "test",
        "APP_DOMAIN": "example.com",
        "APP_DEBUG": False,
    }
    lifespan = Lifespan()
    app = Future(lifespan=lifespan, config=config)
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/", headers={"Host": "api.example.com"})
        assert response.status_code == 200
        assert response.text == "✨ Welcome to Future! ✨"


async def test_single_route_with_domain() -> None:
    routes = [
        Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # type: ignore[reportAttributeAccessIssue]
    ]

    config = {
        "APP_NAME": "test",
        "APP_DOMAIN": "example.com",
        "APP_DEBUG": False,
    }
    lifespan = Lifespan()
    app = Future(lifespan=lifespan, config=config)
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/", headers={"Host": "example.com"})
        assert response.status_code == 200
        assert response.text == "✨ Welcome to Future! ✨"


async def test_domain_routing() -> None:
    routes = [
        RouteGroup(
            name="test",
            routes=[
                Get(path="/", endpoint=WelcomeController.root, name="Welcome"),  # type: ignore[reportAttributeAccessIssue]
            ],
        ),
    ]

    config = {
        "APP_NAME": "test",
        "APP_DOMAIN": "example.com",
        "APP_DEBUG": False,
    }
    lifespan = Lifespan()
    app = Future(lifespan=lifespan, config=config)
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/", headers={"Host": "example.com"})
        assert response.status_code == 200
        assert response.text == "✨ Welcome to Future! ✨"


async def test_route_group_prefix_with_root_path() -> None:
    """prefix=/indexes + Get('/') must match /indexes and /indexes/, not only /indexes/."""
    routes = [
        RouteGroup(
            name="Indexes",
            prefix="/indexes",
            routes=[
                Get("/", WelcomeController.root, "indexes"),  # type: ignore[reportAttributeAccessIssue]
                Get("/<str:index_id>", WelcomeController.root, "indexes.show"),  # type: ignore[reportAttributeAccessIssue]
            ],
        ),
    ]
    config = {"APP_NAME": "test", "APP_DOMAIN": "example.com", "APP_DEBUG": False}
    app = Future(lifespan=Lifespan(), config=config)
    app.add_routes(routes=routes)

    index_routes = [cfg["route"] for cfg in app.routes["example.com"].values() if cfg["route"].name == "indexes"]
    assert len(index_routes) == 1
    assert index_routes[0].path == "/indexes"
    assert index_routes[0]._rx.pattern == b"^/indexes/?$"

    async with FutureTestClient(app) as client:
        for path in ("/indexes", "/indexes/"):
            response = await client.get(f"http://127.0.0.1{path}", headers={"Host": "example.com"})
            assert response.status_code == 200, path
            assert response.text == "✨ Welcome to Future! ✨"
