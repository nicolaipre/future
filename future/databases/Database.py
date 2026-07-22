# Interface for all database types (MySQL, Elasticsearch, Clickhouse, Redis, etc.).
# Concrete databases implement these with their own storage primitives
# (tables, indices, keys, ...). Model only calls these names.


class Database:
    def __init__(self, host: str, port: int, username: str, password: str, database: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database

    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def save(self, model):
        raise NotImplementedError

    def find(self, model, id):
        raise NotImplementedError

    def all(self, model):
        raise NotImplementedError

    def get(self, model, wheres, limit=None, orders=None):
        raise NotImplementedError

    def delete(self, model):
        raise NotImplementedError

    def update(self, model, changes):
        raise NotImplementedError

    def schema_create(self, blueprint):
        raise NotImplementedError

    def schema_drop(self, name):
        raise NotImplementedError

    def migrations_get(self):
        raise NotImplementedError

    def migrations_put(self, name, batch):
        raise NotImplementedError

    def migrations_delete(self, name):
        raise NotImplementedError

    def migrations_max_batch(self):
        raise NotImplementedError

    def migrations_batch_for(self, name):
        raise NotImplementedError

    def transaction(self):
        client = getattr(self, "client", None)
        if client is None:
            self.connect()
            client = getattr(self, "client", None)
        if client is None or not hasattr(client, "begin"):
            raise NotImplementedError(f"{type(self).__name__} does not support transactions")
        return client.begin()
