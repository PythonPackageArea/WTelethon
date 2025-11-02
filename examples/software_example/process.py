import asyncio
from typing import Optional
from wtelethon import TelegramClient, storages, utils
from config import DEAD_DIR_PATH, SLEEP_INTERVAL
from logging_config import get_logger

logger = get_logger(__name__)


async def process_client(client: TelegramClient) -> None:
    session_name = client.memory.session_file
    logger.info(f"Processing account: {session_name}")

    logger.info(f"Connecting {session_name} via {client.current_proxy.host}:{client.current_proxy.port}")

    await client.connect()
    logger.info(f"Account {session_name} connected")

    await client.check_authorization()
    logger.info(f"Account {session_name} authorized")

    await client.disconnect()
    logger.info(f"Account {session_name} disconnected")


async def _process_iteration() -> None:
    client: Optional[TelegramClient] = storages.client_holds_storage.get_free_client()
    if client is None:
        logger.warning("No free accounts available")
        return

    session_name = client.memory.session_file

    try:
        client.set_proxy_from_storage()
    except Exception as exc:
        logger.warning(f"Failed to set proxy for {session_name}")
        return

    try:
        await process_client(client)
        client.remove_from_storage_hold()
    except Exception as exc:
        await client.disconnect()

        if utils.is_dead_error(exc):
            logger.error(f"Account {session_name} is no longer working")
            logger.info(f"Moving {session_name} to 'dead' folder")
            client.remove_from_storage_hold()
            await client.move_files(DEAD_DIR_PATH)
        elif utils.is_connection_error(exc):
            logger.warning(f"Network issues with {session_name}, will retry later")
        else:
            client.remove_from_storage_hold()
            logger.error(f"Unexpected error with {session_name}: {exc}")
            raise exc


async def run_software() -> None:
    logger.info("Started working with your accounts!")
    logger.info("Program will run until all accounts are processed. Press Ctrl+C to stop")

    try:
        while storages.client_holds_storage._holds:
            await _process_iteration()
            await asyncio.sleep(SLEEP_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Stopping program...")
        logger.info("Program stopped. Thank you!")
    except Exception as exc:
        logger.error(f"Critical error: {exc}")
        logger.error("Check settings and try again")
