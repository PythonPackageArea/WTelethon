from wtelethon import storages
from wtelethon.storages.proxies import Proxy

from api_mock import ApiMock
from logging_config import get_logger

api_mock = ApiMock()
logger = get_logger(__name__)


async def load_proxies() -> None:
    """Загрузка прокси из API в хранилище"""
    logger.debug("Начало загрузки прокси из API")
    proxies = api_mock.get_proxies()

    added_count = 0
    for proxy_data in proxies:
        proxy = Proxy(
            source=proxy_data.slug,
            host=proxy_data.host,
            port=proxy_data.port,
            network_type=proxy_data.proxy_type,
            username=proxy_data.username,
            password=proxy_data.password,
        )
        storages.proxy_storage.add_proxy(proxy, proxy_data.proxy_type)
        added_count += 1
        logger.debug(
            f"Добавлен прокси {proxy_data.slug}: {proxy_data.host}:{proxy_data.port}"
        )

    # Удаляем прокси которых больше нет в API
    existing_slugs = {p.slug for p in proxies}
    removed_count = 0
    for proxy_source in list(storages.proxy_storage._proxies.keys()):
        if proxy_source not in existing_slugs:
            storages.proxy_storage.remove_proxy(proxy_source)
            removed_count += 1
            logger.debug(f"Удален устаревший прокси: {proxy_source}")

    logger.info(f"Загрузка прокси завершена: +{added_count}, -{removed_count}")
    logger.info(f"Активных прокси: {len(storages.proxy_storage._proxies)}")
