"""Module with execution time decorator."""
import logging
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)


def log_execution_time(func: Callable) -> Callable:
    """This decorator prints the execution time for the decorated function."""

    def wrapper(*args, **kwargs) -> Any:
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info(f"{func.__name__} ran in {round(end - start, 4)}s")
        return result

    return wrapper
