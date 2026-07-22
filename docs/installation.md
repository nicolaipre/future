# Installation
## Requirements
- Python **3.12+**
- [Poetry](https://python-poetry.org/) (recommended) or pip

## Install from this repo (typical while developing Future)
In an app `pyproject.toml`:

```toml
[tool.poetry.dependencies]
future = { path = "../future", develop = true }
```

Then:

```bash
poetry install
poetry run future --help
```

## Install published package
```bash
poetry add future-api
# or
pip install future-api
```

Or, while developing Future next to an app, use a path dependency (recommended):

```toml
# in your app pyproject.toml
future = { path = "../future", develop = true }
```

```bash
poetry install
poetry run future --help
```

Package import name is always `future` (`from future.application import Future`).

## From source
```bash
git clone https://github.com/nicolaipre/future.git
cd future
poetry install
poetry run future --help
```

## Scaffold an app
```bash
poetry run future init myproject
cd myproject
# edit run.py, app/routes.py, app/config/*
poetry run python run.py
```

## Verify
```bash
python -c "from future.application import Future; print('ok')"
poetry run future --help
```

## Next
1. [Quick start](quick-start.md)
2. [Getting started](getting-started.md)
3. [HTTP guide](http.md)
4. [CLI](cli.md)
