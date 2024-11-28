#!/usr/bin/env python3

"""
Runs the application for local development. This file should not be used to start the
application for production.

Refer to https://www.uvicorn.org/deployment/ for production deployments.
"""

from future.application import Future
from future.controller import WelcomeController
from future.middleware import ResponseCodeConfuser, TestMiddlewareRequest, TestMiddlewareResponse
from future.routing import RouteGroup, Get
import os


routes = [
    RouteGroup(
        name="test",
        #subdomain="api",
        middlewares=[
            TestMiddlewareRequest,
            TestMiddlewareResponse,
        ],
        routes=[
            Get(path='/', endpoint=WelcomeController.root, name="Welcome"),
        ],
    ),
    
    # Also test Single Routes
    Get(path='/ping', endpoint=WelcomeController.ping, name="Ping", middlewares=[TestMiddlewareRequest]),
]

app = Future(name="Future", debug=False, domain="example.com:8000")
app.add_routes(routes)
print(app.routes)

if __name__ == "__main__":
    #os.environ["APP_ENV"] = "dev"
    #port = int(os.environ.get("APP_PORT", 44777))
    app.run(host="0.0.0.0", port=8000, workers=1)