from future.databases.Database import Database
import re


class MongoDB(Database):
    def __init__(self, host: str, port: int, username: str, password: str, database: str):
        super().__init__(host, port, username, password, database)
        self.client = None
        self.db = None

    def connect(self):
        from pymongo import MongoClient
        if self.username:
            uri = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            uri = f"mongodb://{self.host}:{self.port}/{self.database}"
        self.client = MongoClient(uri)
        self.db = self.client[self.database]
        return self.client

    def disconnect(self):
        if self.client is not None:
            self.client.close()
            self.client = None
            self.db = None

    def save(self, model):
        if self.db is None:
            self.connect()
        name = model.tableize()
        data = model.to_dict()
        doc_id = data.get("id")
        if doc_id is not None:
            self.db[name].replace_one({"id": doc_id}, data, upsert=True)
        else:
            self.db[name].insert_one(data)
        return {"status": "saved", "collection": name, "id": doc_id}

    def find(self, model, id):
        if self.db is None:
            self.connect()
        doc = self.db[model.tableize()].find_one({"id": id}, {"_id": 0})
        if doc is None:
            return None
        return model.__class__(**doc)

    def all(self, model):
        if self.db is None:
            self.connect()
        return [model.__class__(**doc) for doc in self.db[model.tableize()].find({}, {"_id": 0})]

    def get(self, model, wheres, limit=None, orders=None):
        if self.db is None:
            self.connect()
        query = {}
        for column, operator, value in wheres:
            if operator == "=":
                query[column] = value
            elif operator == "in":
                query[column] = {"$in": list(value)}
            elif operator == ">":
                query[column] = {"$gt": value}
            elif operator == ">=":
                query[column] = {"$gte": value}
            elif operator == "<":
                query[column] = {"$lt": value}
            elif operator == "<=":
                query[column] = {"$lte": value}
            elif operator == "!=":
                query[column] = {"$ne": value}
            elif operator == "like":
                parts = []
                for char in str(value):
                    if char == "%":
                        parts.append(".*")
                    elif char == "_":
                        parts.append(".")
                    else:
                        parts.append(re.escape(char))
                query[column] = {"$regex": "^" + "".join(parts) + "$"}
            else:
                raise ValueError(f"Unsupported operator: {operator}")
        cursor = self.db[model.tableize()].find(query, {"_id": 0})
        if orders:
            cursor = cursor.sort([(column, 1 if str(direction).upper() == "ASC" else -1) for column, direction in orders])
        if limit is not None:
            cursor = cursor.limit(int(limit))
        return [model.__class__(**doc) for doc in cursor]

    def delete(self, model):
        if self.db is None:
            self.connect()
        name = model.tableize()
        doc_id = getattr(model, "id", None)
        self.db[name].delete_one({"id": doc_id})
        return {"status": "deleted", "collection": name, "id": doc_id}

    def update(self, model, changes):
        if self.db is None:
            self.connect()
        name = model.tableize()
        doc_id = getattr(model, "id", None)
        if not changes:
            return {"status": "noop", "collection": name, "id": doc_id}
        self.db[name].update_one({"id": doc_id}, {"$set": changes})
        return {"status": "updated", "collection": name, "id": doc_id}

    def schema_create(self, blueprint):
        if self.db is None:
            self.connect()
        properties = {}
        required = []
        for column in blueprint.columns:
            if column.type == "string" or column.type == "text":
                bson_type = "string"
            elif column.type == "integer":
                bson_type = "long"
            elif column.type == "float":
                bson_type = "double"
            elif column.type == "boolean":
                bson_type = "bool"
            elif column.type == "datetime":
                bson_type = "date"
            else:
                raise ValueError(f"Unsupported column type: {column.type}")
            properties[column.name] = {"bsonType": bson_type}
            if not column.is_nullable and not column.is_primary:
                required.append(column.name)
        validator = {"$jsonSchema": {"bsonType": "object", "properties": properties}}
        if required:
            validator["$jsonSchema"]["required"] = required
        if blueprint.name in self.db.list_collection_names():
            return {"status": "exists", "collection": blueprint.name}
        self.db.create_collection(blueprint.name, validator=validator)
        for column in blueprint.columns:
            if column.is_unique or column.is_primary:
                self.db[blueprint.name].create_index(column.name, unique=True)
            elif column.is_index:
                self.db[blueprint.name].create_index(column.name)
        return {"status": "created", "collection": blueprint.name}

    def schema_drop(self, name):
        if self.db is None:
            self.connect()
        self.db.drop_collection(name)
        return {"status": "dropped", "collection": name}

    def migrations_get(self):
        if self.db is None:
            self.connect()
        return [doc["name"] for doc in self.db["_migrations"].find().sort([("batch", 1), ("name", 1)])]

    def migrations_put(self, name, batch):
        if self.db is None:
            self.connect()
        self.db["_migrations"].update_one({"name": name}, {"$set": {"name": name, "batch": batch}}, upsert=True)

    def migrations_delete(self, name):
        if self.db is None:
            self.connect()
        self.db["_migrations"].delete_one({"name": name})

    def migrations_max_batch(self):
        if self.db is None:
            self.connect()
        doc = self.db["_migrations"].find_one(sort=[("batch", -1)])
        if doc is None:
            return 0
        return int(doc["batch"])

    def migrations_batch_for(self, name):
        if self.db is None:
            self.connect()
        doc = self.db["_migrations"].find_one({"name": name})
        if doc is None:
            return None
        return int(doc["batch"])
