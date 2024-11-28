from os import environ as env
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

# Application settings sourced from .env
APP_NAME            =  str(env.get("APP_NAME", "Future"))
APP_VERSION         =  str(env.get("APP_VERSION", "1.0"))
APP_DESCRIPTION     =  str(env.get("APP_DESCRIPTION", "A short description"))
APP_DEBUG           = eval(env.get("APP_DEBUG", False))
APP_ACCESS_LOG      = eval(env.get("APP_ACCESS_LOG", False))
APP_WORKERS         =  int(env.get("APP_WORKERS", 4))
APP_DOMAIN          =  str(env.get("APP_DOMAIN", "example.com")).replace("http://", "").replace("https://", "")
APP_HOST            =  str(env.get("APP_HOST", "127.0.0.1"))
APP_PORT            =  int(env.get("APP_PORT", 8000))
APP_SSO             = eval(env.get("APP_SSO", False))
APP_KEY             =  str(env.get("APP_KEY", None))
APP_REGISTRATION    = eval(env.get("APP_REGISTRATION", False))
APP_SSL_CERT_FILE   =  str(env.get("APP_SSL_CERT_FILE", "./cert.pem"))
APP_SSL_KEY_FILE    =  str(env.get("APP_SSL_KEY_FILE", "./key.pem"))
APP_SSL_PASSPHRASE  =  str(env.get("APP_SSL_PASSPHRASE", "password"))

# Database settings sourced from .env
DB_DRIVER           =  str(env.get("DB_DRIVER", "sqlite"))
DB_HOST             =  str(env.get("DB_HOST", "127.0.0.1"))
DB_PORT             =  int(env.get("DB_PORT", 3306))
DB_DATABASE         =  str(env.get("DB_DATABASE", None))
DB_USERNAME         =  str(env.get("DB_USERNAME", None))
DB_PASSWORD         =  str(env.get("DB_PASSWORD", None))
DB_LOGGING          =  str(env.get("DB_LOGGING", True))
DB_OPTIONS          =  str(env.get("DB_OPTIONS", None))

# Elasticsearch settings sourced from .env
ELASTIC_HOST        =  str(env.get("ELASTIC_HOST", "127.0.0.1"))
ELASTIC_PORT        =  int(env.get("ELASTIC_PORT", 9200))
ELASTIC_USER        =  str(env.get("ELASTIC_USER", None))
ELASTIC_PASS        =  str(env.get("ELASTIC_PASS", None))

# API Spec generated based on settings
API_SPEC = {
    "openapi": "1.0.0",
    "info": {
        "title": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
    }
}
