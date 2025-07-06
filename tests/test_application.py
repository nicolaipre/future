from future.application import Future
from future.controllers import WelcomeController
from future.lifespan import Lifespan
from future.routing import Get, RouteGroup
from future.testclient import FutureTestClient


async def test_application_setup() -> None:
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
    config: dict[str, str | bool] = {
        "APP_NAME": "test_application_setup",
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
