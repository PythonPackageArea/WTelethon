import datetime
from enum import StrEnum
import inspect
import random
from typing import TYPE_CHECKING, Callable, Optional
import typing
from telethon.tl.types import JsonObject, JsonString, JsonNumber, JsonObjectValue

if TYPE_CHECKING:
    from telethon_patch import TelegramClient


class PlatformData:
    """Данные платформы для эмуляции различных клиентов Telegram."""

    api_id: int
    api_hash: str

    device_models: set[str]
    system_versions: set[str]

    app_versions_by_layer: dict[int, set[str]]

    lang_codes: set[str]
    system_lang_codes: set[str]

    lang_pack: str
    params_callback: Optional[Callable[["TelegramClient"], JsonObject]] = None

    def __init__(self):
        self.device_models = set()
        self.system_versions = set()
        self.app_versions_by_layer = dict()
        self.lang_codes = set()
        self.system_lang_codes = set()
        self.lang_pack = ""

    def __getattr__(self, item: str) -> any:
        attr = getattr(self, item, None)
        if attr is None:
            raise AttributeError(f"Attribute {item} not found")

        return attr

    def __setattr__(self, item: str, value: any) -> None:
        if isinstance(value, str):
            value = [value]

        if isinstance(value, list):
            value = set(value)

        return object.__setattr__(self, item, value)

    def get_params(self, client: "TelegramClient") -> Optional[JsonObject]:
        if self.params_callback is None:
            return None

        return self.params_callback(client)

    def get_data(self, client: "TelegramClient") -> dict[str, any]:
        params = self.get_params(client)

        if not self.api_id or not self.api_hash:
            raise ValueError("API ID and API hash are required")

        layer = client.get_layer()
        app_versions = self.app_versions_by_layer.get(layer, set())

        if not app_versions:
            raise ValueError(f"No app versions for layer {layer}")

        return {
            "api_id": self.api_id,
            "api_hash": self.api_hash,
            "device_model": random.choice(self.device_models),
            "system_version": random.choice(self.system_versions),
            "app_version": random.choice(app_versions),
            "lang_code": random.choice(self.lang_codes),
            "system_lang_code": random.choice(self.system_lang_codes),
            "lang_pack": self.lang_pack,
            "params": params,
        }

    def set_params_callback(self, callback: Callable[["TelegramClient"], JsonObject]) -> "PlatformData":
        signature = inspect.signature(callback)
        if len(signature.parameters) != 1 or signature.parameters[0].name != "client":
            raise ValueError("Callback must take exactly one argument")

        if not isinstance(signature.return_annotation, JsonObject):
            raise ValueError("Callback must return a JsonObject")

        self.params_callback = callback
        return self

    def update(
        self,
        api_id: Optional[int] = None,
        api_hash: Optional[str] = None,
        device_model: set[str] = None,
        system_version: set[str] = None,
        app_versions_by_layer: dict[int, set[str]] = None,
        lang_codes: set[str] = None,
        system_lang_codes: set[str] = None,
        lang_pack: str = None,
    ) -> "PlatformData":

        for key, value in locals().items():
            if key == "self":
                continue

            if value is not None:
                if isinstance(value, str):
                    setattr(self, key, value)
                    continue

                if isinstance(value, (list, set, dict)):
                    getattr(self, key).update(value)
                    continue

        return self


class PlatformAttachment:
    """Коллекция предустановленных платформенных данных для разных клиентов Telegram."""

    windows: PlatformData
    linux: PlatformData
    macos: PlatformData

    android: PlatformData
    android_beta: PlatformData
    android_tgx: PlatformData

    ios: PlatformData

    web_k: PlatformData
    web_z: PlatformData
    web_a: PlatformData

    def __getattr__(self, item: str) -> any:
        attr = getattr(self, item, None)
        if attr is None:
            self.__setattr__(item, PlatformData())
            return self.__getattr__(item)

        return getattr(self, item, None)

    def __setattr__(self, item: str, value: any) -> None:
        return object.__setattr__(self, item, value)
