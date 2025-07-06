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

# Get the logger and apply colored formatter
logger = logging.getLogger("future")
if hasattr(logger, "handlers") and logger.handlers:
    for handler in logger.handlers:
        handler.setFormatter(ColoredFormatter("%(message)s"))

# Start queue handler if it exists
queue_handler = logging.getHandlerByName("queue_handler")
if queue_handler is not None:
    # Type check for QueueHandler which has listener attribute
    if isinstance(queue_handler, logging.handlers.QueueHandler):
        listener = getattr(queue_handler, "listener", None)
        if listener is not None:
            listener.start()
            atexit.register(listener.stop)

# Create logger instance
log = logging.getLogger("future")
