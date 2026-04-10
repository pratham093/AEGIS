"""Logging setup — console + rotating JSON log file."""

import logging
import logging.handlers
import json
from pathlib import Path
from datetime import datetime, timezone

# logs live one level up from the aegis package
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "aegis.log"


class JSONFormatter(logging.Formatter):
    """formats each log record as a single json object for machine parsing."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            entry["exception"] = self.formatException(record.exc_info)

        # pull domain-specific fields that callers attach via `extra={}`
        for key in ("asset", "signal", "exposure", "regime", "risk_score",
                     "price", "error", "duration_s", "rows", "endpoint"):
            val = getattr(record, key, None)
            if val is not None:
                entry[key] = val
        return json.dumps(entry)


def get_logger(name: str) -> logging.Logger:
    """returns a logger with console + rotating file handlers, creating them once."""
    logger = logging.getLogger(name)

    # avoid stacking duplicate handlers if called more than once
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # console: human-readable, info-level only to keep terminal clean
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        "%(asctime)s  %(levelname)-7s  %(name)s  %(message)s",
        datefmt="%H:%M:%S",
    ))
    logger.addHandler(console)

    # file: structured json at debug level, rotates at 5 MB to cap disk use
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)

    # don't bubble up to root logger and double-print
    logger.propagate = False
    return logger
