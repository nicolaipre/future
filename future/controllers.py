from textwrap import dedent
from typing import Any

from future.graphql import queries, schema
from future.requests import Request
from future.responses import HTMLResponse, JSONResponse, Response, WebSocketResponse
from future.settings import API_SPEC


"""
✅ Why defining class methods without self is valid in Python:
- self is a naming convention, not a keyword — Python doesn't require it.
- Functions defined in a class become methods only when called via an instance.
- If you call them on the class (ClassName.method()), no self is passed — so it's valid to omit it.
- The code is valid Python and works without error as long as you don't instantiate the class.
- Linters like Pylance assume all methods are instance methods unless decorated — but this is just a warning, not a Python error.
- Python allows any name or no parameter at all; def method(): ... inside a class is legal and callable from the class.
- Adding self when it's unused is misleading and violates clarity — it implies instance state is accessed when it's not.
- Metaclasses or conventions can be used to treat methods as static implicitly — decorators are not required for static behavior.
- This pattern is commonly used in frameworks (e.g., FastAPI) where function-style handlers live in classes but are not instance-bound.
"""


class Controller:
    # __new__ is inherited automatically so we do not have to super.__init__() classes that extend it
    def __new__(cls, *args: Any, **kwargs: Any) -> "Controller":
        raise TypeError(f"{cls.__name__} may not be instantiated. This is a hack to prevent mistakes and helps us keep controller methods static.")


class GraphQLController(Controller):
    async def query(request: Request) -> JSONResponse:  # type: ignore[reportSelfClsParameterName]
        # body = await request.body()
        # if not body:
        #    query = queries["GetEverything"]
        # else:
        # try:
        # query_data = json.loads(query)
        # query = {"query": query}
        # query = query_data["query"]
        # except (json.JSONDecodeError, KeyError):
        #    return JSONResponse(data={"error": "Invalid JSON or missing query"}, status=400)

        query = queries["GetEverything"]
        result = await schema.execute(query)
        if result.errors:
            return JSONResponse(data={"errors": [str(error) for error in result.errors]}, status=400)
        return JSONResponse(data=result.data)


class DebugController(Controller):
    async def test(request: Request) -> Response:  # type: ignore[no-self]
        return Response(body="lolok")

    async def hello(request: Request) -> JSONResponse:  # type: ignore[no-self]
        return JSONResponse({"message": "hi"})

    async def test_data(request: Request, data: Any) -> Response:  # type: ignore[no-self]
        return Response(body=f"data: {data}", status=200)

    async def some_handler(request: Request, **params: Any) -> Response:  # type: ignore[no-self]
        return Response(body=f"Handled with params: {params}", status=200)

    async def ping(request: Request) -> Response:  # type: ignore[no-self]
        return Response(body="Pong\n")

    async def test2(request: Request, data: Any) -> Response:  # type: ignore[no-self]
        return Response(body=data, status=200)

    async def args(request: Request, user_id: Any, arg2: Any) -> Response:  # type: ignore[no-self]
        return Response(body=f"{user_id=}, {arg2=}\n")


class WelcomeController(Controller):
    async def root(request: Request) -> Response:  # type: ignore[no-self]
        return Response(body="✨ Welcome to Future! ✨")


class OpenAPIController(Controller):
    """Controller for OpenAPI documentation endpoints."""

    async def openapi(request: Request) -> Response:  # type: ignore[no-self]
        """Serve the OpenAPI schema as JSON."""
        return JSONResponse(data=API_SPEC, status=200)

    async def redoc(request: Request) -> Response:  # type: ignore[no-self]
        """Serve ReDoc HTML."""
        html = dedent(
            f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Redoc</title>
                <meta charset="utf-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
            </head>
            <body>
                <redoc spec-url="{f"{request.scheme}://{request.host}/openapi.json"}"></redoc>
                <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"> </script>
            </body>
            </html>
            """
        )
        return HTMLResponse(html)

    async def swagger_config(request: Request) -> Response:  # type: ignore[no-self]
        """Serve Swagger configuration."""
        swagger_config = {
            "apisSorter": "alpha",
            "operationsSorter": "alpha",
            "docExpansion": "full",
        }
        return JSONResponse(data=swagger_config, status=200)

    async def swagger(request: Request) -> Response:  # type: ignore[no-self]
        """Serve Swagger UI HTML."""
        html = dedent(
            f"""
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.12.1/swagger-ui.min.css">
                    <title>OpenAPI Swagger</title>
                    <style>
                        body {{
                            margin: 0;
                            padding: 0;
                        }}
                    </style>
                </head>
                <body>
                    <div id="openapi"></div>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.12.1/swagger-ui-bundle.min.js"></script>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.12.1/swagger-ui-standalone-preset.min.js"></script>
                    <script>
                        window.onload = function () {{
                            const ui = SwaggerUIBundle({{
                                url: "{request.scheme}://{request.host}/openapi.json",
                                dom_id: "#openapi",
                                configUrl: "{request.scheme}://{request.host}/swagger-config",
                                deepLinking: true,
                                presets: [
                                    SwaggerUIBundle.presets.apis,
                                    SwaggerUIStandalonePreset
                                ],
                                plugins: [
                                    SwaggerUIBundle.plugins.DownloadUrl
                                ],
                                layout: "StandaloneLayout"
                            }})
                        }}
                    </script>
                </body>
            </html>
            """
        )
        return HTMLResponse(html)


class WebSocketController(Controller):
    """Controller for WebSocket endpoints."""

    async def websocket_handler(request: Request, **params: Any) -> WebSocketResponse:  # type: ignore[no-self]
        """WebSocket handler that returns a WebSocketResponse."""
        # Get the message from the request (if any)
        message = params.get("message", "Hello from WebSocket!")
        return WebSocketResponse(message=message)
