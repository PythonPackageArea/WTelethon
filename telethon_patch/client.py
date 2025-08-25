from sqlite3 import Connection
from typing import Optional, Union
import typing
from telethon import TelegramClient as TC
from telethon.network import ConnectionTcpFull
from telethon.sessions import MemorySession, SQLiteSession, StringSession

from telethon_patch import tl_types
from telethon_patch.attachments import MemoryAttachment, JsonAttachment
from telethon_patch.tools.client.account import (
    AccountHelpTools,
    AccountNotificationTools,
    AccountSpambotTools,
    AccountUserTools,
    AccountTwofaTools,
    AccountChatTools,
)
from telethon_patch.tools.client.auth import (
    QRAuthTools,
    SMSAuthTools,
    WebAuthTools,
    SignUpTools,
)

from telethon_patch.tools.attachments import (
    FileAttachmentsTools,
    JsonAttachmentTools,
    MemoryAttachmentTools,
    PlatformAttachmentTools,
)

from telethon_patch.tools.storages import (
    ProxyStorageTools,
    ClientHoldStorageTools,
)
from telethon_patch.tools.client.internal_tools import InternalTools
from telethon_patch.tools.handlers.exception_tools import ExceptionHandlerTools
from telethon_patch.tools.session.convert_tools import ConvertTools

from telethon.tl import alltlobjects
from telethon.network import MTProtoSender, Connection, ConnectionTcpFull, TcpMTProxy

SessionType = Union[MemorySession, SQLiteSession, StringSession]


class TelegramClient(
    AccountHelpTools,
    AccountNotificationTools,
    AccountSpambotTools,
    AccountUserTools,
    AccountTwofaTools,
    AccountChatTools,
    QRAuthTools,
    SMSAuthTools,
    WebAuthTools,
    SignUpTools,
    InternalTools,
    ExceptionHandlerTools,
    ConvertTools,
    MemoryAttachmentTools,
    JsonAttachmentTools,
    FileAttachmentsTools,
    PlatformAttachmentTools,
    ProxyStorageTools,
    ClientHoldStorageTools,
    TC,
):
    """Телеграм-клиент с расширенными возможностями."""

    session: SessionType

    __kwargs__: dict

    def __init__(
        self,
        session: Union[str, SessionType],
        *,
        json_path: Optional[str] = None,
        json_attachment: Optional[JsonAttachment] = None,
        memory_attachment: Optional[MemoryAttachment] = None,
        layer: Optional[int] = None,
        init_params: Optional[tl_types.JsonObject] = None,
        timeout: int = 10,
        request_retries: int = 5,
        connection_retries: int = 5,
        flood_sleep_threshold: int = 60,
        connection: "typing.Type[Connection]" = ConnectionTcpFull,
        proxy: typing.Union[tuple, dict] = None,
        retry_delay: int = 1,
        auto_reconnect: bool = True,
        sequential_updates: bool = False,
        raise_last_call_error: bool = False,
        receive_updates: bool = True,
        catch_up: bool = False,
        entity_cache_limit: int = 5000,
    ):
        """Инициализирует клиент и применяет вложения."""
        if memory_attachment:
            self._memory = memory_attachment

        if json_attachment:
            self._json = json_attachment

        if json_path:
            self.init_json(json_path)

        self._exception_handlers = []
        self._init_params = init_params

        if isinstance(session, str):
            sqlite_session = SQLiteSession(session)

            session = StringSession()
            session.auth_key = sqlite_session.auth_key
            session.set_dc(sqlite_session.dc_id, sqlite_session.server_address, sqlite_session.port)

        self.__kwargs__ = dict(
            session=session,
            timeout=timeout,
            request_retries=request_retries,
            connection_retries=connection_retries,
            flood_sleep_threshold=flood_sleep_threshold,
            connection=connection,
            proxy=proxy,
            retry_delay=retry_delay,
            auto_reconnect=auto_reconnect,
            sequential_updates=sequential_updates,
            raise_last_call_error=raise_last_call_error,
            receive_updates=receive_updates,
            catch_up=catch_up,
            entity_cache_limit=entity_cache_limit,
        )

        self.set_layer(layer)

        if self.json:
            if not self.json.data:
                return

            self.json.fill_memory(self.memory)

        self._super_init()

    def _super_init(self):
        """Вызывает родительский инициализатор с параметрами из памяти."""
        super().__init__(
            api_id=self.memory.api_id,
            api_hash=self.memory.api_hash,
            device_model=self.memory.device_model or "Unknown",
            system_version=self.memory.system_version or "1.0.0",
            app_version=self.memory.app_version or self.__version__,
            lang_code=self.memory.lang_code or "en",
            system_lang_code=self.memory.system_lang_code or "en-US",
            **self.__kwargs__,
        )
        self.update_client_params(self._init_params)
        self.update_client_lang_pack(self.memory.lang_pack)
