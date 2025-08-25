import asyncio
import datetime
import os
from typing import Union, TYPE_CHECKING, Optional

from telethon_patch import tl_functions
from telethon_patch import utils


if TYPE_CHECKING:
    from telethon_patch import TelegramClient


class AccountNotificationTools:
    """Инструменты для работы с уведомлениями аккаунта."""

    async def register_device(
        self: "TelegramClient",
        token: str,
        token_type: int,
        other_uids: Optional[list[int]] = None,
        app_sandbox: Optional[bool] = None,
        secret: Optional[bytes] = None,
    ) -> bool:
        """Регистрирует устройство для уведомлений.

        Args:
            token: Токен устройства.
            token_type: Тип токена.
            other_uids: Список идентификаторов пользователей.
            app_sandbox: Флаг использования песочницы приложения.
            secret: Секретный ключ для регистрации.

        Returns:
            True если регистрация прошла успешно.

        Example:
            >>> await client.register_device("device_token", token_type=1)
            >>> print("Устройство зарегистрировано")
        """
        return await self(
            tl_functions.account.RegisterDeviceRequest(
                token_type=token_type,
                token=token,
                secret=secret or os.urandom(256),
                other_uids=other_uids or [],
                app_sandbox=app_sandbox or False,
            )
        )

    async def register_voip_token(
        self: "TelegramClient",
        token: str,
        other_uids: Optional[list[int]] = None,
        app_sandbox: Optional[bool] = None,
        secret: Optional[bytes] = None,
        token_type: Optional[int] = None,
    ) -> bool:
        """Регистрирует VoIP токен для уведомлений.

        Args:
            token: Токен VoIP.
            other_uids: Список идентификаторов пользователей.
            app_sandbox: Флаг использования песочницы приложения.
            secret: Секретный ключ для регистрации.
            token_type: Тип токена.

        Returns:
            True если регистрация прошла успешно.

        Example:
            >>> await client.register_voip_token("voip_token")
            >>> if client.memory.voip_token:
            >>>     print(f"VoIP токен зарегистрирован (type: {client.memory.voip_token_type})")
        """

        token = token or self.memory.voip_token
        token_type = token_type or utils.get_voip_token_type(self.api_id)

        if token_type is None:
            raise ValueError("Token type is not found")

        self.memory.voip_token = token
        self.memory.voip_token_type = token_type

        return await self.register_push_token(token, other_uids, app_sandbox, secret, token_type)

    async def register_push_token(
        self: "TelegramClient",
        token: str,
        other_uids: Optional[list[int]] = None,
        app_sandbox: Optional[bool] = None,
        secret: Optional[bytes] = None,
        token_type: Optional[int] = None,
    ) -> bool:
        """Регистрирует push токен для уведомлений.

        Args:
            token: Токен push.
            other_uids: Список идентификаторов пользователей.
            app_sandbox: Флаг использования песочницы приложения.
            secret: Секретный ключ для регистрации.
            token_type: Тип токена.

        Returns:
            True если регистрация прошла успешно.

        Example:
            >>> await client.register_push_token("push_token")
            >>> if client.memory.push_token:
            >>>     print(f"Push токен зарегистрирован (type: {client.memory.push_token_type})")
        """

        token = token or self.memory.push_token
        token_type = token_type or utils.get_push_token_type(self.api_id)

        if token_type is None:
            raise ValueError("Token type is not found")

        self.memory.push_token = token
        self.memory.push_token_type = token_type

        return await self.register_device(token, token_type, other_uids, app_sandbox, secret)
