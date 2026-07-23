# Configuration
Scaffolded apps load settings in `app/config/Settings.py` and build the connection map in `app/config/Database.py`. Pass `DATABASES` into `Future(config=...)` in `run.py`.

## Option A — `.env` + python-dotenv (scaffold default)
`future init` creates `.env.example`. Copy it and edit:

```bash
cp .env.example .env
```

```env
APP_NAME=Future
APP_DOMAIN=
APP_HOST=127.0.0.1
APP_PORT=8000
APP_DEBUG=True
APP_WORKERS=1
DB_DATABASE=database
```

`app/config/Settings.py` (generated):

```python
from os import environ as env
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

APP_NAME = str(env.get("APP_NAME", "Future"))
APP_DEBUG = env.get("APP_DEBUG", "False").lower() == "true"
APP_HOST = str(env.get("APP_HOST", "127.0.0.1"))
APP_PORT = int(env.get("APP_PORT", 8000))
APP_WORKERS = int(env.get("APP_WORKERS", 1))
APP_DOMAIN = str(env.get("APP_DOMAIN", ""))

DB_DATABASE = str(env.get("DB_DATABASE", "database"))
```

SQLite opens `{DB_DATABASE}.sqlite` (e.g. `database` → `database.sqlite`).

## Option B — YAML + Ansible Vault
Same idea: load a file once in `Settings.py`, export module-level constants. Useful when secrets are vault-encrypted:

```yaml
# environment.yml
app_name: "myapp"
app_domain: "example.com"
app_host: "127.0.0.1"
app_port: 5000
app_workers: 1
app_debug: true
sqlite_database: "myapp"
# secret_token: !vault |
#   $ANSIBLE_VAULT;1.1;AES256
#   ...
```

```python
# app/config/Settings.py — sketch
from ansible.parsing.dataloader import DataLoader
from ansible.parsing.vault import VaultSecret, VaultSecretsContext
from ansible.module_utils.common.text.converters import to_bytes
from ansible.constants import DEFAULT_VAULT_ID_MATCH

def load_environment_config(path: str) -> dict:
    vault_pass = "..."  # or getpass()
    loader = DataLoader()
    secrets = [(DEFAULT_VAULT_ID_MATCH, VaultSecret(to_bytes(vault_pass)))]
    loader.set_vault_secrets(vault_secrets=secrets)
    VaultSecretsContext.initialize(VaultSecretsContext(secrets))
    data = loader.load_from_file(file_name=path)
    return {key: value if isinstance(value, (bool, int)) else str(value) for key, value in data.items()}

config = load_environment_config("./environment.yml")
APP_NAME = str(config["app_name"])
APP_DOMAIN = str(config["app_domain"])
APP_HOST = str(config["app_host"])
APP_PORT = int(config["app_port"])
APP_DEBUG = config["app_debug"]
APP_WORKERS = int(config["app_workers"])
SQLITE_DATABASE = str(config["sqlite_database"])
```

Encrypt a string into the file:

```bash
ansible-vault encrypt_string 'mytoken' --name 'secret_token' --ask-vault-pass >> environment.yml
```

Pick **one** loader for the app (dotenv **or** YAML). Controllers and `Database.py` only import the constants.

## Database map
`app/config/Database.py` is data only — no `Connections` call at import:

```python
from future.databases.SQLite import SQLite
from app.config.Settings import DB_DATABASE

DATABASES = {
    "default": "sqlite",
    "sqlite": SQLite(database=DB_DATABASE),
}
```

Multi-driver example (same pattern — values from Settings):

```python
from future.databases.SQLite import SQLite
from future.databases.MySQL import MySQL
from future.databases.Postgres import Postgres
# ...
DATABASES = {
    "default": "sqlite",
    "sqlite": SQLite(database=SQLITE_DATABASE),
    "mysql": MySQL(host=MYSQL_HOST, port=MYSQL_PORT, username=MYSQL_USERNAME, password=MYSQL_PASSWORD, database=MYSQL_DATABASE),
    "postgres": Postgres(host=POSTGRES_HOST, port=POSTGRES_PORT, username=POSTGRES_USERNAME, password=POSTGRES_PASSWORD, database=POSTGRES_DATABASE),
}
```

Wire it in `run.py`:

```python
config = {
    "APP_DOMAIN": APP_DOMAIN,
    "APP_NAME": APP_NAME,
    "DATABASES": DATABASES,
}
app = Future(lifespan=lifespan, config=config)
```

## Config keys the core uses
| Key | Role |
|-----|------|
| `APP_DOMAIN` | Host/subdomain routing; `""` = domainless |
| `APP_NAME` | Banner / OpenAPI title fallback |
| `APP_DEBUG` | Uvicorn reload; log level |
| `DATABASES` | Connection registry at boot |
| `OPENAPI` | Docs enablement and UIs |
| `GRAPHQL_SCHEMA` | Optional Strawberry schema for `GraphQLController` |
| `APP_ASGI` | Import string for reload / multi-worker (default `run:app`) |
