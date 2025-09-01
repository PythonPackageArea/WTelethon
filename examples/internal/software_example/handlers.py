import asyncio
import contextlib
import os
from pathlib import Path
import random
import traceback

from telethon.tl import TLRequest
from typing import Union, Callable, Awaitable
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

from config import dead_dir_path


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

    with contextlib.suppress(Exception):
        client.disconnect()
        client.remove_from_storage_hold()
        await client.move_files(dead_dir_path)

    raise exception
