import pytest
from sqlalchemy import create_engine, text

from future.databases.Connections import Connections
from future.databases.Postgres import Postgres
from future.migrations.Schema import Schema
from future.models import Model


def _postgres_ready() -> bool:
    try:
        engine = create_engine("postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/st0nkz")
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _postgres_ready(), reason="Postgres st0nkz not reachable at 127.0.0.1:5432")


class Widget(Model):
    __table__ = "widgets_test"
    __connection__ = "postgres"


def test_postgres_schema_seed_and_query():
    postgres = Postgres(host="127.0.0.1", port=5432, username="postgres", password="postgres", database="st0nkz")
    Connections().set_connection_details({"default": "postgres", "postgres": postgres})
    postgres.schema_drop("widgets_test")
    Schema.connection("postgres")
    with Schema.create("widgets_test") as table:
        table.id()
        table.string("name")
        table.float("price")

    Widget(id="w1", name="alpha", price=10.5).save()
    Widget(id="w2", name="beta", price=20.0).save()

    found = Widget.find("w1")
    assert found is not None and found.name == "alpha"

    rows = Widget.where("price", ">", 15).order_by("price", "desc").get()
    assert len(rows) == 1 and rows[0].id == "w2"

    found.update(price=11.0)
    assert Widget.find("w1").price == 11.0 or float(Widget.find("w1").price) == 11.0

    found.delete()
    assert Widget.find("w1") is None
    assert len(Widget.all()) == 1

    postgres.schema_drop("widgets_test")
