import contextlib
import datetime
from enum import StrEnum
from typing import Optional
import typing

from . import types


class DeadErrorFields:
    dead_status: bool = False
    dead_error: Exception = None


class ApiEnvironmentFields:
    api_id: int
    api_hash: str
    device_model: Optional[str] = None
    system_version: Optional[str] = None
    app_version: Optional[str] = None
    lang_code: Optional[str] = None
    system_lang_code: Optional[str] = None

    lang_pack: str = ""
    layer: int

    tz_offset: Optional[int] = None
    perf_cat: Optional[int] = None


class NotificationFields:
    push_token: Optional[str] = None
    voip_token: Optional[str] = None
    push_token_type: Optional[int] = None
    voip_token_type: Optional[int] = None


class SpamBlockFields:
    spamblock_type: types.SpamblockType = types.SpamblockType.FREE
    spamblock_until_date: Optional[datetime.datetime] = None


class FreezeFields:
    freeze_since_date: Optional[datetime.datetime] = None
    freeze_until_date: Optional[datetime.datetime] = None
    freeze_appeal_url: Optional[str] = None


class TwofaFields:
    twofa: Optional[str] = None
    twofa_unknown: bool = False


class AccountFields:
    account_id: Optional[int] = None

    phone: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    has_profile_pic: bool = False
    date_of_birth: Optional[int] = None
    gender: int = 0


class StatisticsFields:
    spam_count: int = 0
    invites_count: int = 0
    last_connect_date: Optional[datetime.datetime] = None
    session_created_date: Optional[datetime.datetime] = None
    last_check_time: Optional[int] = None

    contacts_count: int = 0
    dialogs_count: int = 0


class NetworkFields:
    proxy: Optional[list] = None
    ipv6: bool = False


class FilesFields:
    source_dir: Optional[str] = None
    session_file: Optional[str] = None


class PremiumFields:
    premium_status: bool = False
    premium_until_date: Optional[datetime.datetime] = None


class MemoryAttachment(
    FreezeFields,
    ApiEnvironmentFields,
    SpamBlockFields,
    TwofaFields,
    AccountFields,
    StatisticsFields,
    NetworkFields,
    FilesFields,
    PremiumFields,
    NotificationFields,
    DeadErrorFields,
):
    """Временное хранилище параметров и статуса Telegram-аккаунта."""

    types = types.Types()

    def __init__(self, **kwargs):
        """Принимает значения полей через kwargs."""
        for key, value in kwargs.items():
            self.__setattr__(key, value)

    def __getattribute__(self, item: str) -> any:
        with contextlib.suppress(AttributeError):
            return object.__getattribute__(self, item)

    def __setattr__(self, item: str, value: any) -> None:
        return object.__setattr__(self, item, value)

    def __iadd__(self, other: "MemoryAttachment") -> "MemoryAttachment":
        for key, value in other.__dict__.items():
            self.__setattr__(key, value)

        return self

    def _to_ts(self, value: datetime.datetime | None):
        return int(value.timestamp()) if value else None

    def _to_iso(self, value: datetime.datetime | None):
        if value is None:
            return None
        if value.tzinfo is None:
            return value.isoformat()
        # %z даёт +0300 без двоеточия
        return value.strftime("%Y-%m-%dT%H:%M:%S%z")

    def fill_json(self, json_attachment: "JsonAttachment") -> int:  # type: ignore
        """Заполняет `JsonAttachment` данными из памяти."""
        data = {
            # базовые
            "app_id": self.api_id,
            "api_id": self.api_id,
            "app_hash": self.api_hash,
            "api_hash": self.api_hash,
            "device_model": self.device_model,
            "device": self.device_model,
            "system_version": self.system_version,
            "sdk": self.system_version,
            "app_version": self.app_version,
            "perf_cat": self.perf_cat,
            "tz_offset": self.tz_offset,
            # язык
            "lang_code": self.lang_code,
            "system_lang_code": self.system_lang_code,
            # аккаунт
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "username": self.username,
            "has_profile_pic": self.has_profile_pic,
            "avatar": None,
            "date_of_birth": self.date_of_birth,
            "sex": self.gender,
            # файлы
            "session_file": self.session_file,
            "session": self.session_file,
            # freeze
            "freeze": (
                {
                    "since": self._to_ts(self.freeze_since_date),
                    "until": self._to_ts(self.freeze_until_date),
                }
                if self.freeze_since_date or self.freeze_until_date
                else None
            ),
            "freeze_since": self._to_iso(self.freeze_since_date),
            "freeze_until": self._to_iso(self.freeze_until_date),
            "freeze_since_date": self._to_ts(self.freeze_since_date),
            "freeze_until_date": self._to_ts(self.freeze_until_date),
            "freeze_appeal_url": self.freeze_appeal_url,
            # статистика
            "spam_count": self.spam_count,
            "stats_spam_count": self.spam_count,
            "invites_count": self.invites_count,
            "stats_invites_count": self.invites_count,
            "last_connect_date": self._to_iso(self.last_connect_date),
            "last_check_time": self.last_check_time,
            "session_created_date": self._to_iso(self.session_created_date),
            "register_time": self._to_ts(self.session_created_date),
            # безопасность
            "twofa": self.twofa,
            "twoFA": self.twofa,
            "tw0FA": self.twofa,
            # спамблок
            "spamblock": self.spamblock_type,
            "spamblock_end_date": self._to_ts(self.spamblock_until_date),
            # премиум
            "is_premium": self.premium_status,
            "premium_expiry": self._to_ts(self.premium_until_date),
            # notification
            "device_token": self.push_token,
        }

        # убрать None
        clean_data = {k: v for k, v in data.items() if v is not None}
        # вложенный freeze=None удалить
        if "freeze" in clean_data and clean_data["freeze"] is None:
            del clean_data["freeze"]
        json_attachment.data.update(clean_data)
        return len(clean_data)

    def update(self, data: dict) -> bool:
        """Обновляет поля объекта из словаря."""
        for key, value in data.items():
            if key in self.__dict__:
                self.__setattr__(key, value)
        return True
