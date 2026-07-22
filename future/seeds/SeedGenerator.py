# Generate seeder stubs from Model annotations.


from pathlib import Path
from types import UnionType
from typing import get_args, get_origin, Union

from future.migrations.MigrationGenerator import MigrationGenerator


class SeedGenerator:
    def __init__(self, models_path="app/models", seeds_path="database/seeds"):
        self.models_path = models_path
        self.seeds_path = seeds_path

    def find_model(self, name):
        for model in MigrationGenerator(models_path=self.models_path).discover_models():
            if model.__name__ == name:
                return model
        raise ValueError(f"Model not found: {name}")

    def value_expr(self, field, annotation):
        origin = get_origin(annotation)
        if origin is Union or origin is UnionType:
            args = [arg for arg in get_args(annotation) if arg is not type(None)]
            annotation = args[0] if args else str
        type_name = getattr(annotation, "__name__", str(annotation))
        if field == "id":
            return "fake.uuid4()"
        if type_name == "datetime":
            return "fake.date_time_this_year()"
        if type_name == "int":
            return "fake.random_int(1, 9999)"
        if type_name == "float":
            return "float(fake.pyfloat(min_value=1, max_value=100))"
        if type_name == "bool":
            return "fake.boolean()"
        if field.endswith("_id"):
            return "str(fake.random_int(1000, 9999))"
        if "email" in field:
            return "fake.email()"
        if "name" in field or "username" in field:
            return "fake.user_name()"
        if field in ("description", "text", "body", "content") or field.endswith("_original") or field.endswith("_translated"):
            return "fake.paragraph()"
        return "fake.word()"

    def render(self, model):
        name = model.__name__
        annotations = dict(getattr(model, "__annotations__", {}))
        args = []
        for field, annotation in annotations.items():
            args.append(f"                {field}={self.value_expr(field, annotation)},")
        if args:
            construct = f"            {name}(\n" + "\n".join(args) + f"\n            ).save()"
        else:
            construct = f"            {name}().save()"
        return (
            "from faker import Faker\n"
            "from future.seeds.Seeder import Seeder\n"
            f"from app.models.{name} import {name}\n"
            "\n"
            "\n"
            f"class {name}Seeder(Seeder):\n"
            "    def run(self):\n"
            "        fake = Faker()\n"
            "        for _ in range(10):\n"
            f"{construct}\n"
        )

    def make(self, model_name=None):
        if model_name is None:
            return self.make_all()
        model = self.find_model(model_name)
        return [self.write(model)]

    def make_all(self):
        paths = []
        for model in MigrationGenerator(models_path=self.models_path).discover_models():
            path = self.write(model, skip_existing=True)
            if path is not None:
                paths.append(path)
        return paths

    def write(self, model, skip_existing=False):
        class_name = f"{model.__name__}Seeder"
        directory = Path(self.seeds_path)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{class_name}.py"
        if path.exists():
            if skip_existing:
                return None
            raise FileExistsError(f"File already exists: {path}")
        path.write_text(self.render(model))
        return str(path)
