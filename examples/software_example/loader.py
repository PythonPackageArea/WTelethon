import os
from pathlib import Path
from wtelethon import TelegramClient, JsonAttachment, MemoryAttachment, helpers
from config import WRONG_FORMAT_DIR_PATH, API_ID, API_HASH, CONNECTION_RETRIES
from logging_config import get_logger

logger = get_logger(__name__)


async def process_lone_files(files: helpers.files.GlobResponse) -> None:
    if files.json_loners:
        logger.warning(f"Found JSON files without session: {len(files.json_loners)}")
        logger.info("These files need to be cleaned up")

        response = input(f"Move them to '{WRONG_FORMAT_DIR_PATH}'? (y/n): ")
        if response.lower() == "y":
            for filename, path in files.json_loners.items():
                os.rename(path, WRONG_FORMAT_DIR_PATH / filename)
            logger.info("Unpaired JSON files moved")

    if files.session_loners:
        logger.warning(f"Found session files without JSON: {len(files.session_loners)}")
        logger.info("Can create JSON files for them")

        response = input("Create JSON files? (y/n): ")
        if response.lower() == "y":
            for filename, path in files.session_loners.items():
                json_path = str(path).replace(".session", ".json")

                json_dir = os.path.dirname(json_path)
                os.makedirs(json_dir, exist_ok=True)

                json_attachment = JsonAttachment(json_path, include_data={"api_id": API_ID, "api_hash": API_HASH})

                await json_attachment.save()
                logger.info(f"Created JSON for {filename}")
        else:
            response2 = input(f"Move to '{WRONG_FORMAT_DIR_PATH}'? (y/n): ")
            if response2.lower() == "y":
                for filename, path in files.session_loners.items():
                    os.rename(path, WRONG_FORMAT_DIR_PATH / filename)
                logger.info("Unpaired session files moved")


async def load_clients(dir_path: Path) -> list[TelegramClient]:
    files = helpers.files.glob_files(dir_path)
    clients = []

    if not files.items():
        logger.warning("No session+json file pairs found")

    await process_lone_files(files)

    for session_name, item in files.items():
        try:
            client = TelegramClient(
                item.session,
                json_attachment=await JsonAttachment(item.json).load(),
                connection_retries=CONNECTION_RETRIES,
            )
            clients.append(client)
            logger.info(f"Client loaded: {session_name}")
        except Exception as exc:
            logger.error(f"Error loading {session_name}: {exc}")

    return clients
