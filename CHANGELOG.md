# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **CLI Tool**: New `future` command-line interface with `routes` and `init` commands
- **Project Scaffolding**: `future init` creates complete project structure with proper templates
- **Dynamic App Detection**: CLI intelligently finds app instances in `run.py`, `example.py`
- **WebSocket Support**: Native WebSocket routing with `WebSocket` route class
- **Cron Scheduler**: Built-in cron-like scheduler integrated with app lifespan
- **GraphQL Integration**: Strawberry GraphQL support with proper type definitions
- **Middleware System**: Hierarchical middleware with request/response interception
- **Route Groups**: Nested route groups with subdomain and prefix support
- **Type Safety**: Comprehensive type annotations throughout the codebase
- **Test Coverage**: 13 comprehensive tests covering all major functionality

### Changed
- **Architecture**: Complete refactor to minimal, decorator-free design
- **Static Methods**: All controller methods use static patterns without `self` parameters
- **Middleware Behavior**: Any return from middleware interrupts request (including `None`)
- **Response Handling**: Native response objects with proper ASGI integration
- **Logging**: Centralized logging with colored formatter matching uvicorn style
- **Configuration**: Simplified config system with environment variable support

### Removed
- **Decorators**: Eliminated all decorators including `@dataclass`, `@property`
- **Database Layer**: Removed SQLAlchemy integration (can be added as plugin)
- **Legacy Code**: Cleaned up old request/response modules
- **Boilerplate**: Removed separate boilerplate.py (integrated into CLI)
- **Complex Dependencies**: Simplified dependency tree

### Fixed
- **Type Checking**: Resolved all mypy errors with proper type annotations
- **Linting**: Fixed all ruff linting issues including imports and formatting
- **Import Errors**: Corrected module imports throughout the codebase
- **Middleware Types**: Fixed middleware class references (not strings)
- **GraphQL Queries**: Resolved duplicate dictionary keys and formatting
- **CLI Templates**: Fixed import paths and parameter names in scaffolded projects

## [0.3.1] - 2025-01-06

### Added
- Initial release of the Future framework
- Basic ASGI application structure
- Core routing and middleware systems
- GraphQL support with Strawberry
- WebSocket support
- CLI tool for project management

### Changed
- Complete architectural overhaul
- Removed all decorators for minimal design
- Implemented static method patterns
- Centralized configuration management

### Removed
- Legacy database integration
- Complex dependency chains
- Decorator-based patterns
- Boilerplate files

## [0.3.0] - 2025-01-06

### Added
- Foundation of the Future framework
- Basic routing system
- Middleware infrastructure
- Type safety throughout

## [0.2.0] - 2025-01-06

### Added
- Initial project structure
- Core ASGI application
- Basic routing capabilities

## [0.1.0] - 2025-01-06

### Added
- Project initialization
- Basic framework structure
- Development environment setup

---

## Versioning

This project uses [Semantic Versioning](https://semver.org/) for version numbers.

### Version Increment Rules:
- **Patch releases** (0.3.1 → 0.3.2): Bug fixes and minor improvements
- **Minor releases** (0.3.1 → 0.4.0): New features, backward compatible
- **Major releases** (0.3.1 → 1.0.0): Breaking changes

### GitHub Workflows
All releases and publishing are handled automatically by GitHub workflows:
- **CI**: Runs on every push/PR (linting, type checking, tests, building)
- **Publish**: Automatically publishes to PyPI when tags are pushed
- **Versioning**: Uses `poetry-dynamic-versioning` for automatic version management

The version is automatically incremented based on git commit messages:
- `feat:` → minor version bump
- `BREAKING CHANGE:` → major version bump
- Default → patch version bump
