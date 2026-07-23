from future.application import Future
from future.controllers import GraphQLController
from future.lifespan import Lifespan
from future.routing import Post, RouteGroup
from future.testing import FutureTestClient


async def test_graphql() -> None:
    routes = [
        RouteGroup(
            subdomain="api",
            name="test",
            routes=[
                Post(path="/graphql", endpoint=GraphQLController.query, name="GraphQL")  # type: ignore[reportAttributeAccessIssue]
            ],
        ),
    ]
    lifespan = Lifespan()
    app = Future(lifespan=lifespan, config={"APP_DOMAIN": "example.com"})
    app.add_routes(routes=routes)

    query = "{ users { id name email } posts { id title } }"
    async with FutureTestClient(app) as client:
        response = await client.post(
            "http://127.0.0.1/graphql",
            headers={"Host": "api.example.com"},
            json={"query": query},
        )
        assert response.status_code == 200
        body = response.json()
        assert "data" in body
        assert "users" in body["data"]
        assert "posts" in body["data"]


async def test_graphql_missing_query() -> None:
    routes = [
        RouteGroup(
            subdomain="api",
            name="test",
            routes=[
                Post(path="/graphql", endpoint=GraphQLController.query, name="GraphQL")  # type: ignore[reportAttributeAccessIssue]
            ],
        ),
    ]
    app = Future(lifespan=Lifespan(), config={"APP_DOMAIN": "example.com"})
    app.add_routes(routes=routes)
    async with FutureTestClient(app) as client:
        response = await client.post("http://127.0.0.1/graphql", headers={"Host": "api.example.com"}, json={})
        assert response.status_code == 400
        assert "errors" in response.json()
