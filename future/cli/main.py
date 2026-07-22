import argparse
import os
import sys

from pathlib import Path
from typing import Any


# Boilerplate templates for `future init`
APP_ROOT = "app"
APP_DIRS = ["config", "controllers", "middleware", "models", "plugins", "tasks"]
PROJECT_FILES = [".env.example", ".gitignore", "LICENSE", "pyproject.toml", "README.md"]
README_MD = """\
# Future boilerplate

Scaffolded with `future init`.

```bash
cp .env.example .env   # DB_DATABASE=database → database.sqlite
poetry install
poetry run future make:migration ExampleModel
poetry run future migrate
poetry run future make:seed ExampleModel
poetry run future seed
poetry run python run.py
poetry run future routes
```
"""
ENV_EXAMPLE = """\
# Application settings
APP_NAME=Example
APP_VERSION=1.0
APP_DESCRIPTION=Description
APP_DOMAIN=example.com
APP_HOST=127.0.0.1
APP_PORT=8000
APP_DEBUG=True
APP_ACCESS_LOG=True
APP_WORKERS=1
APP_KEY=REPLACE_WITH_GENERATED_SECRET_KEY

# Database settings (SQLite by default — no server required)
DB_DATABASE=database

# Optional MySQL (switch app/config/Database.py to MySQL and set these)
# DB_HOST=127.0.0.1
# DB_PORT=3306
# DB_DATABASE=future
# DB_USERNAME=root
# DB_PASSWORD=
"""
PYPROJECT_TOML = """\
[tool.poetry]
name = "future-boilerplate"
version = "0.0.1"
description = "Boilerplate app for the Future framework."
authors = ["nicolaipre"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.12"
python-dotenv = "^1.0.1"
future = {git = "ssh://git@github.com/nicolaipre/future.git"}
# Or, while developing Future next to this app:
# future = { path = "../future", develop = true }

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""
LICENSE = """\
MIT License

Copyright (c) 2025 nicolaipre

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
GITIGNORE = ".idea/\n.vscode/\n.env\n.venv\npoetry.lock\n__pycache__/\n*.sqlite\n*.sqlite3\n"

APP_ROUTES = """\
from app.controllers.ExampleController import ExampleController
from app.middleware.ExampleMiddleware import ExampleMiddleware
from future.openapi import openapi_routes
from future.routing import RouteGroup, Get


routes = [
    RouteGroup(
        name="Docs",
        prefix="/api",
        # middlewares=[ExampleMiddleware],  # protect docs if needed
        routes=openapi_routes(uis=["swagger", "redoc", "scalar", "rapidoc"]),
    ),
    RouteGroup(
        name="Main",
        middlewares=[ExampleMiddleware],
        routes=[
            Get("/", ExampleController.index, "home"),
            Get("/examples", ExampleController.index, "examples"),
            Get("/examples/<id>", ExampleController.show, "example"),
        ],
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
from datetime import datetime


class ExampleModel(Model):
    __connection__ = "default"
    # __table__ = "example_models"  # optional; otherwise tableized class name

    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
"""

EXAMPLE_MIDDLEWARE = """\
from future.middleware import Middleware
from future.response import Response
from typing import Optional


class ExampleMiddleware(Middleware):
    name = "ExampleMiddleware"
    priority = 0

    async def before(self) -> Optional[Response]:
        return None

    async def after(self) -> Optional[Response]:
        return None
"""

EXAMPLE_CONTROLLER = """\
from future.controllers import Controller
from future.response import Response
from app.models.ExampleModel import ExampleModel


class ExampleController(Controller):
    async def index(self) -> Response:
        examples = ExampleModel.all()
        return self.response.json([example.to_dict() for example in examples], status=200)

    async def show(self, id: str) -> Response:
        example = ExampleModel.find(id)
        if example is None:
            return self.response.json({"error": "Not found"}, status=404)
        return self.response.json(example.to_dict(), status=200)
"""

EXAMPLE_TASK = """\
\"\"\"
Example task — pass to Lifespan cron_tasks via Task(..., func=run).
\"\"\"


def run():
    pass
"""

CONFIG_DATABASE = """\
from future.databases.SQLite import SQLite
from app.config.Settings import DB_DATABASE

# Default driver: SQLite (local file). Swap in MySQL when you need a server.
# Future(config={"DATABASES": DATABASES}) registers Connections at boot.
DATABASES = {
    "default": "sqlite",
    "sqlite": SQLite(database=DB_DATABASE),
}
"""

