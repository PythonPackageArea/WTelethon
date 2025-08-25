import asyncio
import contextlib
from typing import Awaitable, Callable, Literal

from telethon_patch.storages import proxy_storage
from loguru import logger


def _sync_load_proxies_from_file_(filename: str, network_type: Literal["socks5", "http"]) -> None:
    with open(filename, mode="r", encoding="utf-8") as file:
        content = file.read()
        proxies = [line for _ in content.split("\n") if (line := _.strip())]

    proxy_storage.add_proxy(proxies, network_type=network_type)


async def load_proxies_from_file(filename: str, network_type: Literal["socks5", "http"]) -> None:
    """Загружает прокси из файла в глобальное хранилище.

    Args:
        filename: Путь к файлу с прокси (по одному на строку).
        network_type: Тип прокси - "socks5" или "http".

    Example:
        >>> # Загрузить SOCKS5 прокси
        >>> await load_proxies_from_file("socks5_proxies.txt", "socks5")
        >>>
        >>> # Загрузить HTTP прокси
        >>> await load_proxies_from_file("http_proxies.txt", "http")
    """
    await asyncio.to_thread(_sync_load_proxies_from_file_, filename=filename, network_type=network_type)
