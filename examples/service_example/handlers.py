import contextlib
from typing import Union, Awaitable

from telethon.tl import TLRequest

from wtelethon import TelegramClient

from api_mock import ApiMock
from logging_config import get_logger

api_mock = ApiMock()
logger = get_logger(__name__)


async def connect_error_handler(
    client: TelegramClient,
    request: Union[TLRequest, Awaitable],
    exception: ConnectionError,
) -> Union[TLRequest, Awaitable]:
    """Обработчик ошибок подключения с заменой прокси"""
    session_name = client.memory.session_file
    old_proxy = f"{client.current_proxy.host}:{client.current_proxy.port}"

    logger.warning(
        f"Ошибка подключения для {session_name} через {old_proxy}: {exception}"
    )

    with contextlib.suppress(Exception):
        client.proxy_error()
        client.set_proxy_from_storage()

        new_proxy = f"{client.current_proxy.host}:{client.current_proxy.port}"
        logger.info(f"Смена прокси для {session_name}: {old_proxy} -> {new_proxy}")

        await api_mock.update_proxy_data(
            client.current_proxy.source,
            connect_error=True,
        )

        logger.debug(f"Переподключение {session_name} через новый прокси")
        await client.disconnect()
        await client.connect()

        logger.info(f"Клиент {session_name} успешно переподключен")
        return request

    logger.error(f"Не удалось обработать ошибку подключения для {session_name}")
    raise exception
