import logging
from contextvars import ContextVar

from app.core.config import LOG_LEVEL

request_id_context: ContextVar[str] = ContextVar("request_id", default="-")
_configured = False


def configure_logging() -> None:
    global _configured

    if _configured:
        return

    log_level = getattr(logging, LOG_LEVEL, logging.INFO)

    previous_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = previous_factory(*args, **kwargs)
        record.request_id = request_id_context.get()
        return record

    logging.setLogRecordFactory(record_factory)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s [%(name)s] [req=%(request_id)s] %(message)s",
    )
    _configured = True


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
