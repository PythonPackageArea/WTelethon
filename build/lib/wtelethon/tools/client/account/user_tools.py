import asyncio
import datetime
import os
from typing import Union, TYPE_CHECKING, Optional

from wtelethon import tl_types, models


if TYPE_CHECKING:
    from wtelethon import TelegramClient


class AccountUserTools:
    """Инструменты для работы с информацией пользователя аккаунта."""

    async def load_me_info(
        self: "TelegramClient",
    ) -> bool:
        """Загружает информацию о текущем пользователе в память.

        Обновляет поля memory: account_id, first_name, last_name,
        username, phone, has_profile_photo.

        Returns:
            True если информация успешно загружена.

        Example:
            >>> await client.load_me_info()
            >>> print(f"Пользователь: {client.memory.first_name}")
            >>> print(f"Телефон: {client.memory.phone}")
        """
        response: tl_types.User = await self.get_me()
        if response is None:
            raise ValueError("User not found")

        self.memory.account_id = response.id
        self.memory.first_name = response.first_name or ""
        self.memory.last_name = response.last_name or ""
        self.memory.username = response.username or ""
        self.memory.phone = response.phone or ""
        self.memory.has_profile_photo = response.photo is not None

        return True

    async def check_authorization(
        self: "TelegramClient",
        provoke_error: bool = True,
    ) -> bool:
        """Проверяет авторизацию аккаунта и состояние сессии.

        Args:
            provoke_error: Если True, вызывает ошибку при неудачной проверке.

        Returns:
            True если аккаунт авторизован.

        Raises:
            Exception: При неавторизованной сессии (если provoke_error=True).

        Example:
            >>> try:
            >>>     is_authorized = await client.check_authorization()
            >>>     print("Аккаунт авторизован")
            >>> except Exception:
            >>>     print("Требуется авторизация")
        """
        if await self.is_user_authorized():
            return True

        self.memory.dead_status = True
        if provoke_error:
            try:
                await self.get_contacts()
            except Exception as exc:
                self.memory.dead_error = exc
                raise exc

        raise False
