import os
from typing import Optional, Union, Type

from telethon import TelegramClient as TC, Connection, ConnectionTcpFull
from telethon.sessions import MemorySession, SQLiteSession, StringSession

from wtelethon import tl_types, utils, models
from wtelethon.attachments import MemoryAttachment, JsonAttachment
from wtelethon.attachments.platform.model import PlatformData
from wtelethon.tools.client.account import (
    AccountHelpTools,
    AccountNotificationTools,
    AccountSpambotTools,
    AccountUserTools,
    AccountTwofaTools,
    AccountChatTools,
)
from wtelethon.tools.client.auth import (
    QRAuthTools,
    SMSAuthTools,
    WebAuthTools,
    SignUpTools,
)
from wtelethon.tools.attachments import (
    FileAttachmentsTools,
    JsonAttachmentTools,
    MemoryAttachmentTools,
    PlatformAttachmentTools,
)
from wtelethon.tools.storages import (
    ProxyStorageTools,
    ClientHoldStorageTools,
)
from wtelethon.tools.client.internal_tools import InternalTools
from wtelethon.tools.handlers.exception_tools import ExceptionHandlerTools
from wtelethon.tools.session.convert_tools import ConvertTools

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
        dc_id: Optional[int] = None,
        json_path: Optional[str] = None,
        json_attachment: Optional[JsonAttachment] = None,
        memory_attachment: Optional[MemoryAttachment] = None,
        platform_data: Optional[PlatformData] = None,
        init_params: Optional[tl_types.JsonObject] = None,
        timeout: int = 10,
        request_retries: int = 5,
        connection_retries: int = 5,
        flood_sleep_threshold: int = 60,
        connection: Type[Connection] = ConnectionTcpFull,
        proxy: Union[tuple, dict] = None,
        retry_delay: int = 1,
        auto_reconnect: bool = True,
        sequential_updates: bool = False,
        raise_last_call_error: bool = False,
        receive_updates: bool = True,
        catch_up: bool = False,
        entity_cache_limit: int = 5000,
    ):
        """Инициализирует клиент и применяет вложения."""

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

        self._exception_handlers = []
        self._init_params = init_params

        if json_attachment is not None:
            self._json = json_attachment
            self.json.fill_memory(self.memory)

        if memory_attachment is not None:
            self.memory.__iadd__(memory_attachment)

        if isinstance(session, str):
            if session[0] == "1" and len(session) == 353:
                self.__kwargs__.update(session=StringSession(session))

            elif utils.is_hex(session) and len(session) == 512:
                self.__kwargs__.update(session=self.load_auth_key_hex(session, dc_id=dc_id))

            else:
                self.memory.source_dir = os.path.dirname(session)
                self.memory.session_file = os.path.basename(session)
                self.__kwargs__.update(session=self._sync_load_sqlite_session())

        if dc_id is not None:
            self.set_dc(dc_id)

        if self.json is None and json_path:
            self.init_json(json_path)
            return

        if platform_data is not None:
            self.update_client_platform(platform_data, reinit=False)

        if self.json:
            self.memory.fill_json(self.json)

        self._super_init()

    def _super_init(self):
        if self.json and self.json.loaded is False:
            raise ValueError("json file is not loaded")

        """Вызывает родительский инициализатор с параметрами из памяти."""
        super().__init__(
            api_id=self.memory.api_id,
            api_hash=self.memory.api_hash,
            device_model=self.memory.device_model,
            system_version=self.memory.system_version,
            app_version=self.memory.app_version,
            lang_code=self.memory.lang_code,
            system_lang_code=self.memory.system_lang_code,
            **self.__kwargs__,
        )
        self.update_client_params(self._init_params)
        self.update_client_lang_pack(self.memory.lang_pack)

        if self.session.dc_id not in models.TGDC:
            self.set_dc(2)
