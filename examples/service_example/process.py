import asyncio
from typing import Optional
from wtelethon import TelegramClient, MemoryAttachment, utils
from api_mock import ApiMock
from handlers import connect_error_handler
from logging_config import get_logger

api_mock = ApiMock()
logger = get_logger(__name__)


async def process_client(client: TelegramClient) -> None:
    session_name = client.memory.session_file
    proxy_info = f"{client.current_proxy.host}:{client.current_proxy.port}"

    logger.info(f"Connecting client {session_name} via {proxy_info}")

    await client.connect()
    logger.debug(f"Client {session_name} connected, checking auth")

    await client.check_authorization()
    logger.info(f"Client {session_name} authorized")


async def create_client() -> Optional[TelegramClient]:
    logger.debug("Requesting client data from API")
    session_data = api_mock.get_session_data()
    if session_data is None:
        logger.warning("No available client data")
        return None

    logger.debug(f"Creating client for session {session_data.slug}")

    memory = MemoryAttachment(
        api_id=session_data.api_id,
        api_hash=session_data.api_hash,
        device_model=session_data.device_model,
        system_version=session_data.system_version,
        app_version=session_data.app_version,
        lang_code=session_data.lang_code,
        system_lang_code=session_data.system_lang_code,
        layer=session_data.layer,
        slug=session_data.slug,
    )

    client = TelegramClient(session_data.string_session, memory_attachment=memory)

    client.add_exception_handler(utils.is_connection_error, connect_error_handler)
    logger.debug("Client configured")
    return client


async def _process_iteration() -> None:
    client = await create_client()
    if client is None:
        logger.debug("Skipping iteration - no available client")
        return

    session_name = client.memory.slug

    try:
        logger.debug(f"Setting proxy for client {session_name}")
        client.set_proxy_from_storage()
    except Exception as exc:
        logger.warning(f"Failed to set proxy for {session_name}: {exc}")
        return

    try:
        await process_client(client)
        logger.debug(f"Client {session_name} processed successfully")
    except Exception as exc:
        await client.disconnect()
        logger.debug(f"Client {session_name} disconnected after error")

        if utils.is_dead_error(exc):
            logger.error(f"Client {session_name} is dead: {exc.__class__.__name__}")
            await api_mock.update_session_data(client.memory.slug, dead=True)
        elif utils.is_connection_error(exc):
            logger.warning(f"Connection error for {session_name}: {exc.__class__.__name__}")
        else:
            logger.error(f"Unhandled error for {session_name}: {exc}", exc_info=True)
            raise exc


async def run_service() -> None:
    logger.info("Main service loop started")
    iteration = 0

    while True:
        iteration += 1
        logger.debug(f"Starting iteration #{iteration}")

        try:
            await _process_iteration()
        except Exception as exc:
            logger.error(f"Error in iteration #{iteration}: {exc}", exc_info=True)

        logger.debug(f"Iteration #{iteration} completed, waiting 1s")
        await asyncio.sleep(1)
