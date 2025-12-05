from future.application import Future
from future.controllers import WelcomeController
from future.lifespan import Lifespan
from future.routing import Get, Post, RouteGroup
from future.testclient import FutureTestClient


async def test_post_request() -> None:
    """Test POST request with JSON data."""
    from future.requests import Request
    from future.responses import Response
    
    async def post_handler(request: Request) -> Response:
        data = await request.json()
        return Response(body=f"Received: {data.get('message', 'no message')}", status=200)
    
    routes = [
        Post(path="/post", endpoint=post_handler, name="POST Handler"),
    ]
    
    config = {
        "APP_NAME": "test_post",
        "APP_DOMAIN": "",
        "APP_DEBUG": False,
    }
    lifespan = Lifespan()
    app = Future(lifespan=lifespan, config=config)
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        json_data = {"message": "Hello POST", "number": 42}
        response = await client.post(
            "http://127.0.0.1/post",
            json=json_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        assert "Hello POST" in response.text

async def test_post_form_data() -> None:
    """Test POST request with form data."""
    from future.requests import Request
    from future.responses import Response
    
    async def form_handler(request: Request) -> Response:
        # For form data, we'll need to parse it manually since we don't have a form() method yet
        body = await request.body()
        form_data = body.decode('utf-8')
        return Response(body=f"Received form: {form_data}", status=200)
    
    routes = [
        Post(path="/form", endpoint=form_handler, name="Form Handler"),
    ]
    
    config = {
        "APP_NAME": "test_post_form",
        "APP_DOMAIN": "",
        "APP_DEBUG": False,
    }
    lifespan = Lifespan()
    app = Future(lifespan=lifespan, config=config)
    app.add_routes(routes=routes)

    async with FutureTestClient(app) as client:
        form_data = "Some example post data"
        response = await client.post(
            "http://127.0.0.1/form",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        assert "Some example post data" in response.text
