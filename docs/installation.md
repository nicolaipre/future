# Installation
## Requirements
- Python **3.12+**
- [Poetry](https://python-poetry.org/) (recommended) or pip

## Package
PyPI name is **`future-framework`**; import name is always **`future`**.

```bash
poetry add future-framework
# or
pip install future-framework
```

```toml
# pyproject.toml
future-framework = "^1.1.0"
```

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
