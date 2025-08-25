import asyncio
import codecs
import datetime
import inspect
import os
import base64
import struct
import shutil
from typing import Awaitable, Callable, Union, TYPE_CHECKING, Optional

from telethon._updates import session
from telethon.client import UserMethods
from telethon.crypto import AuthKey
from telethon.helpers import TotalList
from telethon.tl import TLRequest
from wtelethon import tl_types, tl_functions, tl_errors
from wtelethon import utils, helpers

from telethon.sessions import SQLiteSession, StringSession, MemorySession

if TYPE_CHECKING:
    from wtelethon import TelegramClient


class FileAttachmentsTools:
    """Инструменты для управления файлами сессий и JSON вложений."""

    def __check_session_type(self: "TelegramClient") -> SQLiteSession:
        if not isinstance(self.session, SQLiteSession):
            raise ValueError("session is not a SQLiteSession")

        return self.session

    def __update_path(self: "TelegramClient", _type: str, path: str) -> None:
        if _type == "session":
            session = self.__check_session_type()
            session.close()
            session.filename = path

        elif _type == "json":
            if self.json:
                self.json._file_path = path

        else:
            raise ValueError(f"Invalid type: {_type}")

    def __get_path(self: "TelegramClient", _type: str) -> str:
        if _type == "session":
            return self.__check_session_type().filename
        elif _type == "json":
            return self.json.file_path
        else:
            raise ValueError(f"Invalid type: {_type}")

    def __iter_file_types(
        self: "TelegramClient", session_enabled: bool, json_enabled: bool
    ) -> str:
        return (
            _type
            for _type in ["session", "json"]
            if (_type == "session" and session_enabled)
            or (_type == "json" and json_enabled and self.json)
        )

    def _sync_move_files(
        self: "TelegramClient",
        session_enabled: bool,
        json_enabled: bool,
        new_dir_path: Optional[str] = None,
        new_file_name: Optional[str] = None,
    ) -> bool:
        if new_dir_path:
            utils.ensure_dir(new_dir_path)

        for _type in self.__iter_file_types(session_enabled, json_enabled):
            current_path = self.__get_path(_type)
            new_file_path = os.path.join(
                new_dir_path, new_file_name or os.path.basename(current_path)
            )

            shutil.move(current_path, new_file_path)
            self.__update_path(_type, new_file_path)

        return True

    def _sync_copy_files(
        self: "TelegramClient",
        session_enabled: bool,
        json_enabled: bool,
        new_dir_path: Optional[str] = None,
        new_file_name: Optional[str] = None,
    ) -> bool:
        if new_dir_path:
            utils.ensure_dir(new_dir_path)

        for _type in self.__iter_file_types(session_enabled, json_enabled):
            current_path = self.__get_path(_type)
            new_file_path = os.path.join(
                new_dir_path, new_file_name or os.path.basename(current_path)
            )

            shutil.copy(current_path, new_file_path)
            self.__update_path(_type, new_file_path)

        return True

    def _sync_delete_files(
        self: "TelegramClient",
        session_enabled: bool,
        json_enabled: bool,
    ) -> bool:
        for _type in self.__iter_file_types(session_enabled, json_enabled):
            current_path = self.__get_path(_type)
            if os.path.exists(current_path):
                os.remove(current_path)
            self.__update_path(_type, None)

        return True

    async def move_files(
        self: "TelegramClient",
        new_dir_path: Optional[str] = None,
        new_file_name: Optional[str] = None,
        session_enabled: bool = True,
        json_enabled: bool = True,
    ) -> bool:
        """Перемещает файлы сессии и JSON в новое расположение.

        Args:
            new_dir_path: Путь к новой директории.
            new_file_name: Новое имя файла (без расширения).
            session_enabled: Перемещать .session файл.
            json_enabled: Перемещать .json файл.

        Returns:
            True если файлы успешно перемещены.

        Example:
            >>> # Переместить в папку "backup"
            >>> await client.move_files("./backup")
            >>>
            >>> # Переместить и переименовать
            >>> await client.move_files("./archive", "old_session")
        """
        return await asyncio.to_thread(
            self._sync_move_files,
            new_dir_path=new_dir_path,
            new_file_name=new_file_name,
            session_enabled=session_enabled,
            json_enabled=json_enabled,
        )

    async def copy_files(
        self: "TelegramClient",
        new_dir_path: Optional[str] = None,
        new_file_name: Optional[str] = None,
        session_enabled: bool = True,
        json_enabled: bool = True,
    ) -> bool:
        """Копирует файлы сессии и JSON в новое расположение.

        Args:
            new_dir_path: Путь к новой директории.
            new_file_name: Новое имя файла (без расширения).
            session_enabled: Копировать .session файл.
            json_enabled: Копировать .json файл.

        Returns:
            True если файлы успешно скопированы.

        Example:
            >>> # Создать резервную копию
            >>> await client.copy_files("./backup")
        """
        return await asyncio.to_thread(
            self._sync_copy_files,
            new_dir_path=new_dir_path,
            new_file_name=new_file_name,
            session_enabled=session_enabled,
            json_enabled=json_enabled,
        )

    async def delete_files(
        self: "TelegramClient",
        session_enabled: bool,
        json_enabled: bool,
    ) -> bool:
        """Удаляет файлы сессии и/или JSON.

        Args:
            session_enabled: Удалить .session файл.
            json_enabled: Удалить .json файл.

        Returns:
            True если файлы успешно удалены.

        Example:
            >>> # Удалить только JSON
            >>> await client.delete_files(session_enabled=False, json_enabled=True)
        """
        return await asyncio.to_thread(
            self._sync_delete_files,
            session_enabled=session_enabled,
            json_enabled=json_enabled,
        )
