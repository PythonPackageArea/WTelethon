import asyncio
import datetime
import re
import time
from typing import TYPE_CHECKING, Callable, Optional


from telethon_patch import tl_events, tl_types, tl_functions
from telethon_patch import utils

if TYPE_CHECKING:
    from telethon_patch import TelegramClient


async def ensure_app_code_login(
    reciepient_client: "TelegramClient",
    donor_client: "TelegramClient",
    timeout: int = 15,
) -> bool:
    """Выполняет авторизацию по SMS-коду между двумя клиентами.

    Отправляет SMS-код на номер донорского клиента и автоматически
    извлекает его из сообщений для авторизации получающего клиента.

    Args:
        reciepient_client: Клиент, который получит авторизацию.
        donor_client: Клиент-донор для получения SMS-кода.
        timeout: Время ожидания SMS в секундах (по умолчанию 15).

    Returns:
        Объект Authorization при успешной авторизации.

    Raises:
        ValueError: Если требуется оплата для получения кода.

    Example:
        >>> # Авторизовать новый клиент через SMS старого
        >>> new_client = TelegramClient("new_session")
        >>> old_client = TelegramClient("old_session")  # с номером телефона
        >>>
        >>> auth = await ensure_app_code_login(new_client, old_client, timeout=30)
        >>> if auth:
        >>>     print("SMS-авторизация завершена")
    """

    sent_code = await reciepient_client.send_code_request(donor_client.memory.phone)
    if isinstance(sent_code, tl_types.auth.SentCodeSuccess):
        await reciepient_client._on_login(sent_code.authorization)
        return True

    if isinstance(sent_code, tl_types.auth.SentCodePaymentRequired):
        raise ValueError("Payment required")

    start_time = time.time()
    auth: Optional[tl_types.Authorization] = None

    async def handler(e: tl_events.NewMessage.Event):
        nonlocal auth

        if time.time() - start_time > timeout:
            return None

        code = utils.find_code_in_text(e.message.message)
        if not code or auth is not None:
            return None

        request = tl_functions.auth.SignInRequest(
            donor_client.memory.phone, sent_code.phone_code_hash, str(code)
        )
        auth = await donor_client(request)

    event = tl_events.NewMessage(func=lambda e: e.user_id == 777000)
    donor_client.add_event_handler(handler, event)

    await asyncio.sleep(timeout)
    donor_client.remove_event_handler(handler, event)

    return auth
