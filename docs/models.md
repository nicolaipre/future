# Models
Active Record models live in `app/models/` and inherit `future.models.Model`. **Class annotations are the source of truth** for columns — migrations and seeders are generated from them.

## Define a model
```bash
future make:model Stock
```

```python
from future.models import Model

class Stock(Model):
    # __table__ = "stocks"        # optional; default is tableized class name (Stock → stocks)
    # __connection__ = "default"  # name from DATABASES / Connections

    id: str
    name: str
    symbol: str
    instrument_id: str
    price: float | None
```

Register connections in [Configuration](configuration.md) / [Database](database.md) before using the model at runtime or in CLI.

## Annotations drive generators
After annotations are set:

```bash
future make:migration Stock   # → database/migrations/…_create_stocks.py from annotations
future make:seed Stock        # → database/seeds/StockSeeder.py from annotations

# or every annotated model under app/models/:
future make:migrations
future make:seeds             # skips seed files that already exist
```

Then apply / run:

```bash
future migrate
future seed                   # all seeders
future seed StockSeeder       # one class name
```

Prefer either `make:migration Stock` **or** `make:migrations` for the same model in one session — not both (duplicate files).

Generated migration (from the `Stock` annotations above):

```python
from future.migrations.Migration import Migration
from future.migrations.Schema import Schema

class CreateStocks(Migration):
    __connection__ = "default"

    def up(self):
        with Schema.create("stocks") as table:
            table.id()
            table.string("name")
            table.string("symbol")
            table.string("instrument_id")
            table.float("price").nullable()

    def down(self):
        Schema.drop("stocks")
```

Generated seeder uses the model fields (Faker stubs):

```python
from faker import Faker
from future.seeds.Seeder import Seeder
from app.models.Stock import Stock

class StockSeeder(Seeder):
    def run(self):
        fake = Faker()
        for _ in range(10):
            Stock(
                id=fake.uuid4(),
                name=fake.company(),
                symbol=fake.unique.lexify(text="????").upper(),
                instrument_id=str(fake.random_int(10000, 99999)),
                price=float(fake.pyfloat(min_value=1, max_value=100)),
            ).save()
```

Edit generated files if you need indexes, extras, or richer seed data. Re-running generators does not replace hand-edited migrations; seeds skip existing files on `make:seeds`.

## CRUD
```python
stock = Stock(id="1", name="Equinor", symbol="EQNR", instrument_id="16105067", price=250.0)
stock.save()

stock = Stock.find("1")
stocks = Stock.all()
stock.price = 251.0
stock.save()
stock.delete()
```

## Query
`where` / `order_by` return a **Query** — call `.get()` or `.first()` to hit the DB:

```python
Stock.where("symbol", "EQNR").first()
Stock.where("price", ">", 100).order_by("price", "desc").get()
Stock.where("name", "like", "%Equinor%").limit(20).get()
```

In a controller:

```python
async def get_stocks(self) -> Response:
    ticker = self.request.query.get("ticker")
    if ticker:
        stocks = Stock.where("symbol", ticker).get()
    else:
        stocks = Stock.all()
    return self.response.json([s.to_dict() for s in stocks], status=200)
```

See [CLI](cli.md) for the full command list and [Database](database.md) for drivers and connection registration.
