import contextlib
import time
from typing import TYPE_CHECKING, Optional

from wtelethon.lib.metaclasses.singleton import _SingletonMeta


if TYPE_CHECKING:
    from wtelethon.client import TelegramClient


class ClientHoldsStorage(metaclass=_SingletonMeta):
    """Глобальное хранилище временных блокировок клиентов (singleton)."""

    _holds: dict["TelegramClient", int]

    def __init__(self):
        self._holds = {}

    def add_client(self, client: "TelegramClient"):
        """Добавляет клиента в хранилище с текущим временем."""
        self._holds[client] = time.time()

    def add_hold(self, client: "TelegramClient", add_hold: int = 60):
        """Добавляет временную блокировку для клиента.

        Args:
            client: Клиент для блокировки.
            add_hold: Время блокировки в секундах.
        """
        self._holds[client] = time.time() + add_hold

    def reset_hold(self, client: "TelegramClient"):
        """Снимает блокировку с клиента.

        Args:
            client: Клиент для разблокировки.
        """
        with contextlib.suppress(KeyError):
            self._holds.pop(client)

    def get_free_client(self, client: "TelegramClient") -> Optional["TelegramClient"]:
        """Возвращает свободный клиент, если время блокировки истекло.

        Args:
            client: Клиент для проверки.

        Returns:
            Клиент если он свободен, иначе None.
        """
        for client in self._holds:
            if self._holds[client] < time.time():
                return client

        return None