CONFIG_SETTINGS = """\
from os import environ as env
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

# Application settings sourced from .env
APP_NAME = str(env.get("APP_NAME", "Future"))
APP_VERSION = str(env.get("APP_VERSION", "1.0"))
APP_DESCRIPTION = str(env.get("APP_DESCRIPTION", "A short description"))
APP_DEBUG = env.get("APP_DEBUG", "False").lower() == "true"
APP_LOG_LEVEL = str("DEBUG" if APP_DEBUG else env.get("APP_LOG_LEVEL", "INFO"))
APP_ACCESS_LOG = env.get("APP_ACCESS_LOG", "False").lower() == "true"
APP_WORKERS = int(env.get("APP_WORKERS", 1))
APP_HOST = str(env.get("APP_HOST", "127.0.0.1"))
APP_PORT = int(env.get("APP_PORT", 8000))
APP_KEY = str(env.get("APP_KEY", "secret"))
APP_DOMAIN = str(env.get("APP_DOMAIN", "example.com"))

# Database settings sourced from .env (name only; SQLite appends .sqlite)
DB_DATABASE = str(env.get("DB_DATABASE", "database"))
DB_HOST = str(env.get("DB_HOST", "127.0.0.1"))
DB_PORT = int(env.get("DB_PORT", 3306))
DB_USERNAME = str(env.get("DB_USERNAME", "root"))
DB_PASSWORD = str(env.get("DB_PASSWORD", ""))
DB_LOGGING = env.get("DB_LOGGING", "False").lower() == "true"
"""

RUN_PY = """\
from app.config.Settings import APP_HOST, APP_PORT, APP_DEBUG, APP_WORKERS, APP_NAME, APP_DOMAIN
from app.config.Database import DATABASES
from app.routes import routes
from future.application import Future
from future.lifespan import Lifespan

# Tasks that will run on startup:
startup_tasks = [
    # Task()
]

# Tasks that will run on shutdown:
shutdown_tasks = [
    # Task()
]

# Tasks that will run with intervals using a cron-like scheduler:
cron_tasks = [
    # Task("Example", interval=1, unit=Unit.HOURS, func=run),
]

config = {
    "APP_DOMAIN": APP_DOMAIN,
    "APP_NAME": APP_NAME,
    "APP_HOST": APP_HOST,
    "APP_PORT": APP_PORT,
    "APP_DEBUG": APP_DEBUG,
    "DATABASES": DATABASES,
    "OPENAPI": {
        "enabled": True,
        "uis": ["swagger", "redoc", "scalar", "rapidoc"],
        "auto_routes": False,
        "path_prefix": "",
        # "redocly_license_key": "",  # paid Reference Docs (Try it); omit for OSS ReDoc
    },
}

lifespan = Lifespan(startup_tasks=startup_tasks, shutdown_tasks=shutdown_tasks, cron_tasks=cron_tasks)
app = Future(lifespan=lifespan, config=config)
app.add_routes(routes)

if __name__ == "__main__":
    app.run(host=APP_HOST, port=APP_PORT, workers=APP_WORKERS)
"""


def get_app_from_project() -> Any:
    """Dynamically import the app from the current project."""
    import importlib.util

    # Add current directory to Python path for scaffolded projects
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())

    # Try to import from run.py
    if os.path.exists("run.py"):
        spec = importlib.util.spec_from_file_location("run", "run.py")
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "app"):
                return module.app

    print("Error: Could not find app instance. Make sure you're in a Future project directory.")
    print("Expected to find app in: run.py")
    sys.exit(1)


