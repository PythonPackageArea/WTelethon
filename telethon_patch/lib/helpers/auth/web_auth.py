import asyncio
import datetime
import re
import time
from typing import TYPE_CHECKING, Callable, Optional


from telethon_patch import tl_events, tl_types, tl_functions
from telethon_patch import utils

if TYPE_CHECKING:
    from telethon_patch import TelegramClient


async def ensure_web_login(reciepient_client: "TelegramClient", donor_client: "TelegramClient") -> bool:
    """Выполняет веб-авторизацию между двумя клиентами.

    Создаёт веб-токен на донорском клиенте и передаёт его получающему
    клиенту для авторизации через Telegram Web.

    Args:
        reciepient_client: Клиент, который получит авторизацию.
        donor_client: Клиент-донор с существующей авторизацией.

    Returns:
        True при успешной авторизации.

    Raises:
        ValueError: Если веб-авторизация не принята.

    Example:
        >>> # Авторизовать новый клиент через веб-токен
        >>> new_client = TelegramClient("new_session")
        >>> old_client = TelegramClient("old_session")
        >>>
        >>> await ensure_web_login(new_client, old_client)
        >>> print("Веб-авторизация завершена")
    """
    url_auth_result = await donor_client.accept_web_auth_request()
    if not isinstance(url_auth_result, tl_types.UrlAuthResultAccepted):
        raise ValueError("Url auth result is not accepted")

    await reciepient_client.accept_web_login_token(*utils.parse_url_auth(url_auth_result.url))

    return True
