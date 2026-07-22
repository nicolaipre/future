from future.databases.Connections import Connections
from future.databases.Database import Database
from future.models import Model, Query


class FakeDatabase(Database):
    def __init__(self):
        super().__init__(host="x", port=0, username="", password="", database="")
        self.rows = {}

    def connect(self):
        return self

    def disconnect(self):
        pass

    def save(self, model):
        data = model.to_dict()
        table = model.tableize()
        self.rows.setdefault(table, {})
        self.rows[table][str(data["id"])] = data
        return {"status": "saved", "id": data["id"]}

    def find(self, model, id):
        table = model.tableize()
        data = self.rows.get(table, {}).get(str(id))
        if data is None:
            return None
        return model.__class__(**data)

    def all(self, model):
        table = model.tableize()
        return [model.__class__(**row) for row in self.rows.get(table, {}).values()]

    def get(self, model, wheres, limit=None, orders=None):
        rows = self.all(model)
        for column, operator, value in wheres:
            if operator == "=":
                rows = [row for row in rows if getattr(row, column) == value]
            elif operator == ">":
                rows = [row for row in rows if getattr(row, column) > value]
            else:
                raise ValueError(operator)
        if orders:
            for column, direction in reversed(orders):
                rows.sort(key=lambda row: getattr(row, column), reverse=direction == "desc")
        if limit is not None:
            rows = rows[:limit]
        return rows

    def delete(self, model):
        table = model.tableize()
        self.rows.get(table, {}).pop(str(getattr(model, "id")), None)
        return {"status": "deleted"}

    def update(self, model, changes):
        table = model.tableize()
        row = self.rows.get(table, {}).get(str(getattr(model, "id")))
        if row is not None:
            row.update(changes)
        return {"status": "updated"}


class Item(Model):
    __table__ = "items"
    __connection__ = "fake"


def setup_module():
    Connections().set_connection_details({"default": "fake", "fake": FakeDatabase()})


def test_model_save_find_all():
    setup_module()
    Connections()._connections["fake"].rows = {}
    item = Item(id="1", name="a", price=10)
    item.save()
    found = Item.find("1")
    assert found is not None
    assert found.name == "a"
    assert len(Item.all()) == 1


def test_model_where_and_order():
    setup_module()
    db = Connections()._connections["fake"]
    db.rows = {}
    Item(id="1", name="a", price=10).save()
    Item(id="2", name="b", price=20).save()
    Item(id="3", name="c", price=30).save()
    rows = Item.where("price", ">", 10).order_by("price", "desc").get()
    assert [row.id for row in rows] == ["3", "2"]
    first = Item.where("name", "b").first()
    assert first is not None and first.id == "2"


def test_query_repr():
    q = Query(Item())
    assert "Query" in repr(q)
