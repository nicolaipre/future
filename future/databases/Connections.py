# Named connection registry (Masonite-style logic).
# App config: DB = Connections().set_connection_details(DATABASES)
# Models: Connections().get_connection(name)


class Connections:
    _connections = {}
    _default = None

    def set_connection_details(self, databases):
        self.__class__._default = databases["default"]
        self.__class__._connections = {name: connection for name, connection in databases.items() if name != "default"}
        return self

    def get_connection(self, name="default"):
        if name == "default":
            name = self.__class__._default
        if not name or name not in self.__class__._connections:
            raise RuntimeError("No database connections registered. Pass DATABASES in Future(config={...}) or call Connections().set_connection_details(DATABASES).")
        return self.__class__._connections[name]
