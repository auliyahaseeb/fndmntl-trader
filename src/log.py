import logging
import json
import sys
from datetime import datetime, timezone

STANDARD_LOG_RECORD_FIELDS = frozenset(logging.makeLogRecord({}).__dict__)

class JSONFormatter(logging.Formatter):
    """
    Custom formatter to enforce native structured JSON logging.
    Overrides the standard string formatting to emit machine-readable telemetry.
    """
    def format(self, record: logging.LogRecord) -> str:
        # ISO 8601 timestamp format ensures lexicographic sorting equates to chronological sorting
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "funcName": record.funcName,
            "message": record.getMessage()
        }
        
        # Merge any dimensional data passed through logging's extra= argument.
        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in STANDARD_LOG_RECORD_FIELDS
        }
        if extras:
            log_record["extra"] = extras
            
        # Capture full stack traces for unhandled exceptions
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)

def get_logger(name: str) -> logging.Logger:
    """
    Instantiates and configures a module-level logger bound to stdout.
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers if get_logger is called multiple times
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.propagate = False
        
    return logger
