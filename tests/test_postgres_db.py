from unittest.mock import MagicMock, patch

from future.databases.Postgres import Postgres
from future.models import Model


class Row(Model):
    __table__ = "rows"


def test_postgres_find():
    postgres = Postgres(host="localhost", port=5432, username="u", password="p", database="db")
    connection = MagicMock()
    connection.execute.return_value.mappings.return_value.first.return_value = {"id": "1", "name": "n"}
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value = connection
    engine.connect.return_value.__exit__.return_value = None
    postgres.client = engine

    found = postgres.find(Row(), "1")
    assert found is not None and found.name == "n"
    assert "SELECT" in str(connection.execute.call_args[0][0])


def test_postgres_get_builds_where_sql():
    postgres = Postgres(host="localhost", port=5432, username="u", password="p", database="db")
    connection = MagicMock()
    connection.execute.return_value.mappings.return_value.all.return_value = [{"id": "2", "price": 9}]
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value = connection
    engine.connect.return_value.__exit__.return_value = None
    postgres.client = engine

    rows = postgres.get(Row(), wheres=[("price", ">", 1)], limit=10, orders=[("price", "desc")])
    assert len(rows) == 1 and rows[0].id == "2"
    sql = str(connection.execute.call_args[0][0])
    params = connection.execute.call_args[0][1]
    assert "price" in sql and ">" in sql
    assert params["v0"] == 1


def test_postgres_connect_builds_url():
    with patch("future.databases.Postgres.create_engine") as create_engine:
        postgres = Postgres(host="h", port=5432, username="u", password="p@ss", database="d")
        create_engine.return_value = MagicMock()
        postgres.connect()
        url = create_engine.call_args[0][0]
        assert url == "postgresql+psycopg2://u:p%40ss@h:5432/d"
