# File stubs for make:model / make:controller / make:middleware / make:plugin / make:task / make:seed.


from pathlib import Path


STUB_KINDS = {
    "model": {
        "directory": "app/models",
        "suffix": "",
        "template": '''from future.models import Model
from datetime import datetime


class {class_name}(Model):
    __connection__ = "default"
    # __table__ = "..."  # optional; otherwise tableized class name

    id: str
    name: str
    created_at: datetime
    updated_at: datetime
''',
    },
    "controller": {
        "directory": "app/controllers",
        "suffix": "Controller",
        "template": '''from future.controllers import Controller
from future.response import Response


class {class_name}(Controller):
    async def index(self) -> Response:
        return self.response.json({{"message": "{class_name}"}}, status=200)

    async def show(self, id: str) -> Response:
        return self.response.json({{"id": id}}, status=200)
''',
    },
    "middleware": {
        "directory": "app/middleware",
        "suffix": "Middleware",
        "template": '''from future.middleware import Middleware
from future.response import Response
from typing import Optional


class {class_name}(Middleware):
    name = "{class_name}"
    priority = 0

    async def before(self) -> Optional[Response]:
        return None

    async def after(self) -> Optional[Response]:
        return None
''',
    },
    "plugin": {
        "directory": "app/plugins",
        "suffix": "Plugin",
        "template": '''from future.plugins import Plugin


class {class_name}(Plugin):
    pass
''',
    },
    "task": {
        "directory": "app/tasks",
        "suffix": "",
        "template": '''"""
{class_name} task — pass to Lifespan cron_tasks via Task(..., func=run).
"""


def run():
    pass
''',
    },
    "seed": {
        "directory": "database/seeds",
        "suffix": "Seeder",
        "template": '''from future.seeds.Seeder import Seeder


class {class_name}(Seeder):
    def run(self):
        pass
''',
    },
}


class StubMaker:
    def class_name(self, name, suffix):
        if suffix and not name.endswith(suffix):
            return f"{name}{suffix}"
        return name

    def make(self, kind, name):
        if kind not in STUB_KINDS:
            raise ValueError(f"Unknown stub kind: {kind}")
        config = STUB_KINDS[kind]
        class_name = self.class_name(name, config["suffix"])
        directory = Path(config["directory"])
        if not Path("app").is_dir() and not Path("database").is_dir():
            raise FileNotFoundError("No app/ or database/ directory found. Run future init first.")
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{class_name}.py"
        if path.exists():
            raise FileExistsError(f"File already exists: {path}")
        path.write_text(config["template"].format(class_name=class_name))
        return str(path)
