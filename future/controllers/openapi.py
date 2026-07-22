from textwrap import dedent
import json

from future.controllers.base import Controller
from future.openapi import get_openapi_config, get_spec, path_prefix
from future.response import Response


class OpenAPIController(Controller):
    """Controller for OpenAPI documentation endpoints."""

    async def openapi(self) -> Response:
        """Serve the OpenAPI schema as JSON."""
        return self.response.json(get_spec(), status=200)

    async def redoc(self) -> Response:
        """Serve ReDoc HTML (OSS) or Redocly Reference Docs when license_key is set."""
        spec = f"{self.request.scheme}://{self.request.host}{path_prefix()}/openapi.json"
        license_key = (get_openapi_config().get("redocly_license_key") or "").strip()
        if license_key:
            # Paid Redocly Reference Docs (includes Try it). Requires a valid license.
            # https://cdn.redoc.ly/reference-docs/latest/redocly-reference-docs.min.js
            key_js = json.dumps(license_key)
            html = dedent(
                f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Redocly Reference</title>
                    <meta charset="utf-8"/>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
                    <style>body {{ margin: 0; padding: 0; }}</style>
                </head>
                <body>
                    <div id="redocly_container"></div>
                    <script src="https://cdn.redoc.ly/reference-docs/latest/redocly-reference-docs.min.js"></script>
                    <script>
                        RedoclyReferenceDocs.init(
                            {json.dumps(spec)},
                            {{ licenseKey: {key_js} }},
                            document.querySelector("#redocly_container")
                        );
                    </script>
                </body>
                </html>
                """
            )
            return self.response.html(html)
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
                <redoc spec-url="{spec}"></redoc>
                <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"> </script>
            </body>
            </html>
            """
        )
        return self.response.html(html)

    async def swagger_config(self) -> Response:
        """Serve Swagger configuration."""
        swagger_config = {
            "apisSorter": "alpha",
            "operationsSorter": "alpha",
            "docExpansion": "full",
        }
        return self.response.json(swagger_config, status=200)

    async def swagger(self) -> Response:
        """Serve Swagger UI HTML."""
        base = f"{self.request.scheme}://{self.request.host}{path_prefix()}"
        html = dedent(
            f"""
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.0/swagger-ui.css">
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
                    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.0/swagger-ui-bundle.js"></script>
                    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.0/swagger-ui-standalone-preset.js"></script>
                    <script>
                        window.addEventListener("load", function () {{
                            if (typeof SwaggerUIBundle === "undefined") {{
                                document.getElementById("openapi").textContent = "Failed to load Swagger UI (CDN blocked or offline).";
                                return;
                            }}
                            SwaggerUIBundle({{
                                url: "{base}/openapi.json",
                                dom_id: "#openapi",
                                configUrl: "{base}/swagger-config",
                                deepLinking: true,
                                presets: [
                                    SwaggerUIBundle.presets.apis,
                                    SwaggerUIStandalonePreset
                                ],
                                plugins: [
                                    SwaggerUIBundle.plugins.DownloadUrl
                                ],
                                layout: "StandaloneLayout"
                            }});
                        }});
                    </script>
                </body>
            </html>
            """
        )
        return self.response.html(html)

    async def scalar(self) -> Response:
        """Serve Scalar API reference HTML."""
        spec = f"{self.request.scheme}://{self.request.host}{path_prefix()}/openapi.json"
        html = dedent(
            f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Scalar API Reference</title>
                <meta charset="utf-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body>
                <script id="api-reference" data-url="{spec}"></script>
                <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
            </body>
            </html>
            """
        )
        return self.response.html(html)

    async def rapidoc(self) -> Response:
        """Serve RapiDoc HTML."""
        spec = f"{self.request.scheme}://{self.request.host}{path_prefix()}/openapi.json"
        html = dedent(
            f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>RapiDoc</title>
                <meta charset="utf-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <script type="module" src="https://unpkg.com/rapidoc/dist/rapidoc-min.js"></script>
            </head>
            <body>
                <rapi-doc spec-url="{spec}" render-style="read" show-header="true" allow-try="true"></rapi-doc>
            </body>
            </html>
            """
        )
        return self.response.html(html)
