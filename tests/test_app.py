import pytest

from star.application import Star
from star.routing import RouteGroup, Get
from star.controllers import WelcomeController


def test_app() -> None:
    routes = [
        RouteGroup(
            name="testroutes",
            #subdomain="api",
            routes=[
                Get(path="/", endpoint=WelcomeController.hello, name="Welcome"),
            ]
        ),
    ]

    app = Star(name="testapp", debug=False, domain="example.com")
    app.add_routes(routes=routes)

    #if __name__ == '__main__':
        #app.run(host="0.0.0.0", port=8000, workers=4)
