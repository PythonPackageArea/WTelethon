import asyncio
from typing import Optional

from wtelethon import TelegramClient, storages, utils

from config import DEAD_DIR_PATH, SLEEP_INTERVAL
from logging_config import get_logger

logger = get_logger(__name__)


async def client_process(client: TelegramClient) -> None:
    """Основной процесс работы с клиентом"""
    session_name = client.memory.session_file
    logger.info(f"Работа с аккаунтом: {session_name}")

    logger.info(
        f"Попытка подключиться к {session_name} с прокси {client.current_proxy.host}:{client.current_proxy.port}"
    )

    await client.connect()
    logger.info(f"Аккаунт {session_name} подключен")

    await client.check_authorization()
    logger.info(f"Аккаунт {session_name} авторизован")

    await client.disconnect()
    logger.info(f"Аккаунт {session_name} отключен")


async def _process() -> None:
    """Внутренний процесс обработки одного клиента"""
    client: Optional[TelegramClient] = storages.client_holds_storage.get_free_client()
    if client is None:
        logger.warning("Нет свободных аккаунтов для работы")
        return

    session_name = client.memory.session_file

    try:
        client.set_proxy_from_storage()
    except Exception as e:
        logger.warning(f"Не удалось найти прокси для {session_name}")
        return

    try:
        await client_process(client)
        client.remove_from_storage_hold()

    except Exception as exc:
        await client.disconnect()

        if utils.is_dead_error(exc):
            logger.error(f"Аккаунт {session_name} больше не работает")
            logger.info(f"Перемещаю {session_name} в папку 'dead'")
            client.remove_from_storage_hold()

            await client.move_files(DEAD_DIR_PATH)

        elif utils.is_connection_error(exc):
            logger.warning(f"Проблемы с сетью у {session_name}, попробуем позже")
        else:
            client.remove_from_storage_hold()
            logger.error(f"Неожиданная ошибка с {session_name}: {exc}")
            raise exc


async def run_software() -> None:
    """Запуск основного цикла программы"""
    logger.info("Начали работу с вашими аккаунтами!")
    logger.info(
        "Программа будет работать до тех пор, пока не закончатся аккаунты. Нажмите Ctrl+C для остановки"
    )

    try:
        while storages.client_holds_storage._holds:
            await _process()
            await asyncio.sleep(SLEEP_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Остановка программы...")
        logger.info("Программа остановлена. Спасибо за использование!")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        logger.error("Проверьте настройки и попробуйте снова")
