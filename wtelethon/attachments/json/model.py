import asyncio
import json
import os
from typing import Any, Iterator, Optional, TYPE_CHECKING
from datetime import datetime as dt

if TYPE_CHECKING:
    from wtelethon import MemoryAttachment


class JsonAttachment:
    """JSON вложение для хранения данных аккаунта в файле."""

    _data: dict
    _file_path: str

    def __init__(self, file_path: str, include_data: Optional[dict] = None):
        if not file_path or not os.path.exists(file_path):
            raise ValueError("file_path is not exists")

        if include_data and isinstance(include_data, dict) is False:
            raise ValueError("include_data must be a dictionary")

        self._file_path = file_path
        self._data = include_data or {}

    def __getattr__(self, key: str) -> Any:
        if key in ["_data", "_file_path"]:
            return object.__getattribute__(self, key)

        return self._data.get(key)

    def __setattr__(self, key: str, value: Any) -> None:
        if key in ["_data", "_file_path"]:
            object.__setattr__(self, key, value)
            return

        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __str__(self) -> str:
        return json.dumps(self._data, indent=4)

    def __repr__(self) -> str:
        return f"JsonAttachment(file_path={self._file_path}, data={self._data})"

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def data(self) -> dict:
        return self._data

    async def update(self, data: dict, save: bool = True) -> None:
        self._data.update(data)

        if save:
            await self.save()

    def _sync_save(self) -> bool:
        content = str(self)
        with open(self._file_path, "w") as f:
            f.write(content)

        return True

    def _sync_load(self) -> bool:
        with open(self._file_path, "r") as f:
            self._data = json.load(f)

        return True

    async def save(self) -> "JsonAttachment":
        await asyncio.to_thread(self._sync_save)
        return self

    async def load(self) -> "JsonAttachment":
        await asyncio.to_thread(self._sync_load)
        return self

    # ---------------------------------------------------------------------
    # helpers
    # ---------------------------------------------------------------------

    def first(self, *keys: str, default: Any | None = None) -> Any:
        """Возвращает первое ненулевое значение из списка ключей."""
        for key in keys:
            value = getattr(self, key, None)
            if value not in (None, "", []):
                return value
        return default

    @staticmethod
    def to_dt(value):
        """Конвертация timestamp или ISO-строки в datetime."""
        if value in (None, ""):
            return None
        if isinstance(value, (int, float)):
            return dt.fromtimestamp(value)
        if isinstance(value, str):
            try:
                return dt.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None

    # ------------------------------------------------------------------
    # public api
    # ------------------------------------------------------------------

    def fill_memory(self, memory: "MemoryAttachment") -> bool:
        """Заполняет объект memory данными из JSON."""
        # Lazy import во избежание циклов
        # --- basic
        memory.api_id = self.first("app_id", "api_id")
        memory.api_hash = self.first("app_hash", "api_hash")
        memory.device_model = self.first("device_model", "device")
        memory.system_version = self.first("system_version", "sdk")
        memory.app_version = self.first("app_version")

        # --- language
        memory.lang_code = self.first("lang_code", "lang_pack")
        memory.system_lang_code = self.first("system_lang_code", "system_lang_pack")
        memory.lang_pack = self.first("lang_pack")

        # --- account
        memory.first_name = self.first("first_name")
        memory.last_name = self.first("last_name")
        memory.phone = self.first("phone")
        memory.username = self.first("username")
        memory.has_profile_pic = bool(self.first("avatar", "has_profile_pic"))
        memory.date_of_birth = self.first("date_of_birth") or 0
        memory.gender = self.first("gender", "sex") or 0
        memory.session_file = self.first("session_file", "session")

        # --- freeze
        freeze_data = getattr(self, "freeze", None)
        if isinstance(freeze_data, dict):
            since = freeze_data.get("since")
            until = freeze_data.get("until")
        else:
            since = self.first("freeze_since", "freeze_since_date")
            until = self.first("freeze_until", "freeze_until_date")
        memory.freeze_since_date = self.to_dt(since)
        memory.freeze_until_date = self.to_dt(until)
        memory.freeze_appeal_url = self.first("freeze_appeal_url")

        # --- statistics
        memory.spam_count = self.first("spam_count", "stats_spam_count") or 0
        memory.invites_count = self.first("invites_count", "stats_invites_count") or 0
        memory.last_connect_date = self.to_dt(self.first("last_connect_date"))
        memory.last_check_time = self.first("last_check_time")
        memory.session_created_date = self.to_dt(
            self.first("session_created_date", "register_time")
        )

        # --- security
        memory.twofa = self.first("twofa", "twoFA", "tw0FA")

        return True
