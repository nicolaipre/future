import pytest
from sqlalchemy import create_engine, text

from future.databases.Connections import Connections
from future.databases.MySQL import MySQL
from future.migrations.Schema import Schema
from future.models import Model


def _mysql_ready() -> bool:
    try:
        engine = create_engine("mysql+pymysql://root:password@127.0.0.1:3306/st0nkz")
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _mysql_ready(), reason="MySQL st0nkz not reachable at 127.0.0.1:3306")


class Widget(Model):
    __table__ = "widgets_test"
    __connection__ = "mysql"


def test_mysql_schema_seed_and_query():
    mysql = MySQL(host="127.0.0.1", port=3306, username="root", password="password", database="st0nkz")
    Connections().set_connection_details({"default": "mysql", "mysql": mysql})
    mysql.schema_drop("widgets_test")
    Schema.connection("mysql")
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

    mysql.schema_drop("widgets_test")
