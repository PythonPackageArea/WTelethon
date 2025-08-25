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
from wtelethon import tl_types, tl_functions, tl_errors
from wtelethon import utils, helpers

from telethon.sessions import SQLiteSession, StringSession, MemorySession

from wtelethon import MemoryAttachment

if TYPE_CHECKING:
    from wtelethon import TelegramClient


class MemoryAttachmentTools:
    """Миксин для доступа к MemoryAttachment внутри клиента."""

    _memory: MemoryAttachment

    @property
    def memory(self) -> MemoryAttachment:
        """Инициализация и/или возврат MemoryAttachment.

        Returns:
            Объект MemoryAttachment для хранения данных аккаунта.

        Example:
            >>> client.memory.api_id = 123456
            >>> client.memory.phone = "+1234567890"
            >>> print(client.memory.first_name)
        """
        memory = getattr(self, "_memory", None)
        if memory is None:
            self._memory = MemoryAttachment()

        return self._memory
