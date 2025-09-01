import asyncio
import os
from pathlib import Path
import random
import traceback

from wtelethon import (
    TelegramClient,
    utils,
    helpers,
    storages,
    MemoryAttachment,
)

from api_mock import ApiMock
from handlers import connect_error_handler, dead_error_handler

api_mock = ApiMock()


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


async def get_client():
    session_data = api_mock.get_session_data()
    if session_data is None:
        print("Нет данных для клиента")
        return

    client = TelegramClient(
        session_data.string_session,
        memory_attachment=MemoryAttachment(
            api_id=session_data.api_id,
            api_hash=session_data.api_hash,
            device_model=session_data.device_model,
            system_version=session_data.system_version,
            app_version=session_data.app_version,
            lang_code=session_data.lang_code,
            system_lang_code=session_data.system_lang_code,
            layer=session_data.layer,
            slug=session_data.slug,
        ),
    )

    client.add_exception_handler(utils.is_connection_error, connect_error_handler)
    client.add_exception_handler(utils.is_dead_error, dead_error_handler)

    return client


async def _proccess():

    client = await get_client()
    if client is None:
        print("Нет данных для клиента")
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


async def run_service():
    while True:

        await _proccess()
        await asyncio.sleep(1)
