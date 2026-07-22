# Base class for database seeders (Orator/Masonite-style).


class Seeder:
    def run(self):
        raise NotImplementedError

    def call(self, seeder_class):
        seeder_class().run()
