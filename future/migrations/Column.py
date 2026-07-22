# Portable column definition for Schema blueprints (Orator/Masonite-style).


class Column:
    def __init__(self, name, type, length=None):
        self.name = name
        self.type = type
        self.length = length
        self.is_nullable = False
        self.is_unique = False
        self.is_primary = False
        self.is_index = False
        self.default_value = None

    def nullable(self):
        self.is_nullable = True
        return self

    def unique(self):
        self.is_unique = True
        return self

    def primary(self):
        self.is_primary = True
        return self

    def index(self):
        self.is_index = True
        return self

    def default(self, value):
        self.default_value = value
        return self