def print_routes() -> None:
    from rich.box import SIMPLE_HEAD
    from rich.console import Console
    from rich.table import Table
    from rich.text import Text

    console = Console()
    app = get_app_from_project()
    routes = getattr(app, "routes", {})
    if not routes:
        console.print("[yellow]No routes registered.[/yellow]")
        return

    # (domain, group_name, prefix, subdomain, middleware_label) -> rows
    sections: dict[tuple[str, str, str, str, str], list[tuple[str, str, str, str]]] = {}
    for domain, domain_routes in routes.items():
        domain_label = domain or "(any host)"
        for route_key, route_info in domain_routes.items():
            route = route_info.get("route")
            path = getattr(route, "path", None) or (route_key.split(" ", 1)[-1] if " " in str(route_key) else route_key)
            methods = route_info.get("methods") or (["WEBSOCKET"] if "ws" in path else ["GET"])
            name = getattr(route, "name", "") or ""
            group = route_info.get("group") or {}
            group_name = group.get("name") or "(ungrouped)"
            prefix = group.get("prefix") or ""
            group_sub = group.get("subdomain") or ""
            middleware_classes = route_info.get("middleware", {}).get("classes", [])
            middleware_names = []
            for middleware in middleware_classes:
                if hasattr(middleware, "name") and middleware.name:
                    middleware_names.append(middleware.name)
                else:
                    middleware_names.append(middleware.__name__)
            middleware_label = ", ".join(middleware_names) if middleware_names else "(none)"
            param_names = getattr(route, "param_names", None) or []
            args = ", ".join(param_names) if param_names else "-"
            section_key = (domain_label, group_name, prefix, group_sub, middleware_label)
            sections.setdefault(section_key, []).append((",".join(methods), path, name, args))

    console.print()
    console.print(Text("Routes", style="bold"))
    total = 0
    for (domain_label, group_name, prefix, group_sub, middleware_label), rows in sorted(sections.items(), key=lambda item: (item[0][0], item[0][1], item[0][2])):
        rows.sort(key=lambda row: (row[1], row[0]))
        total += len(rows)
        meta_parts = [f"domain={domain_label}"]
        if prefix:
            meta_parts.append(f"prefix={prefix}")
        if group_sub:
            meta_parts.append(f"subdomain={group_sub}")
        meta_parts.append(f"middleware={middleware_label}")
        console.print()
        console.print(Text(f"{group_name}", style="bold cyan"), Text(f"  {' · '.join(meta_parts)}", style="dim"))
        table = Table(box=SIMPLE_HEAD, show_header=True, pad_edge=False, expand=False)
        table.add_column("Method", style="magenta", no_wrap=True)
        table.add_column("Path", style="green")
        table.add_column("Name", style="white")
        table.add_column("Args", style="yellow")
        for method, path, name, args in rows:
            table.add_row(method, path, name, args)
        console.print(table)

    console.print()
    console.print(Text(f"{total} route(s) in {len(sections)} group(s)", style="dim"))
    console.print()


def scaffold_project(target_dir: str) -> None:
    target = Path(target_dir)
    if target.exists() and any(target.iterdir()):
        print(f"Directory {target} already exists and is not empty.")
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
    (app_dir / "routes.py").write_text(APP_ROUTES)
    (app_dir / "config" / "Settings.py").write_text(CONFIG_SETTINGS)
    (app_dir / "config" / "Database.py").write_text(CONFIG_DATABASE)
    (target / "database" / "migrations").mkdir(parents=True, exist_ok=True)
    (target / "database" / "seeds").mkdir(parents=True, exist_ok=True)
    (app_dir / "controllers" / "ExampleController.py").write_text(EXAMPLE_CONTROLLER)
    (app_dir / "middleware" / "ExampleMiddleware.py").write_text(EXAMPLE_MIDDLEWARE)
    (app_dir / "models" / "ExampleModel.py").write_text(EXAMPLE_MODEL)
    (app_dir / "plugins" / "ExamplePlugin.py").write_text(EXAMPLE_PLUGIN)
    (app_dir / "tasks" / "ExampleTask.py").write_text(EXAMPLE_TASK)

    print(f"Scaffolded new Future project at {target.resolve()}")


def ensure_project_path() -> None:
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())


def register_database_connections() -> None:
    get_app_from_project()


def run_migrations(rollback: bool = False) -> None:
    from future.migrations.Migrator import Migrator
    from rich.console import Console
    from rich.text import Text

    register_database_connections()
    migrator = Migrator(path="database/migrations")
    console = Console()
    if rollback:
        rolled = migrator.rollback()
        if not rolled:
            console.print(Text("✓ Nothing to rollback.", style="green"))
            return
        for name in rolled:
            line = Text()
            line.append("✓ ", style="green")
            line.append("Rolled back ", style="green")
            line.append(name, style="blue")
            console.print(line)
        return
    ran = migrator.run()
    if not ran:
        console.print(Text("✓ Nothing to migrate.", style="green"))
        return
    for name in ran:
        line = Text()
        line.append("✓ ", style="green")
        line.append("Migrated ", style="green")
        line.append(name, style="blue")
        console.print(line)


def run_seeds(seeder: str | None = None) -> None:
    from future.seeds.SeedRunner import SeedRunner

    register_database_connections()
    ran = SeedRunner(path="database/seeds").run(name=seeder)
    print(f"Seeded: {ran}")


def make_migration(model_name: str | None = None) -> None:
    from future.migrations.MigrationGenerator import MigrationGenerator
    from rich.console import Console
    from rich.text import Text

    ensure_project_path()
    console = Console()
    try:
        paths = MigrationGenerator().make(model_name)
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        sys.exit(1)
    if not paths:
        print("No migrations created (no annotated models found).")
        return
    for path in paths:
        line = Text()
        line.append("✓ ", style="green")
        line.append("Migration created successfully! ", style="green")
        line.append(str(path), style="blue")
        console.print(line)


