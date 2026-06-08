import json
import logging
import os
import uuid
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", "none"),
            "trace_id": getattr(record, "trace_id", "none"),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def _build_logger() -> logging.Logger:
    os.makedirs("logs", exist_ok=True)

    log = logging.getLogger("cart_api")
    log.setLevel(logging.INFO)

    if log.handlers:
        return log

    json_formatter = JSONFormatter()

    # stdout handler — captured by Docker / CloudWatch Agent
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(json_formatter)
    log.addHandler(stream_handler)

    # file handler — for local dev and CloudWatch Agent file tail
    file_handler = logging.FileHandler("logs/app.log")
    file_handler.setFormatter(json_formatter)
    log.addHandler(file_handler)

    return log


logger = _build_logger()


def get_correlation_id() -> str:
    return str(uuid.uuid4())
