from future.databases.Connections import Connections
from future.logger import log
import inflection
import json

# Active-record base model (Masonite-style).
# Trade.find("1"), Trade.where("user_id", "123").get(), trade.save()


class ModelMeta(type):
    def __getattr__(self, attribute, *args, **kwargs):
        instantiated = self()
        return getattr(instantiated, attribute)


class Query:
    def __init__(self, model):
        self.model = model
        self.wheres = []
        self.orders = []

    def where(self, column, *args):
        if len(args) == 1:
            operator, value = "=", args[0]
        else:
            operator, value = args[0], args[1]
        self.wheres.append((column, operator, value))
        return self

    def order_by(self, column, direction="asc"):
        self.orders.append((column, direction))
        return self

    def get(self):
        return self.model.connection().get(self.model, self.wheres, orders=self.orders)

    def first(self):
        results = self.model.connection().get(self.model, self.wheres, limit=1, orders=self.orders)
        return results[0] if results else None

    def __repr__(self):
        return "<Query; call .get() or .first() to execute>"

    def __len__(self):
        raise TypeError("Query has no len(); call .get() or .first() first")

    def __iter__(self):
        raise TypeError("Query is not iterable; call .get() or .first() first")


class Model(metaclass=ModelMeta):
    __table__ = None
    __connection__ = "default"

    def __init__(self, **attributes):
        for key, value in attributes.items():
            setattr(self, key, value)

    # Why do we use __getattr__ for find and all, but not for save, delete, update?
    # ModelMeta.__getattr__ turns Trade.find into “make an empty instance, then get find from it.” The instance __getattr__ then returns the callable. That lets class-level calls work without @classmethod (which this codebase forbids).
    def __getattr__(self, attribute):
        if attribute == "find":
            def find(id):
                return self.connection().find(self, id)
            return find
        if attribute == "all":
            def all():
                return self.connection().all(self)
            return all
        if attribute == "where":
            def where(*args):
                return Query(self).where(*args)
            return where
        if attribute == "order_by":
            def order_by(*args):
                return Query(self).order_by(*args)
            return order_by
        if attribute == "transaction":
            def transaction():
                return self.connection().transaction()
            return transaction
        if attribute == "eager_load":
            def eager_load(models, name, related, foreign_key=None, kind="belongs_to"):
                if not models:
                    return models
                if kind == "belongs_to":
                    key = foreign_key or (inflection.underscore(related.__name__) + "_id")
                    ids = list({getattr(model, key, None) for model in models if getattr(model, key, None) is not None})
                    related_map = {}
                    if ids:
                        for row in related.where("id", "in", ids).get():
                            related_map[getattr(row, "id")] = row
                    for model in models:
                        setattr(model, name, related_map.get(getattr(model, key, None)))
                    return models
                key = foreign_key or (inflection.underscore(models[0].__class__.__name__) + "_id")
                parent_ids = [getattr(model, "id") for model in models if getattr(model, "id", None) is not None]
                children = related.where(key, "in", parent_ids).get() if parent_ids else []
                grouped = {}
                for child in children:
                    grouped.setdefault(getattr(child, key), []).append(child)
                for model in models:
                    setattr(model, name, grouped.get(getattr(model, "id"), []))
                return models
            return eager_load
        raise AttributeError(attribute)

    def tableize(self):
        return self.__table__ or inflection.tableize(self.__class__.__name__)

    def connection(self):
        name = self.__connection__
        if name == "default":
            name = Connections._default
        connection = Connections().get_connection(self.__connection__)
        log.debug("%s using database connection %s (%s)", self.__class__.__name__, name, type(connection).__name__)
        table_exists = getattr(connection, "table_exists", None)
        if table_exists is not None:
            table = self.tableize()
            if not table_exists(table):
                message = f'Table "{table}" does not exist on connection {name}. Run: future migrate'
                log.warning(message)
                raise RuntimeError(message)
        return connection

    def to_dict(self):
        return dict(self.__dict__)

    def to_json(self):
        return json.dumps(self.to_dict())

    def openapi_schema(self):
        from datetime import date, datetime
        from typing import get_args, get_origin, Union
        import types
        properties = {}
        required = []
        annotations = {}
        for cls in reversed(type(self).__mro__):
            if cls is object:
                continue
            annotations.update(getattr(cls, "__annotations__", {}))
        for name, annotation in annotations.items():
            if name.startswith("_"):
                continue
            optional = False
            current = annotation
            origin = get_origin(current)
            args = get_args(current)
            if origin is Union or isinstance(current, types.UnionType) or origin is types.UnionType:
                non_none = [item for item in args if item is not type(None)]
                if type(None) in args and len(non_none) == 1:
                    optional = True
                    current = non_none[0]
                    origin = get_origin(current)
                    args = get_args(current)
            if origin is list:
                item = args[0] if args else str
                if isinstance(item, type) and issubclass(item, Model):
                    item_schema = {"$ref": f"#/components/schemas/{item.__name__}"}
                elif item is int:
                    item_schema = {"type": "integer"}
                elif item is float:
                    item_schema = {"type": "number"}
                elif item is bool:
                    item_schema = {"type": "boolean"}
                elif item in (datetime, date):
                    item_schema = {"type": "string", "format": "date-time" if item is datetime else "date"}
                else:
                    item_schema = {"type": "string"}
                properties[name] = {"type": "array", "items": item_schema}
            elif isinstance(current, type) and issubclass(current, Model):
                properties[name] = {"$ref": f"#/components/schemas/{current.__name__}"}
            elif current is int:
                properties[name] = {"type": "integer"}
            elif current is float:
                properties[name] = {"type": "number"}
            elif current is bool:
                properties[name] = {"type": "boolean"}
            elif current is datetime:
                properties[name] = {"type": "string", "format": "date-time"}
            elif current is date:
                properties[name] = {"type": "string", "format": "date"}
            elif current is dict:
                properties[name] = {"type": "object"}
            else:
                properties[name] = {"type": "string"}
            if not optional:
                required.append(name)
        schema = {"type": "object", "properties": properties}
        if required:
            schema["required"] = required
        return schema

    def __repr__(self):
        return str(self.to_dict())

    def save(self):
        return self.connection().save(self)

    def delete(self):
        return self.connection().delete(self)

    def update(self, **changes):
        for key, value in changes.items():
            setattr(self, key, value)
        self.connection().update(self, changes)
        return self

    def belongs_to(self, related, foreign_key=None):
        key = foreign_key or (inflection.underscore(related.__name__) + "_id")
        related_id = getattr(self, key, None)
        if related_id is None:
            return None
        return related.find(related_id)

    def has_many(self, related, foreign_key=None):
        key = foreign_key or (inflection.underscore(self.__class__.__name__) + "_id")
        return related.where(key, getattr(self, "id")).get()
