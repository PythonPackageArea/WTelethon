import asyncio
import os
from typing import Union, TYPE_CHECKING, Optional

from telethon.helpers import TotalList
from wtelethon import tl_types, tl_functions, tl_errors
from wtelethon import utils


if TYPE_CHECKING:
    from wtelethon import TelegramClient


class QRAuthTools:
    """Инструменты для QR-авторизации клиента."""

    async def accept_qr_login_token(
        self: "TelegramClient", token: str
    ) -> tl_types.Authorization:
        """Принимает QR-токен для авторизации другого устройства.

        Args:
            token: QR-токен для авторизации.

        Returns:
            Объект Authorization при успешном принятии токена.

        Example:
            >>> # Принять QR-токен от другого клиента
            >>> qr_token = "AQABc3RyaW5nDATYJ..."
            >>> auth = await client.accept_qr_login_token(qr_token)
            >>> print("QR-токен принят")
        """
        return await self(tl_functions.auth.AcceptLoginTokenRequest(token=token))
