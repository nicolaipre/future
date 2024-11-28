from app.config.environment import APP_DEBUG, APP_DOMAIN, APP_NAME, APP_VERSION, APP_DESCRIPTION, API_SPEC
from app.controllers.ApiController import ExampleController
from future.routing import RouteGroup, Get, Post


ROUTES = [
    RouteGroup(
        name="Example Group",
        #subdomain="",
        #prefix="/",
        middleware=["example"],
        routes=[
            Get("/", ExampleController.root, name="Example Route"),
        ]
    ),
]
