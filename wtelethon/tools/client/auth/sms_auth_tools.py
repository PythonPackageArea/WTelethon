import asyncio
import time
from typing import Union, TYPE_CHECKING, Optional

from telethon.helpers import TotalList

from wtelethon import tl_types, tl_functions, tl_events, utils

if TYPE_CHECKING:
    from wtelethon import TelegramClient


class SMSAuthTools:
    """Инструменты для SMS-авторизации клиента."""

    async def find_app_login_code(self: "TelegramClient") -> Optional[int]:
        """Ищет код авторизации в последнем сообщении от Telegram.

        Returns:
            Найденный код авторизации или None.

        Example:
            >>> code = await client.find_app_login_code()
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
                phone_number=phone,
                api_id=self.api_id,
                api_hash=self.api_hash,
                settings=settings,
            )
        )
        if isinstance(response, tl_types.auth.SentCodeSuccess) and auto_success_response_login:
            await self._on_login(response.authorization.user)

        return response

    async def sign_in(self: "TelegramClient", phone_number: str, phone_code_hash: str, phone_code: str) -> tl_types.Authorization:
        """Выполняет вход по SMS-коду."""
        response: tl_types.auth.Authorization = await self(
            tl_functions.auth.SignInRequest(phone_number, phone_code_hash, phone_code)
        )
        return await self._on_login(response.user)

    @staticmethod
    async def ensure_app_code_login(
        recipient_client: "TelegramClient",
        donor_client: "TelegramClient",
        timeout: int = 15,
    ) -> Optional[tl_types.Authorization]:
        """Выполняет авторизацию по SMS-коду между двумя клиентами.

        Args:
            recipient_client: Клиент, который получит авторизацию.
            donor_client: Клиент-донор для получения SMS-кода.
            timeout: Время ожидания SMS в секундах.

        Returns:
            Объект Authorization при успешной авторизации.

        Example:
            >>> await SMSAuthTools.ensure_app_code_login(new_client, old_client, timeout=30)
        """
        await donor_client.disconnect()
        sent_code = await recipient_client.send_code_request(donor_client.memory.phone)
        await donor_client.connect()

        if isinstance(sent_code, tl_types.auth.SentCodeSuccess):
            await recipient_client._on_login(sent_code.authorization)
            return True

        if isinstance(sent_code, tl_types.auth.SentCodePaymentRequired):
            raise ValueError("Payment required")

        auth = await SMSAuthTools._wait_for_code_and_login(recipient_client, donor_client, sent_code, timeout)
        return auth

    @staticmethod
    async def _wait_for_code_and_login(
        recipient_client: "TelegramClient",
        donor_client: "TelegramClient",
        sent_code: tl_types.auth.SentCode,
        timeout: int,
    ) -> Optional[tl_types.Authorization]:
        """Ожидает код и выполняет вход."""
        start_time = time.time()
        auth: Optional[tl_types.Authorization] = None

        async def handler(e: tl_events.NewMessage.Event) -> None:
            nonlocal auth
            if time.time() - start_time > timeout or auth is not None:
                return

            code = utils.find_code_in_text(e.message.message)
            if not code:
                return

            auth = await recipient_client.sign_in(
                donor_client.memory.phone,
                sent_code.phone_code_hash,
                str(code),
            )
            return auth

        event = tl_events.NewMessage(from_users=[777000])
        donor_client.add_event_handler(handler, event)
        await asyncio.sleep(timeout)
        donor_client.remove_event_handler(handler, event)

        return auth
