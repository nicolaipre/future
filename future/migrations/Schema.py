# Orator/Masonite-style schema facade. Resolves connections via Connections.


from .Blueprint import Blueprint
from future.databases.Connections import Connections


class SchemaMeta(type):
    def connection(cls, name):
        cls._connection_name = name
        return cls

    def create(cls, name):
        return Blueprint(name, cls._connection_name, action="create")

    def drop(cls, name):
        Connections().get_connection(cls._connection_name).schema_drop(name)


class Schema(metaclass=SchemaMeta):
    _connection_name = "default"
