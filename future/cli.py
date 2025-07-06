import argparse
import os
import sys

from pathlib import Path
from typing import Any


# Boilerplate templates (copied from boilerplate.py)
APP_ROOT = "app"
APP_DIRS = ["config", "controllers", "middleware", "models", "plugins"]
PROJECT_FILES = [".env.example", ".gitignore", "LICENSE", "pyproject.toml", "README.md"]
README_MD = """\
# ✨ Future - Broilerplate ✨
Boilerplate example for Future
"""
ENV_EXAMPLE = """\
# Application settings
APP_NAME=Example
APP_VERSION=1.0
APP_DESCRIPTION=Description
APP_DOMAIN=example.com
APP_HOST=127.0.0.1
APP_PORT=8000
APP_DEBUG=False
APP_ACCESS_LOG=True
APP_WORKERS=1
APP_KEY=REPLACE_WITH_GENERATED_SECRET_KEY
APP_SSO=False
APP_REGISTRATION=False

# Database settings
DB_DRIVER=sqlite
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=database.sqlite
DB_USERNAME=
DB_PASSWORD=
DB_LOGGING=False
DB_OPTIONS=

# Elasticsearch settings
ELASTIC_HOST=127.0.0.1
ELASTIC_PORT=9200
ELASTIC_USER=
ELASTIC_PASS=
"""
PYPROJECT_TOML = """\
[tool.poetry]
name = "Future - Boilerplate"
version = "0.0.1"
description = "This is a boilerplate example for Future."
authors = ["nicolaipre"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.12"
python-dotenv = "^1.0.1"
future = {git = "ssh://git@github.com/Defendinary/future.git"}

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""
LICENSE = """\
MIT License

Copyright (c) 2025 Defendinary

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the \"Software\"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
GITIGNORE = ".idea/\n.vscode/\n.env\n.venv\npoetry.lock\n__pycache__/\n"

# Additional template files from boilerplate.py
APP_ROUTES = """\
from app.config.settings import APP_DEBUG, APP_DOMAIN, APP_NAME, APP_VERSION, APP_DESCRIPTION, API_SPEC
from app.controllers.ApiController import ExampleController
from app.middleware.ExampleMiddleware import ExampleMiddleware
from future.routing import RouteGroup, Get, Post


ROUTES = [
    RouteGroup(
        name="Example Group",
        #subdomain="",
        #prefix="/",
        middlewares=[ExampleMiddleware],
        routes=[
            Get("/", ExampleController.example, name="Example Route"),
        ]
    ),
]
"""

EXAMPLE_PLUGIN = """\
from future.plugins import Plugin


class ExamplePlugin(Plugin):
    pass
"""

EXAMPLE_MODEL = """\
from future.models import Model


class ExampleModel(Model):
    pass
"""

EXAMPLE_MIDDLEWARE = """\
from future.middleware import Middleware
from future.requests import Request
from future.responses import Response


class ExampleMiddleware(Middleware):
    name = "ExampleMiddleware"
    attach_to = "request"
    priority = 0

    def intercept(request: Request):
        return Response(b"OK")
"""

EXAMPLE_CONTROLLER = """\
from future.controllers import Controller
from future.requests import Request
from future.responses import Response


class ExampleController(Controller):
    async def example(request: Request):
        return Response(body=b"ExampleController", status=200)
"""

CONFIG_DATABASE = """\
from app.config.environment import DB_DRIVER, DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD, DB_OPTIONS, DB_DATABASE
from future.database import Database

mysql = Database(
    driver=DB_DRIVER,
    host=DB_HOST,
    port=DB_PORT,
    username=DB_USERNAME,
    password=DB_PASSWORD,
    database=DB_DATABASE,
    options=DB_OPTIONS,
)

database = mysql.session()
"""

CONFIG_SETTINGS = """\
from os import environ as env
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

# Application settings sourced from .env
APP_NAME = str(env.get("APP_NAME", "Future"))
APP_VERSION = str(env.get("APP_VERSION", "1.0"))
APP_DESCRIPTION = str(env.get("APP_DESCRIPTION", "A short description"))
APP_DEBUG = bool(env.get("APP_DEBUG", True))
APP_LOG_LEVEL = str("DEBUG" if APP_DEBUG else env.get("APP_LOG_LEVEL", "INFO"))
APP_ACCESS_LOG = bool(env.get("APP_ACCESS_LOG", False))
APP_WORKERS = int(env.get("APP_WORKERS", 4))
APP_HOST = str(env.get("APP_HOST", "127.0.0.1"))
APP_PORT = int(env.get("APP_PORT", 8000))
APP_SSO = bool(env.get("APP_SSO", False))
APP_KEY = str(env.get("APP_KEY", "secret"))
APP_REGISTRATION = bool(env.get("APP_REGISTRATION", False))
APP_SSL_CERT_FILE = str(env.get("APP_SSL_CERT_FILE", "./cert.pem"))
APP_SSL_KEY_FILE = str(env.get("APP_SSL_KEY_FILE", "./key.pem"))
APP_SSL_PASSPHRASE = str(env.get("APP_SSL_PASSPHRASE", "changeme"))
APP_DOMAIN = str(env.get("APP_DOMAIN", "example.com"))

# Database settings sourced from .env
DB_DRIVER = str(env.get("DB_DRIVER", "sqlite"))
DB_HOST = str(env.get("DB_HOST", "127.0.0.1"))
DB_PORT = int(env.get("DB_PORT", 3306))
DB_DATABASE = str(env.get("DB_DATABASE", None))
DB_USERNAME = str(env.get("DB_USERNAME", None))
DB_PASSWORD = str(env.get("DB_PASSWORD", None))
DB_LOGGING = bool(env.get("DB_LOGGING", True))
DB_OPTIONS = str(env.get("DB_OPTIONS", None))

# Elasticsearch settings sourced from .env
ELASTIC_HOST = str(env.get("ELASTIC_HOST", "127.0.0.1"))
ELASTIC_PORT = int(env.get("ELASTIC_PORT", 9200))
ELASTIC_USER = str(env.get("ELASTIC_USER", None))
ELASTIC_PASS = str(env.get("ELASTIC_PASS", None))

# API Spec generated based on settings
API_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
    },
    "paths": {},
}
"""

