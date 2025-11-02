import asyncio
import sys
from wtelethon import helpers, storages, utils
from config import ALIVE_DIR_PATH, PROXIES_FILE_PATH, PROXY_TYPE
from handlers import connect_error_handler
from loader import load_clients
from logging_config import setup_user_logging, get_logger
from process import run_software

setup_user_logging()
helpers.logging.set_telethon_logging("off")

logger = get_logger(__name__)


async def main() -> None:
    logger.info("Welcome to Software Example!")

    logger.info("Loading proxies...")
    try:
        await helpers.storages.proxies.load_proxies_from_file(PROXIES_FILE_PATH, PROXY_TYPE)
    except Exception as exc:
        logger.error(f"Failed to load proxies: {exc}")
        logger.error("Check proxy file and try again")
        sys.exit(1)

    proxy_count = len(storages.proxy_storage._proxies)
    logger.info(f"Loaded {proxy_count} proxies")

    logger.info("Searching for sessions...")
    clients = await load_clients(ALIVE_DIR_PATH)

    if not clients:
        logger.error("No sessions found")
        logger.error(f"Place .session files in {ALIVE_DIR_PATH}")
        sys.exit(1)

    logger.info(f"Loaded {len(clients)} clients")

    for client in clients:
        client.add_exception_handler(utils.is_connection_error, connect_error_handler)
        storages.client_holds_storage.add_client(client)

    logger.info("Starting client processing...")
    await run_software()


if __name__ == "__main__":
    asyncio.run(main())
