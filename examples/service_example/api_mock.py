from dataclasses import dataclass
from typing import Optional


@dataclass
class SessionData:
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


class ApiMock:

    def get_session_data(self) -> Optional[SessionData]:
        return SessionData(
            slug="test_session",
            string_session="1BVtsOK4Bu...",
            api_id=12345,
            api_hash="your_hash",
            device_model="iPhone 14 Pro",
            system_version="iOS 16.0",
            app_version="9.5.0",
            lang_code="en",
            system_lang_code="en-US",
            layer=162,
        )

    async def get_proxies(self) -> list[dict]:
        return [
            {"host": "127.0.0.1", "port": 1080, "type": "socks5"},
            {"host": "127.0.0.2", "port": 1080, "type": "socks5"},
        ]

    async def update_session_data(self, slug: str, dead: bool = False) -> None:
        pass
