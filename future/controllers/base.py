from future.request import Request
from future.response import Response


class Controller:
    def __init__(self, request: Request, response: Response) -> None:
        self.request = request
        self.response = response
