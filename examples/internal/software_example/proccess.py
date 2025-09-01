import asyncio
import os
from pathlib import Path
import random
import traceback

from wtelethon import (
    TelegramClient,
    JsonAttachment,
    MemoryAttachment,
    tl_functions,
    utils,
    helpers,
    storages,
)

from config import dead_dir_path


async def client_proccess(client: "TelegramClient"):
    print(
        "Подключаемся к {} с прокси {}:{}".format(
            client.memory.session_file,
            client.current_proxy.host,
            client.current_proxy.port,
        )
    )

    await client.connect()
    await client.check_authorization()


async def _proccess():
    client: "TelegramClient" = storages.client_holds_storage.get_free_client()
    if client is None:
        print("Нет свободных клиентов")
        return

    try:
        client.set_proxy_from_storage()

    except:
        print("Нет доступных прокси")
        return

    try:
        await client_proccess(client)

    except Exception as exc:
        await client.disconnect()

        if utils.is_dead_error(exc):
            print(
                f"Клиент {client.memory.session_file} мертв ({client.memory.dead_error})"
            )

        elif utils.is_connection_error(exc):
            print(f"Клиент {client.memory.session_file} с ошибкой подключения")

        else:
            raise exc


async def run_software():
    while True:
        
        await _proccess()
        await asyncio.sleep(1)
