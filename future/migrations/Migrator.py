# Discovers and runs migration files against Connections.


import importlib.util
from pathlib import Path

from future.databases.Connections import Connections
from .Migration import Migration
from .Schema import Schema


class Migrator:
    def __init__(self, path):
        self.path = path

    def discover(self):
        migrations = []
        directory = Path(self.path)
        if not directory.exists():
            return migrations
        for file_path in sorted(directory.glob("*.py")):
            if file_path.name.startswith("_"):
                continue
            module_name = f"migration_{file_path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, str(file_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for value in module.__dict__.values():
                if isinstance(value, type) and issubclass(value, Migration) and value is not Migration:
                    migrations.append((file_path.stem, value))
                    break
        return migrations

    def run(self):
        applied_by_connection = {}
        batch_by_connection = {}
        ran = []
        for name, migration_class in self.discover():
            migration = migration_class()
            connection_name = getattr(migration, "__connection__", "default")
            connection = Connections().get_connection(connection_name)
            if connection_name not in applied_by_connection:
                applied_by_connection[connection_name] = set(connection.migrations_get())
                batch_by_connection[connection_name] = connection.migrations_max_batch() + 1
            if name in applied_by_connection[connection_name]:
                continue
            Schema.connection(connection_name)
            migration.up()
            connection.migrations_put(name, batch_by_connection[connection_name])
            ran.append(name)
        return ran

    def rollback(self):
        rolled = []
        by_connection = {}
        for name, migration_class in self.discover():
            migration = migration_class()
            connection_name = getattr(migration, "__connection__", "default")
            by_connection.setdefault(connection_name, []).append((name, migration))
        for connection_name, items in by_connection.items():
            connection = Connections().get_connection(connection_name)
            max_batch = connection.migrations_max_batch()
            if max_batch == 0:
                continue
            for name, migration in reversed(items):
                if connection.migrations_batch_for(name) != max_batch:
                    continue
                Schema.connection(connection_name)
                migration.down()
                connection.migrations_delete(name)
                rolled.append(name)
        return rolled
