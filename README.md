# ✨ Future ✨
Next Gen. [ASGI](https://github.com/django/asgiref) Framework for minimal Web APIs
- [ASGI](https://asgi.readthedocs.io/)
- [ASGI GitHub](https://github.com/django/asgiref)
- [ASGI Fundamentals](https://www.youtube.com/watch?v=ai7y--6ElAE&list=PLJ_usHaf3fgO_PgB1zTSlKVSqDdvh49bi)

## Build Status
[![Build Status](https://github.com/Defendinary/future/workflows/Test%20Suite/badge.svg)](https://github.com/Defendinary/future/actions)
[![Package version](https://badge.fury.io/py/star.svg)](https://pypi.org/project/future-api/)

<!--[![codecov](https://codecov.io/gh/Defendinary/future/branch/master/graph/badge.svg)](https://codecov.io/gh/Defendinary/future)
[![Changelog](https://img.shields.io/badge/changelog-v0.14.6-green.svg)](https://github.com/Defendinary/future/blob/master/CHANGELOG.md)-->

## Versioning

This project uses [Semantic Versioning](https://semver.org/) and automatic version incrementing via git tags.

### Current Version
```bash
make version
# Current version: 0.3.1
```

### GitHub Workflows
All releases, testing, and publishing are handled automatically by GitHub workflows:
- **CI**: Runs on every push/PR (linting, type checking, tests, building)
- **Publish**: Automatically publishes to PyPI when tags are pushed
- **Versioning**: Uses `poetry-dynamic-versioning` for automatic version management

### Changelog
See [CHANGELOG.md](CHANGELOG.md) for detailed release history and changes.

# Usage
```shell
$ poetry init
$ poetry add future-api
$ poetry shell

# Scaffold default, nice & clean application structure
$ future init .
$ future init projectname

# Show all routes
$ future routes
```


## Will be added later
```shell
# Run app
$ future run

# Create new controller
$ future controller TestController

# Create new middleware
$ future middleware TestMiddleware

# Create new model
$ future model TestModel

# Install Authentication
$ future install SSOAuthentication
$ future install SAMLAuthentication
$ future install BasicAuthentication

# Install custom Middlewares
$ future install ResponseCodeConfuser
$ future install SQLiResponseConfuser
```