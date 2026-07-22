# Discovers and runs seeder classes from a seeds directory.


import importlib.util
from pathlib import Path

from .Seeder import Seeder


class SeedRunner:
    def __init__(self, path):
        self.path = path

    def discover(self):
        seeders = {}
        directory = Path(self.path)
        if not directory.exists():
            return seeders
        for file_path in sorted(directory.glob("*.py")):
            if file_path.name.startswith("_"):
                continue
            module_name = f"seeder_{file_path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, str(file_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for value in module.__dict__.values():
                if isinstance(value, type) and issubclass(value, Seeder) and value is not Seeder:
                    seeders[value.__name__] = value
        return seeders

    def run(self, name=None):
        seeders = self.discover()
        if name is not None:
            if name not in seeders:
                raise ValueError(f"Seeder not found: {name}")
            seeders[name]().run()
            return [name]
        ran = []
        for seeder_name in sorted(seeders.keys()):
            seeders[seeder_name]().run()
            ran.append(seeder_name)
        return ran
