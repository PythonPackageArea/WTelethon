import logging
import sys
from typing import Any


class UserFriendlyFormatter(logging.Formatter):
    """Форматтер для пользовательских логов"""

    LEVEL_COLORS = {
        "INFO": "\033[92m",  # Зеленый
        "WARNING": "\033[93m",  # Желтый
        "ERROR": "\033[91m",  # Красный
        "DEBUG": "\033[94m",  # Синий
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        # Простой формат для пользователя
        color = self.LEVEL_COLORS.get(record.levelname, "")
        reset = self.RESET

        if record.levelname == "INFO":
            return f"{color}✓{reset} {record.getMessage()}"
        elif record.levelname == "WARNING":
            return f"{color}⚠{reset} {record.getMessage()}"
        elif record.levelname == "ERROR":
            return f"{color}✗{reset} {record.getMessage()}"
        else:
            return f"{color}•{reset} {record.getMessage()}"


def setup_user_logging() -> None:
    """Настройка пользовательского логирования"""
    # Создаем пользовательский форматтер
    formatter = UserFriendlyFormatter()

    # Настраиваем консольный хендлер
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Настраиваем root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)

    # Отключаем логи телеграм клиента и других библиотек
    logging.getLogger("telethon").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)


def get_logger(name: str) -> logging.Logger:
    """Получить логгер для модуля"""
    return logging.getLogger(name)
