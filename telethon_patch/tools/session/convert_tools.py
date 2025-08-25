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
from telethon_patch import tl_types, tl_functions, tl_errors
from telethon_patch import utils, helpers

from telethon.sessions import SQLiteSession, StringSession, MemorySession

if TYPE_CHECKING:
    from telethon_patch import TelegramClient


class ConvertTools:
    """Инструменты для конвертации сессий между разными форматами."""

    def _sync_convert_to_sqlite(
        self: "TelegramClient",
        dir_path: str,
        file_name: str,
        change_client: bool = True,
    ) -> bool:
        if isinstance(self.session, SQLiteSession):
            return True

        file_name = file_name or self.memory.phone or self.memory.session_file or self.memory.account_id
        if not file_name:
            raise ValueError("file_name is required")

        if not file_name.endswith(".session"):
            file_name += ".session"

        utils.ensure_dir(dir_path)
        session = SQLiteSession(os.path.join(dir_path, file_name))
        session.auth_key = self.session.auth_key
        session.set_dc(
            self.session.dc_id,
            self.session.server_address,
            self.session.port,
        )

        if change_client:
            self.session = session

        return True

    async def convert_to_sqlite(
        self: "TelegramClient",
        dir_path: str,
        file_name: str,
        change_client: bool = True,
    ) -> bool:
        """Конвертирует сессию в SQLite формат.

        Args:
            dir_path: Путь к директории для сохранения .session файла.
            file_name: Имя файла (без расширения).
            change_client: Если True, заменяет текущую сессию клиента на SQLite.

        Returns:
            True если конвертация успешна.

        Example:
            >>> # Конвертировать и заменить текущую сессию
            >>> await client.convert_to_sqlite("./sessions", "my_account")
            >>>
            >>> # Создать SQLite файл без замены текущей сессии
            >>> await client.convert_to_sqlite("./backup", "backup_session", False)
        """
        return await asyncio.to_thread(
            self._sync_convert_to_sqlite,
            dir_path=dir_path,
            file_name=file_name,
            change_client=change_client,
        )

    async def convert_from_sqlite(
        self: "TelegramClient",
        delete_sqlite_session: bool = True,
        change_client: bool = True,
    ) -> bool:
        """Конвертирует SQLite сессию в StringSession (в памяти).

        Args:
            delete_sqlite_session: Если True, удаляет исходный .session файл.
            change_client: Если True, заменяет текущую сессию клиента на StringSession.

        Returns:
            True если конвертация успешна.

        Example:
            >>> # Конвертировать в память и удалить файл
            >>> await client.convert_from_sqlite()
            >>>
            >>> # Конвертировать без удаления файла
            >>> await client.convert_from_sqlite(delete_sqlite_session=False)
        """
        if not isinstance(self.session, SQLiteSession):
            return True

        session = StringSession()
        session.auth_key = self.session.auth_key
        session.set_dc(self.session.dc_id, self.session.server_address, self.session.port)

        if delete_sqlite_session:
            self.session.delete()

        if change_client:
            self.session = session

        return True

    def get_session_string(
        self: "TelegramClient",
    ) -> str:
        """Возвращает строковое представление сессии.

        Returns:
            Строка сессии, которую можно использовать для восстановления.

        Example:
            >>> session_string = client.get_session_string()
            >>> print(f"Session: {session_string[:50]}...")
        """
        return StringSession.save(self.session)

    def get_auth_key_hex(
        self: "TelegramClient",
    ) -> str:
        """Возвращает ключ авторизации в шестнадцатеричном формате.

        Returns:
            Hex-строка ключа авторизации.

        Example:
            >>> auth_key = client.get_auth_key_hex()
            >>> print(f"Auth key: {auth_key[:32]}...")
        """
        return codecs.encode(self.session.auth_key.key, encoding="hex").decode()

    def convert_from_auth_key_hex(
        self: "TelegramClient",
        auth_key_hex: str,
        dc_id: int,
        change_client: bool = True,
    ) -> bool:
        """Создаёт сессию из hex-ключа авторизации.

        Args:
            auth_key_hex: Ключ авторизации в шестнадцатеричном формате.
            dc_id: ID дата-центра.
            change_client: Если True, заменяет текущую сессию клиента.

        Returns:
            True если конвертация успешна.

        Example:
            >>> # Восстановить сессию из hex-ключа
            >>> key = "a1b2c3d4e5f6..."
            >>> client.convert_from_auth_key_hex(key, dc_id=2)
        """
        session = StringSession()
        session.auth_key = AuthKey(codecs.decode(auth_key_hex, encoding="hex"))
        session.set_dc(dc_id, utils.get_dc_address(dc_id), 443)

        if change_client:
            self.session = session

        return True
