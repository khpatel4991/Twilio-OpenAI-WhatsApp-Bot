import logging
import os

logger = logging.getLogger("logtest")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    fmt="%(asctime)s pid/%(process)d [%(filename)s:%(lineno)d] %(message)s"
)

# Console handler (always available in serverless environments)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler (only if logs directory exists, e.g., not in Vercel)
if os.path.exists("./logs"):
    try:
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(
            "./logs/logtest.log", maxBytes=1024 * 1024, backupCount=10
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")
else:
    logger.info("Logs directory not found; using console logging only.")
