import asyncio
import os
from typing import Union, TYPE_CHECKING, Optional

from telethon.helpers import TotalList
from wtelethon import tl_types, tl_functions, tl_errors
from wtelethon import utils


if TYPE_CHECKING:
    from wtelethon import TelegramClient


class SMSAuthTools:
    """Инструменты для SMS-авторизации клиента."""

    async def find_app_login_code(self: "TelegramClient") -> Optional[int]:
        """Ищет код авторизации в последнем сообщении от Telegram.

        Проверяет последнее сообщение от официального бота Telegram (777000)
        и извлекает из него код авторизации.

        Returns:
            Найденный код авторизации или None если код не найден.

        Example:
            >>> # Найти код авторизации из SMS
            >>> code = await client.find_app_login_code()
            >>> if code:
            >>>     print(f"Найден код: {code}")
            >>> else:
            >>>     print("Код не найден")
        """
        entity = await self.get_entity(777000)
        messages: TotalList = await self.get_messages(entity, limit=1)

        if messages:
            return utils.find_code_in_text(messages[0].message)

        return None

    async def send_code_request(
        self: "TelegramClient",
        phone: str,
        settings: tl_types.CodeSettings = tl_types.CodeSettings(),
        auto_success_response_login: bool = True,
    ) -> Union[
        tl_types.auth.SentCode,
        tl_types.auth.SentCodeSuccess,
        tl_types.auth.SentCodePaymentRequired,
    ]:
        """Отправляет запрос на получение кода авторизации.

        Args:
            phone: Номер телефона для отправки кода.
            settings: Настройки отправки кода (по умолчанию пустые).
            auto_success_response_login: Автоматически выполнить вход при успешном ответе.

        Returns:
            Результат отправки кода - обычный ответ, успешная авторизация или требование оплаты.

        Example:
            >>> # Отправить код на номер
            >>> response = await client.send_code_request("+1234567890")
            >>>
            >>> if isinstance(response, tl_types.auth.SentCode):
            >>>     print("Код отправлен, ожидайте SMS")
            >>> elif isinstance(response, tl_types.auth.SentCodeSuccess):
            >>>     print("Авторизация выполнена автоматически")
        """
        response = await self(
            tl_functions.auth.SendCodeRequest(
                phone=phone,
                api_id=self.api_id,
                api_hash=self.api_hash,
                settings=settings,
            )
        )
        if (
            isinstance(response, tl_types.auth.SentCodeSuccess)
            and auto_success_response_login
        ):
            await self._on_login(response.authorization)

        return response
