# Quick start
End-to-end path from an empty folder to a migrated, seeded app using the Future CLI. Scaffolded apps use **SQLite** by default (no database server). Commands below match the monorepo layout (`backend` Poetry env provides `future`; app lives in its own directory).

## Prerequisites
- Python 3.12+
- Future installed (path dependency or git) so the `future` console script is on your `PATH`

When Future lives next to your app (as in this repo), use the backend venv:

```bash
cd /path/to/backend
poetry install
export PATH="$(poetry env info -p)/bin:$PATH"
which future
```

## Scaffold
```bash
mkdir myproject
future init /path/to/myproject
find /path/to/myproject | sort
cd /path/to/myproject
cp .env.example .env
```

`.env` defaults to a local SQLite database name (the driver writes `<name>.sqlite`):

```bash
DB_DATABASE=database
APP_DEBUG=True
```

To use MySQL instead, switch `app/config/Database.py` to `MySQL` and set `DB_HOST` / `DB_PORT` / `DB_USERNAME` / `DB_PASSWORD` / `DB_DATABASE`. MySQL creates the configured database on first connect if it is missing.

## Generators
From the project directory:

```bash
future routes
future make:migration ExampleModel
future make:seed ExampleModel
future make:model Order
future make:migrations
future make:controller Foo
future make:middleware Bar
future make:plugin Baz
future make:task Cleanup
```

Inspect what was created:

```bash
cat app/models/Order.py
ls -la database/migrations/
ls -la database/seeds/
```

Prefer either `make:migration ExampleModel` **or** `make:migrations`, not both for the same model in one session — otherwise you can get duplicate migration files.

## Migrate and seed
```bash
future migrate
future seed
future seed ExampleModelSeeder
future migrate rollback
future migrate
future seed
```

## Run the app
```bash
future run
# or
python run.py
future routes
```

`Future.run` uses the app instance when `workers=1` and `APP_DEBUG` is false. For reload (`APP_DEBUG`) or `workers>1`, set `config["APP_ASGI"]` (default `run:app`) so uvicorn can import the app.

## Verify rows (optional)
```bash
python3 - <<'PY'
import sqlite3
conn = sqlite3.connect("database.sqlite")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("tables:", cur.fetchall())
cur.execute("SELECT COUNT(*) FROM example_models")
print("example_models count:", cur.fetchone()[0])
conn.close()
PY
```

## Next
- [CLI](cli.md)
- [Database and models](database.md)
- [Quick reference](quick-reference.md)
