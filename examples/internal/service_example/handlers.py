import asyncio
import contextlib
import os
from pathlib import Path
import random
import traceback

from telethon.tl import TLRequest
from typing import Union, Callable, Awaitable
from api_mock import ApiMock
from wtelethon import (
    TelegramClient,
    JsonAttachment,
    MemoryAttachment,
    tl_functions,
    tl_types,
    utils,
    helpers,
    storages,
)

api_mock = ApiMock()


async def connect_error_handler(
    client: TelegramClient,
    request: Union[TLRequest, Awaitable],
    exception: ConnectionError,
):

    try:

        client.proxy_error()
        client.set_proxy_from_storage()
        print(
            "Замена прокси в {} на: {}:{}".format(
                client.memory.session_file,
                client.current_proxy.host,
                client.current_proxy.port,
            )
        )
        return

    except:
        pass

    raise exception


async def dead_error_handler(
    client: TelegramClient,
    request: Union[TLRequest, Awaitable],
    exception: ConnectionError,
):

    await client.check_authorization()

    with contextlib.suppress(Exception):
        client.disconnect()
        api_mock.update_session_data(client.memory.slug, dead=True)

    raise exception
