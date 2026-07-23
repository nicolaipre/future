# Future
Minimal, decorator-free [ASGI](https://asgi.readthedocs.io/) framework for Python APIs — routing, middleware, Active Record, migrations, seeds, OpenAPI, and interval tasks.

[![Build Status](https://github.com/nicolaipre/future/actions/workflows/ci.yml/badge.svg)](https://github.com/nicolaipre/future/actions)
[![Package version](https://badge.fury.io/py/future-framework.svg)](https://pypi.org/project/future-framework/)
[![codecov](https://codecov.io/gh/nicolaipre/future/branch/master/graph/badge.svg)](https://codecov.io/gh/nicolaipre/future)

## Documentation
Published at **[nicolaipre.github.io/future](https://nicolaipre.github.io/future/)**. To preview locally: `poetry install --with docs && poetry run mkdocs serve`.

## Install
```bash
poetry add future-framework
# or from git: poetry add git+https://github.com/nicolaipre/future.git@master
poetry run future init myproject
```

Import name is `future` (`from future.application import Future`).

## Hello
```python
from future.application import Future
from future.controllers import Controller
from future.lifespan import Lifespan
from future.response import Response
from future.routing import Get, RouteGroup

class HomeController(Controller):
    async def index(self) -> Response:
        return self.response.json({"ok": True})

app = Future(lifespan=Lifespan([], [], []), config={"APP_DOMAIN": "", "APP_NAME": "Demo"})
app.add_routes([RouteGroup(name="Main", routes=[Get("/", HomeController.index, "home")])])
app.run(host="127.0.0.1", port=8000)
```

## License
See [LICENSE](LICENSE). Versioning: [CHANGELOG.md](CHANGELOG.md).
