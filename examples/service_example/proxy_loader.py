from wtelethon.storages import proxy_storage, Proxy
from api_mock import ApiMock
from logging_config import get_logger

api_mock = ApiMock()
logger = get_logger(__name__)


async def load_proxies() -> None:
    logger.debug("Fetching proxies from API")
    proxies = await api_mock.get_proxies()

    if not proxies:
        logger.warning("No proxies available from API")
        return

    for proxy_data in proxies:
        proxy = Proxy(
            host=proxy_data["host"],
            port=proxy_data["port"],
            username=proxy_data.get("username"),
            password=proxy_data.get("password"),
            network_type=proxy_data.get("type", "socks5"),
        )
        proxy_storage.add_proxy(proxy)

    logger.info(f"Loaded {len(proxies)} proxies from API")
