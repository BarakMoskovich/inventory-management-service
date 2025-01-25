import logging
from typing import Any

class LoggerService:
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    @staticmethod
    def info(logger: logging.Logger, message: str) -> None:
        logger.info(message)

    @staticmethod
    def error(logger: logging.Logger, message: str) -> None:
        logger.error(message)

    @staticmethod
    def warning(logger: logging.Logger, message: str) -> None:
        logger.warning(message)

    @staticmethod
    def debug(logger: logging.Logger, message: str) -> None:
        logger.debug(message)

    @staticmethod
    def exception(logger: logging.Logger, message: str) -> None:
        logger.exception(message)

    @staticmethod
    def get_log_level(level: str) -> int:
        return getattr(logging, level.upper())