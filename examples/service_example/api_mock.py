from dataclasses import dataclass
from typing import Optional

from logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class SessionData:
    """Данные сессии пользователя"""

    slug: str
    string_session: str
    api_id: int
    api_hash: str
    device_model: str
    system_version: str
    app_version: str
    lang_code: str
    system_lang_code: str
    layer: int


@dataclass
class ProxyData:
    """Данные прокси"""

    slug: str
    host: str
    port: int
    username: str
    password: str
    proxy_type: str


class ApiMock:
    """Имитация API для получения данных сессий и прокси"""

    def __init__(self) -> None:
        self._session_data: Optional[SessionData] = None
        self._proxy_data: list[ProxyData] = []
        self._initialize_mock_data()

    def _initialize_mock_data(self) -> None:
        """Инициализация тестовых данных"""
        self._session_data = SessionData(
            slug="example_session",
            string_session="1ApWapzMBu4s-MNLyCzYPQuwzG5VTb2xgXBxJJ2Ib-CiZZEWjPzHKTIzu7GyXSeuWtls8YPROMm_qzLXxQfy7Uj_RsUXq-RDMFsjjz-tLLYIbgXpEnnfyRD2gWGMHtdwO_HOHkIG_r7ytwNsKSSRmjkTi6NKhfYQ6QgOb8eLOIud8ZC7fybaFXJ1X-npcill1vUHqkP33y-726h5gxXWGM5Yrr-3bC-UVNTPP_tWWdM_DFWPj_41cULq-2ttA2BikCkXmVjAjJzb8cN6GiZd7sMftjPGKuZsWjppCPjRSGcozGNsR69kbiYEX0ez5tWTc5zmlMDbfI_sx1M1GnKmu1qV4d8YGJX0=",
            api_id=12345,
            api_hash="your_api_hash_here",
            device_model="Mozilla Firefox 124.0",
            system_version="Windows 10",
            app_version="10.9.63 A",
            lang_code="ru",
            system_lang_code="ru-RU",
            layer=200,
        )

        self._proxy_data = [
            ProxyData(
                slug="proxy_1",
                host="127.0.0.1",
                port=1080,
                username="username1",
                password="password1",
                proxy_type="socks5",
            ),
            ProxyData(
                slug="proxy_2",
                host="127.0.0.1",
                port=9050,
                username="username2",
                password="password2",
                proxy_type="socks5",
            ),
        ]

    def get_session_data(self) -> Optional[SessionData]:
        """Получить данные сессии"""
        logger.debug(
            f"Запрос данных сессии: {self._session_data.slug if self._session_data else 'None'}"
        )
        return self._session_data

    async def update_session_data(self, slug: str, dead: bool) -> str:
        """Обновить статус сессии"""
        logger.info(f"Обновление статуса сессии {slug}: dead={dead}")
        # В реальном API здесь был бы HTTP запрос
        return "ok"

    async def update_proxy_data(self, slug: str, connect_error: bool) -> str:
        """Обновить статус прокси"""
        logger.warning(
            f"Обновление статуса прокси {slug}: connect_error={connect_error}"
        )
        # В реальном API здесь был бы HTTP запрос
        return "ok"

    def get_proxies(self) -> list[ProxyData]:
        """Получить список прокси"""
        logger.debug(f"Запрос списка прокси: {len(self._proxy_data)} шт.")
        return self._proxy_data.copy()
