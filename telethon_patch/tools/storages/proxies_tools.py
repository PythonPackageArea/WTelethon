from typing import TYPE_CHECKING

from telethon_patch.storages import proxy_storage


if TYPE_CHECKING:
    from telethon_patch import TelegramClient
    from telethon_patch.storages import Proxy


class ProxyStorageTools:
    """Инструменты для работы с хранилищем прокси-серверов."""

    _current_proxy: "Proxy"

    @property
    def current_proxy(self: "TelegramClient") -> "Proxy":
        """Возвращает текущий прокси клиента.

        Returns:
            Объект Proxy или None если прокси не установлен.

        Example:
            >>> if client.current_proxy:
            >>>     print(f"Прокси: {client.current_proxy.host}:{client.current_proxy.port}")
        """
        return getattr(self, "_current_proxy", None)

    def set_proxy_from_storage(
        self: "TelegramClient",
        random_choice: bool = False,
        usage_index_choice: bool = True,
    ) -> "Proxy":
        """Устанавливает прокси из хранилища для клиента.

        Args:
            random_choice: Если True, выбирает прокси случайно.
            usage_index_choice: Если True, выбирает по индексу использования.

        Returns:
            Объект установленного прокси.

        Raises:
            ValueError: Если в хранилище нет доступных прокси.

        Example:
            >>> # Установить прокси по умолчанию (по индексу)
            >>> proxy = client.set_proxy_from_storage()
            >>>
            >>> # Установить случайный прокси
            >>> proxy = client.set_proxy_from_storage(random_choice=True)
        """
        new_proxy = proxy_storage.get_proxy(
            random_choice=random_choice,
            usage_index_choice=usage_index_choice,
        )
        if not new_proxy:
            raise ValueError("No available proxies found")

        self.set_proxy(new_proxy.client_format())
        self._current_proxy = new_proxy
        return new_proxy

    def proxy_error(self: "TelegramClient"):
        """Отмечает ошибку для текущего прокси.

        Увеличивает счетчик ошибок для текущего прокси, что влияет
        на его приоритет при следующем выборе.

        Example:
            >>> try:
            >>>     await client.connect()
            >>> except ConnectionError:
            >>>     client.proxy_error()  # отметить ошибку прокси
            >>>     client.set_proxy_from_storage()  # взять другой
        """
        if self.current_proxy:
            self.current_proxy.add_error()
