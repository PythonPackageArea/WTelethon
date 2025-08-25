from typing import TYPE_CHECKING, Optional

from telethon_patch import JsonAttachment

if TYPE_CHECKING:
    from telethon_patch import TelegramClient


class JsonAttachmentTools:
    """Миксин для работы с JsonAttachment."""

    _json: JsonAttachment

    @property
    def json(self) -> JsonAttachment:
        """Возвращает JsonAttachment если он инициализирован.

        Returns:
            JsonAttachment объект или None если не инициализирован.

        Example:
            >>> if client.json:
            >>>     print(f"JSON файл: {client.json.file_path}")
        """
        return getattr(self, "_json", None)

    def init_json(self, file_path: str, include_data: Optional[dict] = None) -> bool:
        """Создаёт JsonAttachment и сохраняет ссылку.

        Args:
            file_path: Путь к JSON файлу.
            include_data: Дополнительные данные для включения.

        Returns:
            True если инициализация прошла успешно.

        Example:
            >>> client.init_json("account.json", {"custom_field": "value"})
        """
        if getattr(self, "_json", None) is not None:
            raise ValueError("json is already set")

        self._json = JsonAttachment(file_path=file_path, include_data=include_data)
        return True

    async def load_json_info(self: "TelegramClient") -> bool:
        """Загружает данные из JSON и применяет к памяти клиента.

        Returns:
            True если данные успешно загружены.

        Example:
            >>> await client.load_json_info()
            >>> print(f"Загружен аккаунт: {client.memory.phone}")
        """
        if self.json is None:
            raise ValueError("json is not set")

        await self.json.load()
        self.json.fill_memory(self.memory)
        self._super_init()
        return True

    async def dump_json_info(self: "TelegramClient") -> bool:
        """Сохраняет информацию из памяти клиента в JSON файл.

        Returns:
            True если данные успешно сохранены.

        Example:
            >>> # Обновить данные в памяти
            >>> client.memory.first_name = "Новое имя"
            >>> # Сохранить изменения
            >>> await client.dump_json_info()
        """
        if self.json is None:
            raise ValueError("json is not set")

        self.memory.fill_json(self.json)
        await self.json.save()
        return True
