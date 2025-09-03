import os
from pathlib import Path

from wtelethon import TelegramClient, JsonAttachment, MemoryAttachment, helpers

from config import WRONG_FORMAT_DIR_PATH, API_ID, API_HASH, CONNECTION_RETRIES
from logging_config import get_logger

logger = get_logger(__name__)


async def process_lone_files(files: helpers.files.GlobResponse) -> None:
    """Обработка файлов без пары (json без session или наоборот)"""
    if files.json_loners:
        logger.warning(f"Найдены JSON файлы без session: {len(files.json_loners)}")
        logger.info("Эти файлы нужно очистить")

        response = input(f"Переместить их в папку '{WRONG_FORMAT_DIR_PATH}'? (y/n): ")
        if response.lower() == "y":
            for filename, path in files.json_loners.items():
                os.rename(path, WRONG_FORMAT_DIR_PATH / filename)
            logger.info("Непарные JSON файлы перемещены")

    if files.session_loners:
        logger.warning(f"Найдены session файлы без JSON: {len(files.session_loners)}")
        logger.info("Можно создать для них JSON файлы")

        response = input("Создать JSON файлы? (y/n): ")
        if response.lower() == "y":
            for filename, path in files.session_loners.items():
                json_path = str(path).replace(".session", ".json")
                json_attachment = await JsonAttachment(json_path)

                memory_attachment = MemoryAttachment(
                    api_id=API_ID,
                    api_hash=API_HASH,
                )
                memory_attachment.fill_json(json_attachment)
                await json_attachment.save()
                logger.info(f"Создан JSON для {filename}")
        else:
            response2 = input(f"Переместить в папку '{WRONG_FORMAT_DIR_PATH}'? (y/n): ")
            if response2.lower() == "y":
                for filename, path in files.session_loners.items():
                    os.rename(path, WRONG_FORMAT_DIR_PATH / filename)
                logger.info("Непарные session файлы перемещены")


async def load_clients(dir_path: Path) -> list[TelegramClient]:
    """Загрузка клиентов из директории"""
    files = helpers.files.glob_files(dir_path)
    clients = []

    if not files.items():
        logger.warning("Не найдено ни одной пары session+json файлов")

    # Обработка непарных файлов
    await process_lone_files(files)

    # Загрузка клиентов
    for session_name, item in files.items():
        try:
            client = TelegramClient(
                item.session,
                json_attachment=await JsonAttachment(item.json).load(),
                connection_retries=CONNECTION_RETRIES,
            )
            clients.append(client)
            logger.info(f"Клиент загружен: {session_name}")
        except Exception as e:
            logger.error(f"Ошибка загрузки {session_name}: {e}")

    return clients
