from future.databases.Database import Database
from future.plugins.ElasticsearchPlugin import ElasticsearchPlugin


class Elasticsearch(Database):
    def __init__(self, host: str, port: int, username: str, password: str, database: str = ""):
        super().__init__(host, port, username, password, database)
        self.client = ElasticsearchPlugin(host=host, username=username, password=password)

    def connect(self):
        return self.client

    def disconnect(self):
        pass

    def save(self, model):
        name = model.tableize()
        return self.client.index_document(name, model.to_dict(), document_id=getattr(model, "id", None))

    def find(self, model, id):
        result = self.client.get_document(model.tableize(), id)
        if not result or "error" in result or "_source" not in result:
            return None
        return model.__class__(**result["_source"])

    def all(self, model):
        result = self.client.search_documents(model.tableize(), {"query": {"match_all": {}}, "size": 10000})
        if not result or "error" in result:
            return []
        return [model.__class__(**hit["_source"]) for hit in result.get("hits", {}).get("hits", [])]

    def get(self, model, wheres, limit=None, orders=None):
        must = []
        for column, operator, value in wheres:
            if operator == "=":
                must.append({"match": {column: value}})
            elif operator == ">":
                must.append({"range": {column: {"gt": value}}})
            elif operator == ">=":
                must.append({"range": {column: {"gte": value}}})
            elif operator == "<":
                must.append({"range": {column: {"lt": value}}})
            elif operator == "<=":
                must.append({"range": {column: {"lte": value}}})
            elif operator == "!=":
                must.append({"bool": {"must_not": [{"match": {column: value}}]}})
            elif operator == "in":
                must.append({"terms": {column: list(value)}})
            else:
                raise ValueError(f"Unsupported operator: {operator}")
        size = limit if limit is not None else 10000
        body = {"query": {"bool": {"must": must}}, "size": size}
        if orders:
            body["sort"] = [{column: {"order": direction}} for column, direction in orders]
        result = self.client.search_documents(model.tableize(), body)
        if not result or "error" in result:
            return []
        return [model.__class__(**hit["_source"]) for hit in result.get("hits", {}).get("hits", [])]

    def delete(self, model):
        return self.client.delete_document(model.tableize(), getattr(model, "id", None))

    def update(self, model, changes):
        return self.client.update_document(model.tableize(), getattr(model, "id", None), changes)

    def schema_create(self, blueprint):
        properties = {}
        for column in blueprint.columns:
            if column.type == "string" and (column.is_primary or column.name == "id"):
                properties[column.name] = {"type": "keyword"}
            elif column.type == "string":
                properties[column.name] = {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}
            elif column.type == "text":
                properties[column.name] = {"type": "text"}
            elif column.type == "integer":
                properties[column.name] = {"type": "long"}
            elif column.type == "float":
                properties[column.name] = {"type": "double"}
            elif column.type == "boolean":
                properties[column.name] = {"type": "boolean"}
            elif column.type == "datetime":
                properties[column.name] = {"type": "date"}
            else:
                raise ValueError(f"Unsupported column type: {column.type}")
        mapping = {"properties": properties}
        if self.client.index_exists(blueprint.name):
            return {"status": "exists", "index": blueprint.name}
        result = self.client.create_index(blueprint.name, mapping=mapping)
        if isinstance(result, dict) and "error" in result:
            raise RuntimeError(result["error"])
        return result

    def schema_drop(self, name):
        if not self.client.index_exists(name):
            return {"status": "missing", "index": name}
        result = self.client.delete_index(name)
        if isinstance(result, dict) and "error" in result:
            raise RuntimeError(result["error"])
        return result

    def _ensure_migrations_index(self):
        if self.client.index_exists("migrations"):
            return
        mapping = {"properties": {"name": {"type": "keyword"}, "batch": {"type": "integer"}}}
        result = self.client.create_index("migrations", mapping=mapping)
        if isinstance(result, dict) and "error" in result:
            raise RuntimeError(result["error"])

    def migrations_get(self):
        self._ensure_migrations_index()
        result = self.client.search_documents("migrations", {"query": {"match_all": {}}, "size": 10000, "sort": [{"batch": "asc"}, {"name": "asc"}]})
        if not result or "error" in result:
            return []
        return [hit["_source"]["name"] for hit in result.get("hits", {}).get("hits", [])]

    def migrations_put(self, name, batch):
        self._ensure_migrations_index()
        result = self.client.index_document("migrations", {"name": name, "batch": batch}, document_id=name)
        if isinstance(result, dict) and "error" in result:
            raise RuntimeError(result["error"])

    def migrations_delete(self, name):
        self._ensure_migrations_index()
        result = self.client.delete_document("migrations", name)
        if isinstance(result, dict) and "error" in result:
            raise RuntimeError(result["error"])

    def migrations_max_batch(self):
        self._ensure_migrations_index()
        result = self.client.search_documents("migrations", {"query": {"match_all": {}}, "size": 0, "aggs": {"max_batch": {"max": {"field": "batch"}}}})
        if not result or "error" in result:
            return 0
        value = result.get("aggregations", {}).get("max_batch", {}).get("value")
        if value is None:
            return 0
        return int(value)

    def migrations_batch_for(self, name):
        self._ensure_migrations_index()
        result = self.client.get_document("migrations", name)
        if not result or "error" in result or "_source" not in result:
            return None
        return int(result["_source"]["batch"])
