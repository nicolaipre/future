# Database and models
Future uses an **Active Record**-style `Model` plus a `Connections` registry. Drivers implement a shared interface; completeness varies.

## Register connections
Define the map in `app/config/Database.py` (data only — no `Connections` call at import):

```python
# app/config/Database.py
from future.databases.SQLite import SQLite
# from future.databases.MySQL import MySQL

DATABASES = {
    "default": "sqlite",
    "sqlite": SQLite(database="database"),
    # "mysql": MySQL(host=..., port=3306, username=..., password=..., database="app"),
}
```

Pass it into `Future` so the app registers `Connections` at boot:

```python
from app.config.Database import DATABASES

config = {
    "APP_DOMAIN": APP_DOMAIN,
    "APP_NAME": APP_NAME,
    "DATABASES": DATABASES,
}
app = Future(lifespan=lifespan, config=config)
# app.databases is the same map; Connections is registered inside Future.__init__
```

CLI `migrate` / `seed` load `run.py` (constructing `Future`) so registration happens the same way.

## Define a model
```python
from future.models import Model
from datetime import datetime

class Trade(Model):
    __connection__ = "default"  # name from Connections / DATABASES
    # __table__ = "trades"      # optional; otherwise tableized class name (Trade → trades)
```

Column annotations (used by `future make:migration`) follow your project’s model style.

## Create / update / save
```python
trade = Trade(
    id="3",
    timestamp=datetime.now(),
    user_name="John Doe",
    user_id="1234567890",
    instrument_name="Apple",
    instrument_id="1234567890",
    price=100.0,
    percentage_change=10.0,
    trade_type="buy",
    currency="USD",
)
trade.save()
print(trade.to_dict())

trade.price = 101.0
trade.save()
```

## Find / all
```python
trade = Trade.find("1")
print(trade)           # Model.__repr__ → dict-like string
print(trade.to_json())

trades = Trade.all()
for trade in trades:
    print(trade)
```

## Query builder
`where()` / `order_by()` return a **Query** — they do not hit the DB until you call `.get()` or `.first()`:

```python
Trade.where("user_id", "1234567890").get()              # list of Trade
Trade.where("user_id", ">", 123456789).get()
Trade.where("user_id", ">", 123456789).first()          # one Trade or None
Trade.order_by("timestamp", "desc").first()
Trade.where("price", ">", 50).order_by("price", "desc").get()
```

Printing a bare Query shows: `<Query; call .get() or .first() to execute>`.

## Driver status
| Driver | Connect | Schema / migrate | CRUD |
|--------|---------|------------------|------|
| SQLite | Yes | Yes | Yes |
| MySQL | Yes | Yes | Yes |
| Postgres | Yes | Yes | Yes |
| Elasticsearch | Yes | Yes | Yes |
| MongoDB | Yes | Yes | Yes |
| ClickHouse | Yes | Yes | Yes |
| Redis | Yes | N/A | Yes |

Scaffolded apps default to **SQLite**. Set `DB_DATABASE` to a bare name (e.g. `database`); the driver opens `database.sqlite`. Use `:memory:` for in-memory tests. MySQL uses the same setting as the schema name and auto-creates it on first connect if missing.

Use `with Model.transaction():` (or `connection.transaction()`) for a SQLAlchemy transaction block. Relations: `model.belongs_to(Related)`, `model.has_many(Related)`, and `Model.eager_load(rows, name, Related, kind="belongs_to"|"has_many")`.

## Migrations
Schema uses a portable blueprint (`Schema.create` / `drop`); each driver maps that to tables, indices, or collections.

```bash
poetry run future make:migration Trade   # from model annotations
poetry run future make:migrations        # all annotated models
poetry run future migrate
poetry run future migrate rollback
```

Migrations live under `database/migrations/`. Set `__connection__` to `"default"` (follows `DATABASES["default"]`) or a concrete name (`"mysql"`, `"elasticsearch"`). The same blueprint runs on whichever driver that connection uses.

## Seeds
```bash
poetry run future make:seed Trade      # → database/seeds/TradeSeeder.py
poetry run future make:seeds          # all annotated models (skips files that already exist)
poetry run future seed                 # run every seeder in database/seeds/
poetry run future seed TradeSeeder     # run one seeder
```

Seeds live under `database/seeds/`. Register connections via `Future(config={"DATABASES": ...})` (or `Connections().set_connection_details`) so CLI migrate/seed see them when they load `run.py`.
