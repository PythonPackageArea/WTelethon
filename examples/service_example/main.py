import asyncio

from wtelethon import helpers, storages, utils

from api_mock import ApiMock
from logging_config import setup_service_logging, get_logger
from proccess import run_service
from proxy_loader import load_proxies

setup_service_logging()
helpers.logging.set_telethon_logging("off")

api_mock = ApiMock()
logger = get_logger(__name__)


async def main() -> None:
    """Запуск сервиса"""
    logger.info("Запуск сервиса WTelethon")

    try:

        logger.debug("Загрузка прокси из API")
        await helpers.tasks.run_fetch_task(load_proxies)
        logger.info("Прокси успешно загружены")

        logger.info("Запуск основного цикла сервиса")
        await run_service()
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске сервиса: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
