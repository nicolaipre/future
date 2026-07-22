# Schema blueprint — collects portable columns; applied on context exit.


from .Column import Column
from future.databases.Connections import Connections


class Blueprint:
    def __init__(self, name, connection_name, action="create"):
        self.name = name
        self.connection_name = connection_name
        self.action = action
        self.columns = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            return False
        connection = Connections().get_connection(self.connection_name)
        if self.action == "create":
            connection.schema_create(self)
        return False

    def _add(self, column):
        self.columns.append(column)
        return column

    def id(self):
        return self._add(Column("id", "string", length=255)).primary()

    def string(self, name, length=255):
        return self._add(Column(name, "string", length=length))

    def text(self, name):
        return self._add(Column(name, "text"))

    def integer(self, name):
        return self._add(Column(name, "integer"))

    def float(self, name):
        return self._add(Column(name, "float"))

    def boolean(self, name):
        return self._add(Column(name, "boolean"))

    def datetime(self, name):
        return self._add(Column(name, "datetime"))

    def timestamps(self):
        self.datetime("created_at").nullable()
        self.datetime("updated_at").nullable()
        return self
