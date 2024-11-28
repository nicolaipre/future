from future.controllers import Controller
from future.requests import Request
from future.responses import Response


class ExampleController(Controller):
    async def example(request: Request):
        return Response(body=b"ExampleController", status=200)
