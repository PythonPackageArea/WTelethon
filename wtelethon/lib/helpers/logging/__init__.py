import logging
import sys
from typing import Optional


def set_telethon_log_level(level: int | str) -> None:
    """Устанавливает уровень логирования для Telethon.

    Args:
        level: Уровень логирования. Может быть числом (10-50) или строкой
               (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Example:
        >>> # Установить детальное логирование
        >>> set_telethon_log_level("DEBUG")
        >>>
        >>> # Установить только ошибки
        >>> set_telethon_log_level(40)
    """
    logger = logging.getLogger("telethon")
    logger.disabled = False
    logger.setLevel(level)


def set_telethon_logging(
    mode: str = "simple", previous_handler: Optional[logging.Handler] = None
) -> Optional[logging.Handler]:
    """Настраивает режим логирования для Telethon.

    Args:
        mode: Режим логирования. Варианты:
              - "off": отключить логирование
              - "simple": простое логирование (INFO уровень)
              - "verbose": подробное логирование (DEBUG уровень)
        previous_handler: Предыдущий обработчик для удаления.

    Returns:
        Созданный обработчик или None если логирование отключено.

    Example:
        >>> # Включить простое логирование
        >>> handler = set_telethon_logging("simple")
        >>>
        >>> # Переключиться на подробное
        >>> handler = set_telethon_logging("verbose", handler)
        >>>
        >>> # Отключить логирование
        >>> set_telethon_logging("off", handler)
    """
    logger = logging.getLogger("telethon")

    if mode == "off":
        logger.disabled = True
        logger.setLevel(logging.CRITICAL + 1)
        for child_name in list(logging.Logger.manager.loggerDict.keys()):
            if child_name.startswith("telethon."):
                child_logger = logging.getLogger(child_name)
                child_logger.disabled = True
                child_logger.setLevel(logging.CRITICAL + 1)

        if previous_handler and previous_handler in logger.handlers:
            logger.removeHandler(previous_handler)
        return None

    logger.disabled = False
    logger.setLevel(logging.DEBUG)
    for child_name in list(logging.Logger.manager.loggerDict.keys()):
        if child_name.startswith("telethon."):
            child_logger = logging.getLogger(child_name)
            child_logger.disabled = False

    if previous_handler and previous_handler in logger.handlers:
        logger.removeHandler(previous_handler)

    handler = logging.StreamHandler(sys.stdout)
    if mode == "verbose":
        fmt = "%(asctime)s %(name)s [%(levelname)s] %(message)s"
        level = logging.DEBUG
    else:
        fmt = "%(levelname)s: %(message)s"
        level = logging.INFO

    handler.setFormatter(logging.Formatter(fmt))
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False

    return handler
