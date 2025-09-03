import asyncio
import sys

from wtelethon import helpers, storages, utils

from config import ALIVE_DIR_PATH, PROXIES_FILE_PATH, PROXY_TYPE
from handlers import connect_error_handler
from loader import load_clients
from logging_config import setup_user_logging, get_logger
from proccess import run_software

setup_user_logging()
helpers.logging.set_telethon_logging("off")

logger = get_logger(__name__)


async def main() -> None:
    """Запуск программы"""
    logger.info("Добро пожаловать в Software Example!")

    # Загрузка прокси
    logger.info("Загрузка прокси...")
    try:
        await helpers.storages.proxies.load_proxies_from_file(
            PROXIES_FILE_PATH,
            PROXY_TYPE,
        )
    except Exception as e:
        logger.error(f"Не удалось загрузить прокси: {e}")
        logger.error("Проверьте файл с прокси и попробуйте снова")
        sys.exit(1)

    proxy_count = len(storages.proxy_storage._proxies)
    logger.info(f"Прокси загружены: {proxy_count} шт.")

    # Загрузка клиентов
    logger.info("Поиск сессий для загрузки...")
    clients = await load_clients(ALIVE_DIR_PATH)

    if not clients:
        logger.error("Не найдено ни одной сессии")
        logger.error(f"Поместите .session файлы в папку {ALIVE_DIR_PATH}")
        sys.exit(1)

    logger.info(f"Клиенты готовы: {len(clients)} шт.")

    # Настройка клиентов
    for client in clients:
        client.add_exception_handler(utils.is_connection_error, connect_error_handler)
        storages.client_holds_storage.add_client(client)

    logger.info("Запуск работы с клиентами...")
    await run_software()


if __name__ == "__main__":
    asyncio.run(main())
