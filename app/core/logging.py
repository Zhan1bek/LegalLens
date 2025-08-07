from loguru import logger
import sys

logger.remove()
logger.add(
    sys.stdout,
    level="INFO",
    serialize=True,
    backtrace=True,
    diagnose=True,
)
