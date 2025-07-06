from os import environ as env

from dotenv import load_dotenv


load_dotenv(dotenv_path=".env")  # FIXME: dotenv not used correctly. Shouldn't need both os.environ and dotenv...
# os.environ["APP_ENV"] = "dev"
# port = int(os.environ.get("APP_PORT", 44777))


# Application settings sourced from .env
APP_NAME = str(env.get("APP_NAME", "Future"))
APP_VERSION = str(env.get("APP_VERSION", "1.0"))
APP_DESCRIPTION = str(env.get("APP_DESCRIPTION", "A short description"))
APP_DEBUG = bool(env.get("APP_DEBUG", True))
APP_LOG_LEVEL = str("DEBUG" if APP_DEBUG else env.get("APP_LOG_LEVEL", "INFO"))
APP_ACCESS_LOG = bool(env.get("APP_ACCESS_LOG", False))
APP_WORKERS = int(env.get("APP_WORKERS", 4))
APP_HOST = str(env.get("APP_HOST", "127.0.0.1"))
APP_PORT = int(env.get("APP_PORT", 9000))
APP_SSO = bool(env.get("APP_SSO", False))
APP_KEY = str(env.get("APP_KEY", "secret"))  # os.urandom(24)  # TODO: add to cli --generate
APP_REGISTRATION = bool(env.get("APP_REGISTRATION", False))
APP_SSL_CERT_FILE = str(env.get("APP_SSL_CERT_FILE", "./cert.pem"))
APP_SSL_KEY_FILE = str(env.get("APP_SSL_KEY_FILE", "./key.pem"))
APP_SSL_PASSPHRASE = str(env.get("APP_SSL_PASSPHRASE", "changeme"))
APP_DOMAIN = str(env.get("APP_DOMAIN", "example.com"))

# Database settings sourced from .env
DB_DRIVER = str(env.get("DB_DRIVER", "sqlite"))
DB_HOST = str(env.get("DB_HOST", "127.0.0.1"))
DB_PORT = int(env.get("DB_PORT", 3306))
DB_DATABASE = str(env.get("DB_DATABASE", None))
DB_USERNAME = str(env.get("DB_USERNAME", None))
DB_PASSWORD = str(env.get("DB_PASSWORD", None))
DB_LOGGING = str(env.get("DB_LOGGING", True))
DB_OPTIONS = str(env.get("DB_OPTIONS", None))

# Elasticsearch settings sourced from .env
ELASTIC_HOST = str(env.get("ELASTIC_HOST", "127.0.0.1"))
ELASTIC_PORT = int(env.get("ELASTIC_PORT", 9200))
ELASTIC_USER = str(env.get("ELASTIC_USER", None))
ELASTIC_PASS = str(env.get("ELASTIC_PASS", None))

# API Spec generated based on settings
API_SPEC = {
    "openapi": "3.0.0",  # Updated to 3.0.0 for better compatibility
    "info": {
        "title": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
    },
    "paths": {},
    # "servers": [
    #    {
    #        "url": APP_DOMAIN,
    #         "description": "Development server"
    #     }
    # ]
}

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {
            "format": "%(message)s",
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "level": APP_LOG_LEVEL,
            "formatter": "colored",
            "stream": "ext://sys.stdout",
        },
        "queue_handler": {
            "class": "logging.handlers.QueueHandler",
            "handlers": [
                "stdout",
            ],
            "respect_handler_level": True,
        },
    },
    "loggers": {
        "future": {
            "level": APP_LOG_LEVEL,
            "handlers": ["queue_handler"],
        }
    },
}
