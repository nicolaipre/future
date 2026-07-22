# Base class for migration files (Orator/Masonite-style).


class Migration:
    __connection__ = "default"

    def up(self):
        raise NotImplementedError

    def down(self):
        raise NotImplementedError
