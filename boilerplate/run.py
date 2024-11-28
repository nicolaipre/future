#!/usr/bin/env python3
from future.application import Future
from app.config.environment import (
    APP_NAME,
    APP_DEBUG,
    APP_HOST,
    APP_PORT,
    APP_DEBUG,
    APP_DOMAIN,
    APP_ACCESS_LOG,
    APP_WORKERS,
    APP_SSL_CERT_FILE,
    APP_SSL_KEY_FILE,
    APP_SSL_PASSPHRASE
)
from app.routes import ROUTES

app = Future(
    name=APP_NAME,
    domain=APP_DOMAIN,
    debug=APP_DEBUG,
)
app.add_routes(routes=ROUTES)
#print([x.prefix for x in ROUTES])

if __name__ == '__main__':
    app.run(
        host=APP_HOST,
        port=APP_PORT,
        workers=APP_WORKERS
    )
