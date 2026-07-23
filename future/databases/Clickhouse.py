from future.databases.Database import Database


class Clickhouse(Database):
    def __init__(self, host: str, port: int, username: str, password: str, database: str):
        super().__init__(host, port, username, password, database)
        self.client = None

    def connect(self):
        from clickhouse_driver import Client
        self.client = Client(host=self.host, port=self.port, user=self.username, password=self.password, database=self.database)
        return self.client

    def disconnect(self):
        self.client = None

    def save(self, model):
        if self.client is None:
            self.connect()
        table = model.tableize()
        data = model.to_dict()
        doc_id = data.get("id")
        if doc_id is not None:
            self.client.execute(f"ALTER TABLE `{table}` DELETE WHERE id = %(id)s", {"id": doc_id})
        columns = list(data.keys())
        col_sql = ", ".join(f"`{column}`" for column in columns)
        self.client.execute(f"INSERT INTO `{table}` ({col_sql}) VALUES", [tuple(data[column] for column in columns)])
        return {"status": "saved", "table": table, "id": doc_id}

    def find(self, model, id):
        if self.client is None:
            self.connect()
        table = model.tableize()
        rows, columns = self.client.execute(f"SELECT * FROM `{table}` WHERE id = %(id)s LIMIT 1", {"id": id}, with_column_types=True)
        if not rows:
            return None
        names = [column[0] for column in columns]
        return model.__class__(**dict(zip(names, rows[0], strict=True)))

    def all(self, model):
        if self.client is None:
            self.connect()
        table = model.tableize()
        rows, columns = self.client.execute(f"SELECT * FROM `{table}`", with_column_types=True)
        names = [column[0] for column in columns]
        return [model.__class__(**dict(zip(names, row, strict=True))) for row in rows]

    def get(self, model, wheres, limit=None, orders=None):
        if self.client is None:
            self.connect()
        table = model.tableize()
        clauses = []
        params = {}
        for index, (column, operator, value) in enumerate(wheres):
            if operator == "in":
                values = list(value)
                if not values:
                    return []
                keys = []
                for item_index, item in enumerate(values):
                    key = f"v{index}_{item_index}"
                    keys.append(f"%({key})s")
                    params[key] = item
                clauses.append(f"`{column}` IN ({', '.join(keys)})")
                continue
            if operator == "like":
                key = f"v{index}"
                clauses.append(f"`{column}` LIKE %({key})s")
                params[key] = value
                continue
            if operator not in ("=", ">", ">=", "<", "<=", "!="):
                raise ValueError(f"Unsupported operator: {operator}")
            key = f"v{index}"
            clauses.append(f"`{column}` {operator} %({key})s")
            params[key] = value
        sql = f"SELECT * FROM `{table}`"
        if clauses:
            sql += f" WHERE {' AND '.join(clauses)}"
        if orders:
            sql += " ORDER BY " + ", ".join(f"`{column}` {direction}" for column, direction in orders)
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        rows, columns = self.client.execute(sql, params, with_column_types=True)
        names = [column[0] for column in columns]
        return [model.__class__(**dict(zip(names, row, strict=True))) for row in rows]

    def delete(self, model):
        if self.client is None:
            self.connect()
        table = model.tableize()
        doc_id = getattr(model, "id", None)
        self.client.execute(f"ALTER TABLE `{table}` DELETE WHERE id = %(id)s", {"id": doc_id})
        return {"status": "deleted", "table": table, "id": doc_id}

    def update(self, model, changes):
        if self.client is None:
            self.connect()
        table = model.tableize()
        doc_id = getattr(model, "id", None)
        if not changes:
            return {"status": "noop", "table": table, "id": doc_id}
        set_sql = ", ".join(f"`{column}` = %({column})s" for column in changes.keys())
        params = dict(changes)
        params["id"] = doc_id
        self.client.execute(f"ALTER TABLE `{table}` UPDATE {set_sql} WHERE id = %(id)s", params)
        return {"status": "updated", "table": table, "id": doc_id}

    def schema_create(self, blueprint):
        if self.client is None:
            self.connect()
        definitions = []
        order_by = "tuple()"
        for column in blueprint.columns:
            if column.type == "string":
                ch_type = "String"
            elif column.type == "text":
                ch_type = "String"
            elif column.type == "integer":
                ch_type = "Int64"
            elif column.type == "float":
                ch_type = "Float64"
            elif column.type == "boolean":
                ch_type = "UInt8"
            elif column.type == "datetime":
                ch_type = "DateTime"
            else:
                raise ValueError(f"Unsupported column type: {column.type}")
            if column.is_nullable:
                ch_type = f"Nullable({ch_type})"
            definitions.append(f"`{column.name}` {ch_type}")
            if column.is_primary:
                order_by = f"`{column.name}`"
        create_sql = f"CREATE TABLE IF NOT EXISTS `{blueprint.name}` ({', '.join(definitions)}) ENGINE = MergeTree() ORDER BY {order_by}"
        self.client.execute(create_sql)
        return {"status": "created", "table": blueprint.name}

    def schema_drop(self, name):
        if self.client is None:
            self.connect()
        self.client.execute(f"DROP TABLE IF EXISTS `{name}`")
        return {"status": "dropped", "table": name}

    def migrations_get(self):
        if self.client is None:
            self.connect()
        self.client.execute("CREATE TABLE IF NOT EXISTS `migrations` (`name` String, `batch` Int32) ENGINE = MergeTree() ORDER BY (`batch`, `name`)")
        rows = self.client.execute("SELECT name FROM migrations ORDER BY batch, name")
        return [row[0] for row in rows]

    def migrations_put(self, name, batch):
        if self.client is None:
            self.connect()
        self.client.execute("CREATE TABLE IF NOT EXISTS `migrations` (`name` String, `batch` Int32) ENGINE = MergeTree() ORDER BY (`batch`, `name`)")
        self.client.execute("INSERT INTO migrations (name, batch) VALUES", [(name, batch)])

    def migrations_delete(self, name):
        if self.client is None:
            self.connect()
        self.client.execute("ALTER TABLE migrations DELETE WHERE name = %(name)s", {"name": name})

    def migrations_max_batch(self):
        if self.client is None:
            self.connect()
        self.client.execute("CREATE TABLE IF NOT EXISTS `migrations` (`name` String, `batch` Int32) ENGINE = MergeTree() ORDER BY (`batch`, `name`)")
        rows = self.client.execute("SELECT max(batch) FROM migrations")
        if not rows or rows[0][0] is None:
            return 0
        return int(rows[0][0])

    def migrations_batch_for(self, name):
        if self.client is None:
            self.connect()
        rows = self.client.execute("SELECT batch FROM migrations WHERE name = %(name)s", {"name": name})
        if not rows:
            return None
        return int(rows[0][0])
