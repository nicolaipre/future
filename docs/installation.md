# Installation

## Prerequisites

- Python 3.12 or higher
- Poetry (recommended) or pip

## Installation Methods

### Using Poetry (Recommended)

```bash
# Install Future with Poetry
poetry add future-api

# Or add to existing project
poetry add future-api
```

### Using pip

```bash
# Install from PyPI
pip install future-api
```

### From Source

```bash
# Clone the repository
git clone https://github.com/Defendinary/future.git
cd future

# Install in development mode
poetry install
```

## Verify Installation

```bash
# Check if Future is installed
python -c "import future; print('Future installed successfully!')"

# Check CLI tool
future --help
```

## Next Steps

After installation, you can:

1. [Create a new project](usage.md#basic-application-setup)
2. [Learn about routing](usage.md#routing)
3. [Understand middleware](usage.md#middleware)
4. [Explore WebSocket support](usage.md#websocket-support)
5. [Check out examples](examples.md) 