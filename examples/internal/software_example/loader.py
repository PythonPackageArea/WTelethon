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

from config import wrong_format_dir_path


async def loners_process(files: helpers.files.GlobResponse):

    if files.json_loners:
        print("json файлов без session:", files.json_loners.__len__())
        if input("Переместить их в неверный формат? (y/n): ") == "y":
            for filename, path in files.json_loners.items():
                os.rename(path, wrong_format_dir_path / filename)

            print("Перемещение json файлов в неверный формат завершено")

    if files.session_loners:

        print("\n\nsession файлов без json:", files.session_loners.__len__())
        if input("Сгенерировать для них json? (y/n): ") == "y":
            for filename, path in files.session_loners.items():
                json_attachment = await JsonAttachment(
                    path.replace(".session", ".json")
                )
                memory_attachment = MemoryAttachment(
                    api_id=12345,
                    api_hash="12345",
                )
                memory_attachment.fill_json(json_attachment)
                await json_attachment.save()

        else:
            if input("Переместить их в неверный формат? (y/n): ") == "y":
                for filename, path in files.session_loners.items():
                    os.rename(path, wrong_format_dir_path / filename)

                print("Перемещение session файлов в неверный формат завершено")


async def load_clients(dir_path: Path) -> list[TelegramClient]:
    files = helpers.files.glob_files(dir_path)
    clients = []

    await loners_process(files)

    for _, item in files.items():
        client = TelegramClient(
            item.session,
            json_attachment=await JsonAttachment(item.json).load(),
            connection_retries=0,
        )
        clients.append(client)

        """
        # variation
        client = TelegramClient(
            item.session,
            json_path=item.json,
        )
        await client.load_json_info()
  
        """

    return clients
