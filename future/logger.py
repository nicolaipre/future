import atexit
import logging
import logging.config
import logging.handlers

from future.settings import LOGGING_CONFIG


# ANSI color codes
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors like uvicorn"""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            # Calculate padding based on original levelname length BEFORE adding colors
            padding = " " * (9 - len(levelname))  # 9 is max level length (CRITICAL) + 1
            colored_levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
            return f"{colored_levelname}:{padding}{record.getMessage()}"
        return super().format(record)


# Configure logging using settings
logging.config.dictConfig(LOGGING_CONFIG)

log = logging.getLogger("future")
formatter = ColoredFormatter("%(message)s")

# QueueHandler itself does not format; the listener's stdout handler does.
# Handler level NOTSET so Future's log.setLevel(APP_DEBUG) alone controls filtering.
queue_handler = logging.getHandlerByName("queue_handler")
if queue_handler is not None and isinstance(queue_handler, logging.handlers.QueueHandler):
    listener = getattr(queue_handler, "listener", None)
    if listener is not None:
        for handler in listener.handlers:
            handler.setFormatter(formatter)
            handler.setLevel(logging.NOTSET)
        listener.start()
        atexit.register(listener.stop)
else:
    for handler in log.handlers:
        handler.setFormatter(formatter)
        handler.setLevel(logging.NOTSET)
