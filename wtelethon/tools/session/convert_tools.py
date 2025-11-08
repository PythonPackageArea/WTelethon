import asyncio
import codecs
import os
from typing import TYPE_CHECKING, Optional, List

from telethon.crypto import AuthKey
from telethon.sessions import SQLiteSession, StringSession

from wtelethon import utils, helpers

if TYPE_CHECKING:
    from wtelethon import TelegramClient


class ConvertTools:
    """Инструменты для конвертации сессий между разными форматами."""

    def _sync_create_sqlite_session(
        self: "TelegramClient",
        dir_path: str,
        filename: str,
    ) -> bool:
        if self.memory.source_dir and self.memory.session_file:
            session_path = os.path.join(self.memory.source_dir, self.memory.session_file)
            if os.path.exists(session_path):
                return True

        if isinstance(self.session, SQLiteSession):
            return True

        file_name = str(filename or self.memory.phone or self.memory.session_file or self.memory.account_id)
        if not file_name:
            raise ValueError("file_name is required")

        file_name = f"{file_name.strip('.session')}.session"

        utils.ensure_dir(dir_path)
        session_path = os.path.join(dir_path, file_name)
        session = SQLiteSession(session_path)

        session.set_dc(
            self.session.dc_id,
            self.session.server_address,
            self.session.port,
        )
        session.auth_key = self.session.auth_key
        session.close()

        self.memory.source_dir = dir_path
        self.memory.session_file = file_name

        return True

    async def create_sqlite_session(
        self: "TelegramClient",
        dir_path: str,
        filename: str,
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
            self._sync_create_sqlite_session,
            dir_path=dir_path,
            filename=filename,
        )

    def _sync_load_sqlite_session(
        self: "TelegramClient",
    ) -> StringSession:
        session_path = os.path.join(self.memory.source_dir, self.memory.session_file)

        if not self.memory.session_file or not os.path.exists(session_path):
            raise ValueError("session file not found")

        sqlite_session = SQLiteSession(session_path)

        self.session = StringSession()
        self.set_dc(sqlite_session.dc_id)
        self.set_auth_key(sqlite_session.auth_key)

        return self.session

    async def load_sqlite_session(
        self: "TelegramClient",
    ) -> StringSession:
        """Конвертирует SQLite сессию в StringSession (в памяти).


        Returns:
            True если конвертация успешна.

        Example:
            >>> # Загрузить SQLiteSession сессию, сохраняя как StringSession
            >>> await client.load_sqlite_session()
        """
        return await asyncio.to_thread(
            self._sync_load_sqlite_session,
        )

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

    def load_auth_key_hex(
        self: "TelegramClient",
        auth_key_hex: str,
        dc_id: int,
    ) -> StringSession:
        """Создаёт сессию из hex-ключа авторизации.

        Args:
            auth_key_hex: Ключ авторизации в шестнадцатеричном формате.
            dc_id: ID дата-центра.

        Returns:
            True если конвертация успешна.

        Example:
            >>> # Восстановить сессию из hex-ключа
            >>> key = "a1b2c3d4e5f6..."
            >>> client.load_auth_key_hex(key, dc_id=2)
        """
        self.session = StringSession()

        self.set_dc(dc_id)
        self.set_auth_key(AuthKey(codecs.decode(auth_key_hex, encoding="hex")))

        return self.session

    def set_dc(
        self: "TelegramClient",
        dc_id: int,
    ) -> bool:
        self.session.set_dc(dc_id, utils.get_dc_address(dc_id), 443)
        return True

    def set_auth_key(
        self: "TelegramClient",
        auth_key: AuthKey,
    ) -> bool:
        self.session.auth_key = auth_key
        return True

    def create_tdata(
        self: "TelegramClient",
        tdata_output_path: str,
        passcode: str = "",
    ) -> bool:
        """Создает TData из текущей сессии клиента.

        Args:
            tdata_output_path: Путь для сохранения TData.
            passcode: Пароль для TData (опционально).

        Returns:
            True если создание прошло успешно.

        Example:
            >>> success = client.create_tdata("./new_tdata")
        """
        if not self.session.auth_key or not self.session.dc_id:
            raise ValueError("Client session is not authorized")

        utils.ensure_dir(tdata_output_path)

        return helpers.tdata._create_tdata_files(tdata_output_path, [(self.session.dc_id, self.session.auth_key.key)], passcode)

    @staticmethod
    def create_tdata_from_clients(
        clients: List["TelegramClient"],
        tdata_output_path: str,
        passcode: str = "",
        active_index: int = 0,
    ) -> bool:
        """Создает TData из нескольких клиентов.

        Args:
            clients: Список клиентов для добавления в TData.
            tdata_output_path: Путь для сохранения TData.
            passcode: Пароль для TData (опционально).
            active_index: Индекс активного аккаунта.

        Returns:
            True если создание прошло успешно.

        Example:
            >>> clients = [client1, client2, client3]
            >>> success = ConvertTools.create_tdata_from_clients(clients, "./multi_tdata")
        """
        if not clients:
            raise ValueError("At least one client is required")

        accounts = []
        for client in clients:
            if not client.session.auth_key or not client.session.dc_id:
                raise ValueError("Client session is not authorized")
            accounts.append((client.session.dc_id, client.session.auth_key.key))

        utils.ensure_dir(tdata_output_path)

        return helpers.tdata._create_tdata_files(tdata_output_path, accounts, passcode, active_index)
