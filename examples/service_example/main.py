import asyncio
from wtelethon import helpers
from api_mock import ApiMock
from logging_config import setup_service_logging, get_logger
from process import run_service
from proxy_loader import load_proxies

setup_service_logging()
helpers.logging.set_telethon_logging("off")

api_mock = ApiMock()
logger = get_logger(__name__)


async def main() -> None:
    logger.info("Starting WTelethon service")

    try:
        logger.debug("Loading proxies from API")
        await helpers.tasks.run_fetch_task(load_proxies)
        logger.info("Proxies loaded successfully")

        logger.info("Starting main service loop")
        await run_service()
    except Exception as exc:
        logger.error(f"Critical service error: {exc}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
