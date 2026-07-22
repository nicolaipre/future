from datetime import datetime

from future.databases.Connections import Connections
from future.databases.SQLite import SQLite
from future.migrations.Blueprint import Blueprint
from future.models import Model


class Item(Model):
    __connection__ = "sqlite"
    __table__ = "items"

    id: str
    name: str
    price: float
    active: bool


def _register(database=":memory:"):
    Connections().set_connection_details({
        "default": "sqlite",
        "sqlite": SQLite(database=database),
    })
    return Connections().get_connection("sqlite")


def _create_items_table(connection):
    blueprint = Blueprint("items", "sqlite", action="create")
    blueprint.id()
    blueprint.string("name")
    blueprint.float("price")
    blueprint.boolean("active")
    blueprint.timestamps()
    connection.schema_create(blueprint)


def test_sqlite_connect_memory():
    connection = _register(":memory:")
    assert connection.connect() is not None
    connection.disconnect()


def test_sqlite_connect_creates_file(tmp_path):
    name = str(tmp_path / "app")
    connection = _register(name)
    connection.connect()
    assert (tmp_path / "app.sqlite").exists()
    connection.disconnect()


def test_sqlite_schema_and_crud():
    connection = _register(":memory:")
    _create_items_table(connection)

    item = Item(id="1", name="apple", price=1.5, active=True, created_at=datetime(2026, 1, 1), updated_at=datetime(2026, 1, 1))
    item.save()

    found = Item.find("1")
    assert found is not None
    assert found.name == "apple"
    assert float(found.price) == 1.5
    assert int(found.active) == 1

    item.update(name="pear", price=2.0)
    found = Item.find("1")
    assert found.name == "pear"
    assert float(found.price) == 2.0

    Item(id="2", name="banana", price=0.5, active=False).save()
    all_items = Item.all()
    assert len(all_items) == 2

    cheap = Item.where("price", "<", 1.0).get()
    assert len(cheap) == 1
    assert cheap[0].name == "banana"

    ordered = Item.order_by("price", "desc").get()
    assert ordered[0].name == "pear"

    Item.find("2").delete()
    assert Item.find("2") is None
    assert len(Item.all()) == 1

    connection.schema_drop("items")
    connection.disconnect()


def test_sqlite_upsert_on_save():
    connection = _register(":memory:")
    _create_items_table(connection)

    Item(id="1", name="a", price=1.0, active=True).save()
    Item(id="1", name="b", price=3.0, active=False).save()
    found = Item.find("1")
    assert found.name == "b"
    assert float(found.price) == 3.0
    assert len(Item.all()) == 1
    connection.disconnect()


def test_sqlite_migrations_table():
    connection = _register(":memory:")
    assert connection.migrations_get() == []
    assert connection.migrations_max_batch() == 0

    connection.migrations_put("2026_01_01_create_items", 1)
    connection.migrations_put("2026_01_02_create_orders", 1)
    connection.migrations_put("2026_01_03_alter_items", 2)

    assert connection.migrations_get() == ["2026_01_01_create_items", "2026_01_02_create_orders", "2026_01_03_alter_items"]
    assert connection.migrations_max_batch() == 2
    assert connection.migrations_batch_for("2026_01_02_create_orders") == 1
    assert connection.migrations_batch_for("missing") is None

    connection.migrations_delete("2026_01_03_alter_items")
    assert connection.migrations_get() == ["2026_01_01_create_items", "2026_01_02_create_orders"]
    assert connection.migrations_max_batch() == 1
    connection.disconnect()


def test_sqlite_file_persists_across_connections(tmp_path):
    name = str(tmp_path / "persist")
    connection = _register(name)
    _create_items_table(connection)
    Item(id="1", name="kept", price=9.0, active=True).save()
    connection.disconnect()

    connection = _register(name)
    found = Item.find("1")
    assert found is not None
    assert found.name == "kept"
    connection.disconnect()
