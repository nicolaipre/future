# Generate Schema migrations from Model annotations.


import importlib.util
import inflection
from datetime import datetime
from pathlib import Path
from types import UnionType
from typing import get_args, get_origin, Union

from future.models import Model


class MigrationGenerator:
    def __init__(self, models_path="app/models", migrations_path="database/migrations"):
        self.models_path = models_path
        self.migrations_path = migrations_path

    def find_model(self, name):
        for model in self.discover_models():
            if model.__name__ == name:
                return model
        raise ValueError(f"Model not found: {name}")

    def discover_models(self):
        directory = Path(self.models_path)
        if not directory.exists():
            raise FileNotFoundError(f"Models path not found: {self.models_path}")
        models = []
        seen = set()
        for file_path in sorted(directory.glob("*.py")):
            if file_path.name.startswith("_"):
                continue
            module_name = f"app_model_{file_path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, str(file_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for value in module.__dict__.values():
                if not isinstance(value, type) or not issubclass(value, Model) or value is Model:
                    continue
                if value.__name__ in seen:
                    continue
                if not getattr(value, "__annotations__", None):
                    continue
                seen.add(value.__name__)
                models.append(value)
        return models

    def table_name(self, model):
        return model.__table__ or inflection.tableize(model.__name__)

    def column_line(self, field, annotation):
        nullable = False
        origin = get_origin(annotation)
        if origin is Union or origin is UnionType:
            args = get_args(annotation)
            nullable = type(None) in args
            non_null = [arg for arg in args if arg is not type(None)]
            annotation = non_null[0] if non_null else str
        if field == "id":
            return "table.id()"
        type_name = getattr(annotation, "__name__", str(annotation))
        if annotation is datetime or type_name == "datetime":
            line = f'table.datetime("{field}")'
        elif annotation is int or type_name == "int":
            line = f'table.integer("{field}")'
        elif annotation is float or type_name == "float":
            line = f'table.float("{field}")'
        elif annotation is bool or type_name == "bool":
            line = f'table.boolean("{field}")'
        elif field in ("description", "text", "body", "content") or field.endswith("_original") or field.endswith("_translated"):
            line = f'table.text("{field}")'
        else:
            line = f'table.string("{field}")'
        if nullable:
            line += ".nullable()"
        return line

    def blueprint_lines(self, model):
        annotations = dict(getattr(model, "__annotations__", {}))
        lines = []
        if "created_at" in annotations and "updated_at" in annotations:
            annotations.pop("created_at")
            annotations.pop("updated_at")
            use_timestamps = True
        else:
            use_timestamps = False
        for field, annotation in annotations.items():
            lines.append(f"            {self.column_line(field, annotation)}")
        if use_timestamps:
            lines.append("            table.timestamps()")
        return lines

    def render(self, model):
        table = self.table_name(model)
        class_name = f"Create{inflection.camelize(table)}"
        connection = getattr(model, "__connection__", "default")
        columns = "\n".join(self.blueprint_lines(model))
        return (
            "from future.migrations.Migration import Migration\n"
            "from future.migrations.Schema import Schema\n"
            "\n"
            "\n"
            f"class {class_name}(Migration):\n"
            f'    __connection__ = "{connection}"\n'
            "\n"
            "    def up(self):\n"
            f'        with Schema.create("{table}") as table:\n'
            f"{columns}\n"
            "\n"
            "    def down(self):\n"
            f'        Schema.drop("{table}")\n'
        )

    def make(self, model_name=None):
        if model_name is None:
            return self.make_all()
        model = self.find_model(model_name)
        return [self.write(model)]

    def make_all(self):
        paths = []
        for index, model in enumerate(self.discover_models()):
            paths.append(self.write(model, stamp_offset=index))
        return paths

    def write(self, model, stamp_offset=0):
        table = self.table_name(model)
        stamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        if stamp_offset:
            stamp = f"{stamp}_{stamp_offset:02d}"
        file_name = f"{stamp}_create_{table}.py"
        directory = Path(self.migrations_path)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / file_name
        path.write_text(self.render(model))
        return str(path)
