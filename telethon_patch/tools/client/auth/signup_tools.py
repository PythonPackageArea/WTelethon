import asyncio
import os
from typing import Union, TYPE_CHECKING, Optional

from telethon.helpers import TotalList
from telethon_patch import tl_types, tl_functions, tl_errors
from telethon_patch import utils


if TYPE_CHECKING:
    from telethon_patch import TelegramClient


class SignUpTools:
    """Инструменты для регистрации новых аккаунтов Telegram."""

    async def register(
        self: "TelegramClient",
        code: Union[str, int],
        first_name: str,
        last_name: str = "",
        *,
        phone: str,
        phone_code_hash: str,
    ) -> tl_types.User:
        """Регистрирует новый аккаунт Telegram или выполняет вход в существующий.

        Сначала пытается выполнить вход с указанными данными. Если номер
        не зарегистрирован, создаёт новый аккаунт с указанными именем и фамилией.

        Args:
            code: Код подтверждения из SMS.
            first_name: Имя пользователя.
            last_name: Фамилия пользователя (необязательно).
            phone: Номер телефона.
            phone_code_hash: Хеш кода из предыдущего запроса.

        Returns:
            Объект User после успешной регистрации или входа.

        Example:
            >>> # Сначала отправить код
            >>> sent_code = await client.send_code_request("+1234567890")
            >>>
            >>> # Затем зарегистрироваться
            >>> user = await client.register(
            >>>     code="12345",
            >>>     first_name="Иван",
            >>>     last_name="Петров",
            >>>     phone="+1234567890",
            >>>     phone_code_hash=sent_code.phone_code_hash
            >>> )
            >>> print(f"Аккаунт создан: {user.first_name}")
        """

        me = await self.get_me()
        if me:
            return me

        if not self._tos:
            try:
                return await self.sign_in(
                    phone=phone,
                    code=code,
                    phone_code_hash=phone_code_hash,
                )
            except tl_errors.PhoneNumberUnoccupiedError:
                pass

        result: tl_types.auth.Authorization = await self(
            tl_functions.auth.SignUpRequest(
                phone_number=phone,
                phone_code_hash=phone_code_hash,
                first_name=first_name,
                last_name=last_name,
            )
        )

        if self._tos:
            await self(tl_functions.help.AcceptTermsOfServiceRequest(self._tos.id))

        return await self._on_login(result.user)
