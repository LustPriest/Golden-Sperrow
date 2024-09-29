import sys
import picologging as logging
import structlog

structlog.configure(
    cache_logger_on_first_use=True,
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="%d-%m-%Y %H:%M.%S", utc=False),
        structlog.dev.ConsoleRenderer(),
    ],
)

logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

logger = structlog.wrap_logger(logging.getLogger("Golden Sperrow"))