RUN_PY = """\
from app.routes import ROUTES
from future.application import Future
from future.lifespan import Lifespan
from future.settings import APP_NAME, APP_DOMAIN, APP_DEBUG, APP_LOG_LEVEL

# Startup tasks (run once when app starts)
startup_tasks = [
    # Add your startup tasks here
]

# Shutdown tasks (run once when app stops)
shutdown_tasks = [
    # Add your shutdown tasks here
]

# Cron jobs (run periodically)
cronjobs = [
    # Add your cron jobs here
]

lifespan = Lifespan(startup_tasks, shutdown_tasks, cronjobs)

config = {
    "APP_NAME": APP_NAME,
    "APP_DOMAIN": APP_DOMAIN,
    "APP_DEBUG": APP_DEBUG,
    "APP_LOG_LEVEL": APP_LOG_LEVEL,
}

app = Future(lifespan=lifespan, config=config)
app.add_routes(routes=ROUTES)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, workers=1)
"""


def get_app_from_project() -> Any:
    """Dynamically import the app from the current project."""
    import importlib.util

    # Add current directory to Python path for scaffolded projects
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())

    # Try to import from run.py first
    if os.path.exists("run.py"):
        spec = importlib.util.spec_from_file_location("run", "run.py")
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "app"):
                return module.app

    # Try to import from example (for development)
    try:
        from example import app

        return app
    except ImportError:
        pass

    print("Error: Could not find app instance. Make sure you're in a Future project directory.")
    print("Expected to find app in: run.py or example.py")
    sys.exit(1)


def print_routes() -> None:
    print("\n=== ROUTE MAPPING ===\n")
    app = get_app_from_project()
    routes = getattr(app, "routes", {})
    for domain, domain_routes in routes.items():
        for path, route_info in domain_routes.items():
            schema = "ws://" if "ws" in path else "http://"
            # Remove double slashes
            full_path = (schema + domain + path).replace("//", "/", 1)
            # Extract middleware names
            middleware_levels = route_info.get("middleware", {}).get("levels", [])
            middleware_names = []
            for level in middleware_levels:
                for middleware in level.get("before", []) + level.get("after", []):
                    if hasattr(middleware, "name"):
                        middleware_names.append(middleware.name)
                    else:
                        middleware_names.append(middleware.__name__)
            middleware_str = f" ({', '.join(middleware_names)})" if middleware_names else ""
            # Determine method (GET for HTTP, WEBSOCKET for WebSocket)
            method = "WEBSOCKET" if "ws" in path else "GET"
            print(f"{method} {full_path}{middleware_str}")


def scaffold_project(target_dir: str) -> None:
    target = Path(target_dir)
    if target.exists():
        print(f"Directory {target} already exists.")
        sys.exit(1)

    # Create main app directory
    app_dir = target / APP_ROOT
    app_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    for d in APP_DIRS:
        (app_dir / d).mkdir(parents=True, exist_ok=True)

    # Create root level files
    (target / "README.md").write_text(README_MD)
    (target / ".env.example").write_text(ENV_EXAMPLE)
    (target / "pyproject.toml").write_text(PYPROJECT_TOML)
    (target / "LICENSE").write_text(LICENSE)
    (target / ".gitignore").write_text(GITIGNORE)
    (target / "run.py").write_text(RUN_PY)

    # Create app-specific files
    (app_dir / "__init__.py").write_text("")
    (app_dir / "routes.py").write_text(APP_ROUTES)
    (app_dir / "config" / "__init__.py").write_text("")
    (app_dir / "config" / "settings.py").write_text(CONFIG_SETTINGS)
    (app_dir / "config" / "database.py").write_text(CONFIG_DATABASE)
    (app_dir / "controllers" / "__init__.py").write_text("")
    (app_dir / "controllers" / "ApiController.py").write_text(EXAMPLE_CONTROLLER)
    (app_dir / "middleware" / "__init__.py").write_text("")
    (app_dir / "middleware" / "ExampleMiddleware.py").write_text(EXAMPLE_MIDDLEWARE)
    (app_dir / "models" / "__init__.py").write_text("")
    (app_dir / "models" / "ExampleModel.py").write_text(EXAMPLE_MODEL)
    (app_dir / "plugins" / "__init__.py").write_text("")
    (app_dir / "plugins" / "ExamplePlugin.py").write_text(EXAMPLE_PLUGIN)

    print(f"Scaffolded new Future project at {target.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Future Framework CLI")
    subparsers = parser.add_subparsers(dest="command")

    # future routes
    subparsers.add_parser("routes", help="List all routes")

    # future init . or future init <project>
    init_parser = subparsers.add_parser("init", help="Scaffold a new project")
    init_parser.add_argument("target", nargs="?", default=".", help="Target directory (default: current directory)")

    args = parser.parse_args()

    if args.command == "routes":
        print_routes()
    elif args.command == "init":
        if args.target == ".":
            scaffold_project(os.getcwd())
        else:
            scaffold_project(os.path.join(os.getcwd(), args.target))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
