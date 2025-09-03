import contextlib
from typing import Union, Awaitable

from telethon.tl import TLRequest

from wtelethon import TelegramClient

from logging_config import get_logger

logger = get_logger(__name__)


async def connect_error_handler(
    client: TelegramClient,
    request: TLRequest,
    exception: ConnectionError,
) -> Union[TLRequest, Awaitable]:
    """Обработчик ошибок подключения с заменой прокси"""
    session_name = client.memory.session_file

    logger.warning(f"Проблемы с интернетом у {session_name}, меняю прокси...")

    with contextlib.suppress(Exception):
        client.proxy_error()
        client.set_proxy_from_storage()

        logger.info(f"Новый прокси установлен для {session_name}")

        await client.disconnect()
        await client.connect()

        logger.info(f"Аккаунт {session_name} переподключен успешно")
        return request

    logger.warning(f"Не удалось переподключить {session_name}")
    raise exception