def make_seed(model_name: str | None = None) -> None:
    from future.seeds.SeedGenerator import SeedGenerator

    ensure_project_path()
    try:
        paths = SeedGenerator().make(model_name)
    except (FileNotFoundError, FileExistsError, ValueError) as error:
        print(f"Error: {error}")
        sys.exit(1)
    if not paths:
        print("No new seeders created (all models already have seeders, or no annotated models found).")
        return
    for path in paths:
        print(f"Created: {path}")


def make_stub(kind: str, name: str) -> None:
    from .stubs import StubMaker

    ensure_project_path()
    try:
        path = StubMaker().make(kind, name)
    except (FileNotFoundError, FileExistsError, ValueError) as error:
        print(f"Error: {error}")
        sys.exit(1)
    print(f"Created: {path}")


def run_app(host: str | None = None, port: int | None = None, workers: int | None = None) -> None:
    app = get_app_from_project()
    config = getattr(app, "config", {}) or {}
    bind_host = host if host is not None else config.get("APP_HOST", "127.0.0.1")
    bind_port = port if port is not None else int(config.get("APP_PORT", 8000))
    bind_workers = workers if workers is not None else int(config.get("APP_WORKERS", 1))
    app.run(host=bind_host, port=bind_port, workers=bind_workers)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Future Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  future init .
  future run
  future routes
  future make:model Trade
  future make:controller Trade
  future make:migration Trade
  future make:migrations
  future make:seed Trade
  future make:seeds
  future migrate
  future migrate rollback
  future seed
  future seed TradeSeeder
""",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("routes", help="List all routes from the app in run.py")

    init_parser = subparsers.add_parser("init", help="Scaffold a new Future project (app/, database/, run.py)")
    init_parser.add_argument("target", nargs="?", default=".", help="Target directory (default: current directory)")

    run_parser = subparsers.add_parser("run", help="Run the app from run.py")
    run_parser.add_argument("--host", default=None, help="Bind host (default: app config or 127.0.0.1)")
    run_parser.add_argument("--port", type=int, default=None, help="Bind port (default: app config or 8000)")
    run_parser.add_argument("--workers", type=int, default=None, help="Worker processes (default: app config or 1)")

    migrate_parser = subparsers.add_parser("migrate", help="Run or rollback migrations in database/migrations/")
    migrate_parser.add_argument("action", nargs="?", default="run", choices=["run", "rollback"], help="run (default) or rollback last batch")

    seed_parser = subparsers.add_parser("seed", help="Run seeders in database/seeds/ (loads run.py so Future registers DATABASES)")
    seed_parser.add_argument("seeder", nargs="?", default=None, help="Seeder class name, or omit to run all seeders")

    make_migration_parser = subparsers.add_parser("make:migration", help="Generate a Schema migration from one Model")
    make_migration_parser.add_argument("model", help="Model class name")

    subparsers.add_parser("make:migrations", help="Generate Schema migrations for all annotated models")

    make_seed_parser = subparsers.add_parser("make:seed", help="Generate a seeder from one Model")
    make_seed_parser.add_argument("model", help="Model class name")

    subparsers.add_parser("make:seeds", help="Generate seeders for all annotated models (skips existing files)")

    stub_help = {
        "model": "Create app/models/<Name>.py",
        "controller": "Create app/controllers/<Name>Controller.py",
        "middleware": "Create app/middleware/<Name>Middleware.py",
        "plugin": "Create app/plugins/<Name>Plugin.py",
        "task": "Create app/tasks/<Name>.py",
    }
    for kind, help_text in stub_help.items():
        stub_parser = subparsers.add_parser(f"make:{kind}", help=help_text)
        stub_parser.add_argument("name", help=f"{kind.capitalize()} name")

    args = parser.parse_args()

    if args.command == "routes":
        print_routes()
    elif args.command == "init":
        if args.target == ".":
            scaffold_project(os.getcwd())
        else:
            scaffold_project(os.path.join(os.getcwd(), args.target))
    elif args.command == "run":
        run_app(host=args.host, port=args.port, workers=args.workers)
    elif args.command == "migrate":
        run_migrations(rollback=(args.action == "rollback"))
    elif args.command == "seed":
        run_seeds(seeder=args.seeder)
    elif args.command == "make:migration":
        make_migration(model_name=args.model)
    elif args.command == "make:migrations":
        make_migration(model_name=None)
    elif args.command == "make:seed":
        make_seed(model_name=args.model)
    elif args.command == "make:seeds":
        make_seed(model_name=None)
    elif args.command and args.command.startswith("make:"):
        kind = args.command.split(":", 1)[1]
        if kind in stub_help:
            make_stub(kind=kind, name=args.name)
        else:
            parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
