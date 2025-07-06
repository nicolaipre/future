from future.application import Future
from future.controllers import GraphQLController
from future.lifespan import Lifespan
from future.routing import Get, RouteGroup
from future.testclient import FutureTestClient


async def test_graphql() -> None:
    routes = [
        RouteGroup(
            subdomain="api",
            name="test",
            routes=[
                Get(path="/graphql", endpoint=GraphQLController.query, name="GraphQL")  # type: ignore[reportAttributeAccessIssue]
            ],
        ),
    ]
    lifespan = Lifespan()
    app = Future(lifespan=lifespan, config={"APP_DOMAIN": "example.com"})
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        response = await client.get("http://127.0.0.1/graphql", headers={"Host": "api.example.com"})
        assert response.status_code == 200
        # GraphQL should return JSON data
        assert "users" in response.text
        assert "posts" in response.text
