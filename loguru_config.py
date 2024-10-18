from loguru import logger
import sys


def configure_loguru(level: str):
    """
    level - "DEBUG" , "INFO", "ERROR"
    """
    logger.remove()  # Удаляем все предыдущие обработчики
    logger.add(
        sys.stdout,
        format="<level>{level}</level> | <cyan>{file}</cyan>:<yellow>{function}</yellow>:<green>{line}</green> | <magenta>{time:HH:mm:ss}</magenta> | <level>{message}</level>",
        level=level,
    )
