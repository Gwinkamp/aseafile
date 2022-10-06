import sys
import logging
import aiologger
from aiologger.handlers.streams import AsyncStreamHandler
from typing import TextIO
from aseafile.constants import (
    LOGGING_MESSAGE_FORMAT,
    LOGGING_DATE_FORMAT,
    LOGGING_MESSAGE_STYLE
)

DEFAULT_FORMATTER = logging.Formatter(
    fmt=LOGGING_MESSAGE_FORMAT,
    datefmt=LOGGING_DATE_FORMAT,
    style=LOGGING_MESSAGE_STYLE)


class LoggerFactory:

    @staticmethod
    def create_default_logger(
            name: str,
            stream: TextIO = sys.stdout,
            level: int = logging.INFO,
            formatter: logging.Formatter = DEFAULT_FORMATTER) -> aiologger.Logger:
        handler = AsyncStreamHandler(stream, formatter=formatter, level=level)
        logger = aiologger.Logger(name=name)
        logger.add_handler(handler)
        return logger
