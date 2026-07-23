# Database
Connection registry and drivers. Models, migrations, and seeds: see [Models](models.md).

## Register connections
Define the map in `app/config/Database.py` (data only — no `Connections` call at import). Pass it into `Future` in `run.py`:

```python
from future.databases.SQLite import SQLite
from app.config.Settings import DB_DATABASE

DATABASES = {
    "default": "sqlite",
    "sqlite": SQLite(database=DB_DATABASE),
}
```

```python
config = {
    "APP_DOMAIN": APP_DOMAIN,
    "APP_NAME": APP_NAME,
    "DATABASES": DATABASES,
}
app = Future(lifespan=lifespan, config=config)
```

CLI `migrate` / `seed` load `run.py` so registration matches runtime. Env loading (`.env` or Ansible YAML): [Configuration](configuration.md).


## Per-model connection
Models are not locked to one database. Set `__connection__` on the model to a key from `DATABASES` (or `"default"` for `DATABASES["default"]`). Migrations inherit that name; see [Models](models.md#connections).


## Run migrations and seeds
Generate files **from model annotations** first (`future make:migration` / `make:seed`) — details in [Models](models.md). Then:

```bash
future migrate
future migrate rollback
future seed
future seed StockSeeder
```

## Drivers
| Driver | Schema / migrate | CRUD |
|--------|------------------|------|
| SQLite | Yes | Yes |
| MySQL | Yes | Yes |
| Postgres | Yes | Yes |
| Elasticsearch | Yes | Yes |
| MongoDB | Yes | Yes |
| ClickHouse | Yes | Yes |
| Redis | N/A | Yes |

Scaffold default is **SQLite**. Set `DB_DATABASE` / `sqlite_database` to a bare name; the driver appends `.sqlite`.

For local MySQL, Postgres, Redis, MongoDB, Elasticsearch, ClickHouse, and RabbitMQ, see the [Docker example](docker.md).
