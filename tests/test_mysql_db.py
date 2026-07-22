from unittest.mock import MagicMock, patch

from future.databases.MySQL import MySQL
from future.models import Model


class Row(Model):
    __table__ = "rows"


def test_mysql_find():
    mysql = MySQL(host="localhost", port=3306, username="u", password="p", database="db")
    connection = MagicMock()
    connection.execute.return_value.mappings.return_value.first.return_value = {"id": "1", "name": "n"}
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value = connection
    engine.connect.return_value.__exit__.return_value = None
    mysql.client = engine

    found = mysql.find(Row(), "1")
    assert found is not None and found.name == "n"
    assert "SELECT" in str(connection.execute.call_args[0][0])


def test_mysql_get_builds_where_sql():
    mysql = MySQL(host="localhost", port=3306, username="u", password="p", database="db")
    connection = MagicMock()
    connection.execute.return_value.mappings.return_value.all.return_value = [{"id": "2", "price": 9}]
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value = connection
    engine.connect.return_value.__exit__.return_value = None
    mysql.client = engine

    rows = mysql.get(Row(), wheres=[("price", ">", 1)], limit=10, orders=[("price", "desc")])
    assert len(rows) == 1 and rows[0].id == "2"
    sql = str(connection.execute.call_args[0][0])
    params = connection.execute.call_args[0][1]
    assert "price" in sql and ">" in sql
    assert params["v0"] == 1


def test_mysql_connect_builds_url():
    with patch("future.databases.MySQL.create_engine") as create_engine:
        mysql = MySQL(host="h", port=3306, username="u", password="p", database="d")
        server = MagicMock()
        server.begin.return_value.__enter__.return_value = MagicMock()
        server.begin.return_value.__exit__.return_value = None
        create_engine.side_effect = [server, MagicMock()]
        mysql.connect()
        urls = [call.args[0] for call in create_engine.call_args_list]
        assert any(url.endswith("/d") and "mysql+pymysql://u:p@h:3306/d" == url for url in urls)
        assert any(url.endswith("/") for url in urls)
