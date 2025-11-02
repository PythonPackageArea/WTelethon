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

    logger.warning(f"Internet problems with {session_name}, changing proxy...")

    with contextlib.suppress(Exception):
        client.proxy_error()
        client.set_proxy_from_storage()

        logger.info(f"New proxy set for {session_name}")

        await client.disconnect()
        await client.connect()

        logger.info(f"Account {session_name} reconnected successfully")
        return request

    logger.warning(f"Failed to reconnect {session_name}")
    raise exception
