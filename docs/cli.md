# CLI
Entry point: `poetry run future` (or the installed `future` console script).

```bash
poetry run future --help
```

## Project
```bash
# Scaffold a new project (app/, database/, run.py, …)
future init .
future init myproject

# Run the app from run.py (loads Future → registers DATABASES)
future run
future run --host 0.0.0.0 --port 8000 --workers 1
```

`Future.run` uses the app instance when `workers=1` and `APP_DEBUG` is false. For reload (`APP_DEBUG`) or `workers>1`, set `config["APP_ASGI"]` (default `run:app`) so uvicorn can import the app.

```bash
# List registered routes (expects app in run.py)
future routes
```

## Generators
Creates files under `app/` or `database/` when that project tree exists:

```bash
future make:model Order
future make:controller Order          # → OrderController
future make:middleware Auth           # → AuthMiddleware
future make:plugin Cache              # → CachePlugin
future make:task Cleanup

# Migration from model annotations
future make:migration Trade
future make:migrations

# Seeder from model annotations
future make:seed Trade                # → TradeSeeder
future make:seeds                     # all annotated models (skips existing files)
```

## Database
Define `DATABASES` in `app/config/Database.py` and pass it into `Future` via `run.py` config. CLI `migrate` / `seed` load `run.py` so registration happens on the app object. See [Database and models](database.md).

```bash
# Run pending migrations (database/migrations/)
future migrate
future migrate rollback

# Run seeders (database/seeds/; omit name to run all)
future seed
future seed TradeSeeder
```

## Not implemented
- Plugin installers (`future install …`) — not implemented
