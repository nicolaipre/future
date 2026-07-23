# Installation
## Requirements
- Python **3.12+**
- [Poetry](https://python-poetry.org/) (recommended) or pip

## Package
```bash
poetry add git+https://github.com/nicolaipre/future.git@master
```

Or in `pyproject.toml`:

```toml
future = { git = "https://github.com/nicolaipre/future.git", rev = "master" }
```

Import name is always `future`:

```python
from future.application import Future
```

## Scaffold an app
```bash
poetry run future init myproject
cd myproject
cp .env.example .env
poetry install
poetry run future migrate
poetry run future seed
poetry run python run.py
```

See [Getting started](getting-started.md) and [Configuration](configuration.md).
