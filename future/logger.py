import logging
import logging.config
import logging.handlers
import atexit

_valid_log_levels = logging.getLevelNamesMapping()

_LOGGER_DICT_CONF = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "kv_log": {
            "format": "%(asctime)s log_level=%(levelname)s filename=%(filename)s name=%(name)s msg=%(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "kv_log",
            "stream": "ext://sys.stdout",
        },
        # "file_kv": {
        #     "class": "logging.handlers.RotatingFileHandler",
        #     "level": "INFO",
        #     "formatter": "kv_log",
        #     "filename": f"logs/web-api.log",
        #     "maxBytes": 10000000,
        #     "backupCount": 3
        # },
        "queue_handler": {
            "class": "logging.handlers.QueueHandler",
            "handlers": [
                "stdout",
                # "file_kv"
            ],
            "respect_handler_level": True,
        },
    },
    "loggers": {
        "future": {
            "level": "INFO",
            "handlers": [
                "queue_handler",
            ],
        }
    },
}


def setup_logging():
    logging.config.dictConfig(_LOGGER_DICT_CONF)
    queue_handler = logging.getHandlerByName("queue_handler")

    if queue_handler is not None:
        # queue_handler.listener: logging.handlers.QueueListener
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


# def change_handlers_log_level(log_level: str):
#
#     # TODO: make dynamic?
#     if log_level not in _valid_log_levels:
#         raise Exception(f"Invalid log level {log_level=}")
#
#     file_kv_handler = logging.getHandlerByName("file_kv")
#     stdout_handler = logging.getHandlerByName("stdout")
#     stdout_handler.setLevel(log_level)
#     file_kv_handler.setLevel(log_level)
