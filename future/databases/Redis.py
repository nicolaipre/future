import json

from future.databases.Database import Database


class Redis(Database):
    def __init__(self, host: str, port: int, username: str, password: str, database: str):
        super().__init__(host, port, username, password, database)
        self.client = None

    def connect(self):
        import redis
        db_index = int(self.database) if str(self.database).isdigit() else 0
        self.client = redis.Redis(host=self.host or "127.0.0.1", port=self.port or 6379, username=self.username or None, password=self.password or None, db=db_index, decode_responses=True)
        self.client.ping()
        return self.client

    def disconnect(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    def _key(self, table, id):
        return f"{table}:{id}"

    def _ids_key(self, table):
        return f"{table}:ids"

    def save(self, model):
        if self.client is None:
            self.connect()
        table = model.tableize()
        data = model.to_dict()
        doc_id = data.get("id")
        if doc_id is None:
            raise ValueError("Redis models require an id for save()")
        self.client.set(self._key(table, doc_id), json.dumps(data))
        self.client.sadd(self._ids_key(table), str(doc_id))
        return {"status": "saved", "key": self._key(table, doc_id), "id": doc_id}

    def find(self, model, id):
        if self.client is None:
            self.connect()
        raw = self.client.get(self._key(model.tableize(), id))
        if raw is None:
            return None
        return model.__class__(**json.loads(raw))

    def all(self, model):
        if self.client is None:
            self.connect()
        table = model.tableize()
        ids = self.client.smembers(self._ids_key(table))
        rows = []
        for doc_id in ids:
            raw = self.client.get(self._key(table, doc_id))
            if raw is not None:
                rows.append(model.__class__(**json.loads(raw)))
        return rows

    def get(self, model, wheres, limit=None, orders=None):
        rows = self.all(model)
        for column, operator, value in wheres:
            filtered = []
            for row in rows:
                current = getattr(row, column, None)
                if operator == "=" and current == value:
                    filtered.append(row)
                elif operator == "!=" and current != value:
                    filtered.append(row)
                elif operator == ">" and current is not None and current > value:
                    filtered.append(row)
                elif operator == ">=" and current is not None and current >= value:
                    filtered.append(row)
                elif operator == "<" and current is not None and current < value:
                    filtered.append(row)
                elif operator == "<=" and current is not None and current <= value:
                    filtered.append(row)
                elif operator == "in" and current in list(value):
                    filtered.append(row)
                elif operator not in ("=", "!=", ">", ">=", "<", "<=", "in"):
                    raise ValueError(f"Unsupported operator: {operator}")
            rows = filtered
        if orders:
            for column, direction in reversed(orders):
                rows.sort(key=lambda row: getattr(row, column, None), reverse=str(direction).upper() == "DESC")
        if limit is not None:
            rows = rows[: int(limit)]
        return rows

    def delete(self, model):
        if self.client is None:
            self.connect()
        table = model.tableize()
        doc_id = getattr(model, "id", None)
        self.client.delete(self._key(table, doc_id))
        self.client.srem(self._ids_key(table), str(doc_id))
        return {"status": "deleted", "key": self._key(table, doc_id), "id": doc_id}

    def update(self, model, changes):
        if self.client is None:
            self.connect()
        table = model.tableize()
        doc_id = getattr(model, "id", None)
        if not changes:
            return {"status": "noop", "id": doc_id}
        raw = self.client.get(self._key(table, doc_id))
        if raw is None:
            return {"status": "missing", "id": doc_id}
        data = json.loads(raw)
        data.update(changes)
        self.client.set(self._key(table, doc_id), json.dumps(data))
        return {"status": "updated", "id": doc_id}

    def schema_create(self, blueprint):
        raise NotImplementedError("Redis has no schema; structural migrations are unsupported")

    def schema_drop(self, name):
        raise NotImplementedError("Redis has no schema; structural migrations are unsupported")

    def migrations_get(self):
        raise NotImplementedError("Redis has no schema; structural migrations are unsupported")

    def migrations_put(self, name, batch):
        raise NotImplementedError("Redis has no schema; structural migrations are unsupported")

    def migrations_delete(self, name):
        raise NotImplementedError("Redis has no schema; structural migrations are unsupported")

    def migrations_max_batch(self):
        raise NotImplementedError("Redis has no schema; structural migrations are unsupported")

    def migrations_batch_for(self, name):
        raise NotImplementedError("Redis has no schema; structural migrations are unsupported")
