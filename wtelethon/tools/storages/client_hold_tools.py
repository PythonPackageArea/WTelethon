from typing import TYPE_CHECKING

from wtelethon.storages import client_holds_storage

if TYPE_CHECKING:
    from wtelethon import TelegramClient


class ClientHoldStorageTools:
    """Инструменты для управления временными блокировками клиентов."""

    def add_storage_hold(self: "TelegramClient", add_hold: int = 60):
        """Добавляет временную блокировку для клиента.

        Args:
            add_hold: Время блокировки в секундах (по умолчанию 60).

        Example:
            >>> # Добавить ужержание клиента на 2 минуты
            >>> client.add_storage_hold(120)
        """
        client_holds_storage.add_hold(self, add_hold)

    def reset_storage_hold(self: "TelegramClient"):
        """Сбрасывает блокировку клиента, если она была установлена.

        Example:
            >>> client.reset_storage_hold()
        """
        client_holds_storage.reset_hold(self)
