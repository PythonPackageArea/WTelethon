import asyncio
import datetime
import re
import time
from typing import TYPE_CHECKING, Callable, Optional


from telethon_patch import tl_events, tl_types, tl_functions
from telethon_patch import utils

if TYPE_CHECKING:
    from telethon_patch import TelegramClient


async def ensure_qr_login(
    recipient_client: "TelegramClient", donor_client: "TelegramClient"
) -> bool:
    """Выполняет QR-авторизацию между двумя клиентами.

    Создаёт QR-токен на получающем клиенте и автоматически принимает его
    на донорском клиенте для передачи авторизации.

    Args:
        recipient_client: Клиент, который получит авторизацию.
        donor_client: Клиент-донор с существующей авторизацией.

    Returns:
        True при успешной авторизации.

    Example:
        >>> # Авторизовать новый клиент через QR от старого
        >>> new_client = TelegramClient("new_session")
        >>> old_client = TelegramClient("old_session")
        >>>
        >>> await ensure_qr_login(new_client, old_client)
        >>> print("QR-авторизация завершена")
    """
    qr_login = await recipient_client.qr_login()
    await asyncio.gather(
        asyncio.ensure_future(qr_login.wait()),
        donor_client.accept_qr_login_token(token=qr_login.token),
    )

    return True
