from dataclasses import dataclass


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


@dataclass
class ProxyData:
    slug: str
    host: str
    port: int
    username: str
    password: str
    type: str


class ApiMock:
    def __init__(self):
        pass

    def get_session_data(self) -> SessionData:
        return SessionData(
            slug="hekekxow",
            string_session="1ApWapzMBu4s-MNLyCzYPQuwzG5VTb2xgXBxJJ2Ib-CiZZEWjPzHKTIzu7GyXSeuWtls8YPROMm_qzLXxQfy7Uj_RsUXq-RDMFsjjz-tLLYIbgXpEnnfyRD2gWGMHtdwO_HOHkIG_r7ytwNsKSSRmjkTi6NKhfYQ6QgOb8eLOIud8ZC7fybaFXJ1X-npcill1vUHqkP33y-726h5gxXWGM5Yrr-3bC-UVNTPP_tWWdM_DFWPj_41cULq-2ttA2BikCkXmVjAjJzb8cN6GiZd7sMftjPGKuZsWjppCPjRSGcozGNsR69kbiYEX0ez5tWTc5zmlMDbfI_sx1M1GnKmu1qV4d8YGJX0=",
            api_id=12345,
            api_hash="12345",
            device_model="Mozilla Firefox 124.0",
            system_version="Windows 10",
            app_version="10.9.63 A",
            lang_code="fa",
            system_lang_code="xh-ZA",
            layer=200,
        )

    def update_session_data(self, slug: str, dead: bool) -> str:
        return "ok"

    def get_proxies(self) -> list[ProxyData]:
        return [
            ProxyData(
                slug="hekekxow",
                host="127.0.0.1",
                port=1080,
                username="w1234567890",
                password="None",
                type="socks5",
            ),
            ProxyData(
                slug="scbdickd",
                host="127.0.0.1",
                port=9050,
                username="w1234567890",
                password="None",
                type="socks5",
            ),
        ]
