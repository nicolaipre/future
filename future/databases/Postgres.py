from future.databases.Database import Database
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus


class Postgres(Database):
    def __init__(self, host: str, port: int, username: str, password: str, database: str):
        super().__init__(host, port, username, password, database)
        self.client = None

    def connect(self):
        url = f"postgresql+psycopg2://{quote_plus(self.username)}:{quote_plus(self.password)}@{self.host}:{self.port}/{self.database}"
        self.client = create_engine(url)
        return self.client

    def disconnect(self):
        if self.client is not None:
            self.client.dispose()
            self.client = None

    def save(self, model):
        if self.client is None:
            self.connect()
        table = model.tableize()
        data = model.to_dict()
        col_sql = ", ".join(f'"{column}"' for column in data.keys())
        val_sql = ", ".join(f":{column}" for column in data.keys())
        upd_sql = ", ".join(f'"{column}"=EXCLUDED."{column}"' for column in data.keys() if column != "id")
        if "id" in data and upd_sql:
            insert_sql = text(f'INSERT INTO "{table}" ({col_sql}) VALUES ({val_sql}) ON CONFLICT ("id") DO UPDATE SET {upd_sql}')
        else:
            insert_sql = text(f'INSERT INTO "{table}" ({col_sql}) VALUES ({val_sql})')
        with self.client.begin() as connection:
            connection.execute(insert_sql, data)
        return {"status": "saved", "table": table, "id": data.get("id")}

    def find(self, model, id):
        if self.client is None:
            self.connect()
        table = model.tableize()
        sql = text(f'SELECT * FROM "{table}" WHERE "id" = :id LIMIT 1')
        with self.client.connect() as connection:
            row = connection.execute(sql, {"id": id}).mappings().first()
        if row is None:
            return None
        return model.__class__(**dict(row))

    def all(self, model):
        if self.client is None:
            self.connect()
        table = model.tableize()
        sql = text(f'SELECT * FROM "{table}"')
        with self.client.connect() as connection:
            rows = connection.execute(sql).mappings().all()
        return [model.__class__(**dict(row)) for row in rows]

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
                    keys.append(f":{key}")
                    params[key] = item
                clauses.append(f'"{column}" IN ({", ".join(keys)})')
                continue
            if operator not in ("=", ">", ">=", "<", "<=", "!="):
                raise ValueError(f"Unsupported operator: {operator}")
            key = f"v{index}"
            clauses.append(f'"{column}" {operator} :{key}')
            params[key] = value
        sql = f'SELECT * FROM "{table}"'
        if clauses:
            sql += f" WHERE {' AND '.join(clauses)}"
        if orders:
            sql += " ORDER BY " + ", ".join(f'"{column}" {direction}' for column, direction in orders)
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        with self.client.connect() as connection:
            rows = connection.execute(text(sql), params).mappings().all()
        return [model.__class__(**dict(row)) for row in rows]

    def delete(self, model):
        if self.client is None:
            self.connect()
        table = model.tableize()
        sql = text(f'DELETE FROM "{table}" WHERE "id" = :id')
        with self.client.begin() as connection:
            connection.execute(sql, {"id": getattr(model, "id", None)})
        return {"status": "deleted", "table": table, "id": getattr(model, "id", None)}

    def update(self, model, changes):
        if self.client is None:
            self.connect()
        table = model.tableize()
        if not changes:
            return {"status": "noop", "table": table}
        set_sql = ", ".join(f'"{column}"=:{column}' for column in changes.keys())
        params = dict(changes)
        params["id"] = getattr(model, "id", None)
        sql = text(f'UPDATE "{table}" SET {set_sql} WHERE "id" = :id')
        with self.client.begin() as connection:
            connection.execute(sql, params)
        return {"status": "updated", "table": table, "id": params["id"]}

    def schema_create(self, blueprint):
        if self.client is None:
            self.connect()
        definitions = []
        uniques = []
        indexes = []
        for column in blueprint.columns:
            if column.type == "string":
                sql_type = f"VARCHAR({column.length or 255})"
            elif column.type == "text":
                sql_type = "TEXT"
            elif column.type == "integer":
                sql_type = "BIGINT"
            elif column.type == "float":
                sql_type = "DOUBLE PRECISION"
            elif column.type == "boolean":
                sql_type = "BOOLEAN"
            elif column.type == "datetime":
                sql_type = "TIMESTAMP"
            else:
                raise ValueError(f"Unsupported column type: {column.type}")
            null_sql = "NULL" if column.is_nullable else "NOT NULL"
            default_sql = ""
            if column.default_value is not None:
                if isinstance(column.default_value, str):
                    default_sql = f" DEFAULT '{column.default_value}'"
                else:
                    default_sql = f" DEFAULT {column.default_value}"
            primary_sql = " PRIMARY KEY" if column.is_primary else ""
            definitions.append(f"\"{column.name}\" {sql_type} {null_sql}{default_sql}{primary_sql}")
            if column.is_unique and not column.is_primary:
                uniques.append(f"UNIQUE (\"{column.name}\")")
            if column.is_index and not column.is_primary and not column.is_unique:
                indexes.append(column.name)
        parts = definitions + uniques
        create_sql = text(f"CREATE TABLE IF NOT EXISTS \"{blueprint.name}\" ({', '.join(parts)})")
        with self.client.begin() as connection:
            connection.execute(create_sql)
            for index_name in indexes:
                connection.execute(text(f"CREATE INDEX IF NOT EXISTS \"index_{blueprint.name}_{index_name}\" ON \"{blueprint.name}\" (\"{index_name}\")"))
        return {"status": "created", "table": blueprint.name}

    def schema_drop(self, name):
        if self.client is None:
            self.connect()
        with self.client.begin() as connection:
            connection.execute(text(f"DROP TABLE IF EXISTS \"{name}\""))
        return {"status": "dropped", "table": name}

    def table_exists(self, name):
        if self.client is None:
            self.connect()
        sql = text("SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = :name LIMIT 1")
        with self.client.connect() as connection:
            return connection.execute(sql, {"name": name}).first() is not None

    def _ensure_migrations_table(self):
        if self.client is None:
            self.connect()
        sql = text("CREATE TABLE IF NOT EXISTS \"migrations\" (\"name\" VARCHAR(255) PRIMARY KEY, \"batch\" INT NOT NULL)")
        with self.client.begin() as connection:
            connection.execute(sql)

    def migrations_get(self):
        self._ensure_migrations_table()
        with self.client.connect() as connection:
            rows = connection.execute(text("SELECT \"name\" FROM \"migrations\" ORDER BY \"batch\", \"name\"")).mappings().all()
        return [row["name"] for row in rows]

    def migrations_put(self, name, batch):
        self._ensure_migrations_table()
        sql = text("INSERT INTO \"migrations\" (\"name\", \"batch\") VALUES (:name, :batch) ON CONFLICT (\"name\") DO UPDATE SET \"batch\" = EXCLUDED.\"batch\"")
        with self.client.begin() as connection:
            connection.execute(sql, {"name": name, "batch": batch})

    def migrations_delete(self, name):
        self._ensure_migrations_table()
        sql = text("DELETE FROM \"migrations\" WHERE \"name\" = :name")
        with self.client.begin() as connection:
            connection.execute(sql, {"name": name})

    def migrations_max_batch(self):
        self._ensure_migrations_table()
        with self.client.connect() as connection:
            row = connection.execute(text("SELECT MAX(\"batch\") AS batch FROM \"migrations\"")).mappings().first()
        if row is None or row["batch"] is None:
            return 0
        return int(row["batch"])

    def migrations_batch_for(self, name):
        self._ensure_migrations_table()
        with self.client.connect() as connection:
            row = connection.execute(text("SELECT \"batch\" FROM \"migrations\" WHERE \"name\" = :name"), {"name": name}).mappings().first()
        if row is None:
            return None
        return int(row["batch"])
