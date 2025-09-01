import contextlib
import random
import time
from typing import Literal, Optional, Union

import python_socks

from wtelethon.lib.metaclasses.singleton import _SingletonMeta


_LIMIT_PROXY_ERRORS: int = 3
_LIMIT_PROXY_ERRORS_TIME: int = 60 * 3
_LIMIT_BEFORE_ERROR: int = 0.5


class Proxy:
    """Представляет прокси-сервер с метаданными использования."""

    __source: str
    __host: str
    __port: int
    __username: Optional[str]
    __password: Optional[str]
    __network_type: str
    __last_used: float
    __last_errors: list[float]

    @property
    def source(self) -> str:
        return self.__source

    @property
    def host(self) -> str:
        return self.__host

    @property
    def port(self) -> int:
        return self.__port

    @property
    def username(self) -> Optional[str]:
        return self.__username

    @property
    def password(self) -> Optional[str]:
        return self.__password

    @property
    def network_type(self) -> str:
        return self.__network_type

    @property
    def last_used(self) -> float:
        return self.__last_used

    @property
    def last_errors(self) -> list[float]:
        return self.__last_errors

    def __init__(
        self,
        source: str,
        host: str,
        port: int,
        network_type: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        if network_type not in ["socks5", "http"]:
            raise ValueError("Invalid network type")

        self.__source = source
        self.__host = host
        self.__port = port
        self.__username = username
        self.__password = password
        self.__network_type = network_type.upper()
        self.__last_used = time.time()
        self.__last_errors = []

    def client_format(
        self,
    ) -> tuple[python_socks.ProxyType, str, int, bool, Optional[str], Optional[str]]:
        """Возвращает прокси в формате для python-socks клиента.

        Returns:
            Кортеж (ProxyType, host, port, auth_required, username, password).

        Example:
            >>> proxy = Proxy("source", "127.0.0.1", 1080, "socks5", "user", "pass")
            >>> format_tuple = proxy.client_format()
            >>> # Можно использовать для настройки клиента
        """
        return (
            python_socks.ProxyType[self.network_type],
            self.host,
            self.port,
            self.username and self.password,
            self.username,
            self.password,
        )

    def usage_update(self):
        """Обновляет время последнего использования прокси."""
        self.__last_used = time.time()

    def clear_errors(self):
        """Очищает устаревшие ошибки прокси."""
        self.__last_errors = [
            err
            for err in self.__last_errors
            if time.time() - err <= _LIMIT_PROXY_ERRORS_TIME
        ]

    def add_error(self):
        """Добавляет ошибку прокси с текущим временем."""
        self.clear_errors()
        self.__last_errors.append(time.time())


class ProxyStorage(metaclass=_SingletonMeta):
    """Глобальное хранилище прокси-серверов (singleton)."""

    _proxies: dict[str, Proxy]

    _limit_proxy_errors: int = _LIMIT_PROXY_ERRORS
    _limit_proxy_errors_time: int = _LIMIT_PROXY_ERRORS_TIME

    def __init__(self):
        self._proxies = {}

    def add_proxy(
        self, proxy: Union[str, Proxy], network_type: Literal["socks5", "http"]
    ):
        """Добавляет прокси в хранилище.

        Args:
            proxy: Прокси как строка "host:port" или "user:pass@host:port", или объект Proxy.
            network_type: Тип прокси - "socks5" или "http".

        Example:
            >>> storage = ProxyStorage()
            >>> storage.add_proxy("127.0.0.1:1080", "socks5")
            >>> storage.add_proxy("user:pass@proxy.com:8080", "http")
        """
        if isinstance(proxy, str):
            attrs = proxy.split(":")
            if len(attrs) not in [2, 4]:
                raise ValueError("Invalid proxy string")

            if len(attrs) == 4:
                index = 0 if attrs[1].isdigit() else 2 if attrs[3].isdigit() else None
                if index is None:
                    raise ValueError("Invalid proxy string: {}".format(proxy))

                username, password = attrs[(index + 2) % 4], attrs[(index + 3) % 4]

            else:
                username, password = None, None
                index = 0

            proxy = Proxy(
                proxy,
                host=attrs[index],
                port=int(attrs[index + 1]),
                network_type=network_type,
                username=username,
                password=password,
            )

        else:
            proxy = proxy

        self._proxies[proxy.source] = proxy

    def _get_available_proxies(self) -> list[Proxy]:
        for proxy in self._proxies.values():
            proxy.clear_errors()
            if proxy.last_errors and (
                time.time() - proxy.last_errors[-1] < _LIMIT_BEFORE_ERROR
                or len(proxy.last_errors) >= _LIMIT_PROXY_ERRORS
            ):
                continue

            yield proxy

    def get_proxy(
        self, random_choice: bool = False, usage_index_choice: bool = True
    ) -> Optional[Proxy]:
        """Получает доступный прокси из хранилища.

        Args:
            random_choice: Если True, выбирает случайный доступный прокси.
            usage_index_choice: Если True, выбирает наименее использованный прокси.

        Returns:
            Объект Proxy или None если нет доступных прокси.

        Raises:
            ValueError: Если оба параметра True или оба False.

        Example:
            >>> # Получить наименее использованный прокси
            >>> proxy = storage.get_proxy(usage_index_choice=True)
            >>>
            >>> # Получить случайный прокси
            >>> proxy = storage.get_proxy(random_choice=True)
        """
        if not self._proxies:
            return None

        if all([random_choice, usage_index_choice]):
            raise ValueError(
                "random_choice and usage_index_choice cannot be True at the same time"
            )

        if not any([random_choice, usage_index_choice]):
            raise ValueError("random_choice or usage_index_choice must be True")

        available_proxies = list(self._get_available_proxies())
        if not available_proxies:
            return None

        if random_choice:
            proxy = random.choice(available_proxies)

        if usage_index_choice:
            proxy = next(
                iter(
                    sorted(available_proxies, key=lambda x: x.last_used, reverse=False)
                )
            )

        proxy.usage_update()
        return proxy
