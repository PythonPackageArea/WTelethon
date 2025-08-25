import asyncio
import codecs
import datetime
import inspect
import os
import base64
import struct
from typing import Awaitable, Callable, Union, TYPE_CHECKING, Optional

from telethon.client import UserMethods
from telethon.crypto import AuthKey
from telethon.helpers import TotalList
from telethon.tl import TLRequest
from telethon.types import JsonObject
from telethon_patch import tl_types, tl_functions, tl_errors
from telethon_patch import utils, helpers

from telethon.sessions import SQLiteSession, StringSession, MemorySession

from telethon_patch.attachments.platform.model import PlatformData
from telethon.tl.alltlobjects import LAYER

if TYPE_CHECKING:
    from telethon_patch import TelegramClient


class PlatformAttachmentTools:
    """Миксин для работы с платформенными параметрами клиента."""

    _init_params: Optional[tl_types.JsonObject]

    def get_layer(self: "TelegramClient") -> int:
        """Возвращает текущий слой MTProto.

        Returns:
            Номер слоя MTProto.

        Example:
            >>> layer = client.get_layer()
            >>> print(f"MTProto layer: {layer}")
        """
        return self.memory.layer or LAYER

    def set_layer(self: "TelegramClient", layer: int) -> None:
        """Сохраняет слой MTProto в памяти."""
        self.memory.layer = layer

    def update_client_params(self: "TelegramClient", value: tl_types.JsonObject) -> None:
        """Обновляет параметры клиента."""
        self._init_request.params = value

    def update_client_lang_pack(self: "TelegramClient", lang_pack: str) -> None:
        """Изменяет lang_pack клиента."""
        self._init_request.lang_pack = lang_pack
        self.memory.lang_pack = lang_pack

    def update_client_platform(self: "TelegramClient", platform: PlatformData) -> "TelegramClient":
        """Применяет параметры выбранной платформы и переинициализирует клиент.

        Args:
            platform: Объект PlatformData с настройками платформы.

        Returns:
            Ссылку на сам клиент для цепочки вызовов.

        Example:
            >>> from telethon_patch import PlatformAttachment
            >>> client.update_client_platform(PlatformAttachment.android)
        """

        data = platform.get_data(self)

        api_id, api_hash = data.get("api_id"), data.get("api_hash")
        assert api_id and api_hash, "API ID or API hash is required"

        self.memory.api_id = api_id
        self.memory.api_hash = api_hash
        self.memory.device_model = data.get("device_model")
        self.memory.system_version = data.get("system_version")
        self.memory.app_version = data.get("app_version")
        self.memory.lang_code = data.get("lang_code")
        self.memory.system_lang_code = data.get("system_lang_code")
        self._super_init()

        self.update_client_lang_pack(data.get("lang_pack") or "")
        self.update_client_params(data.get("params"))

        return self
