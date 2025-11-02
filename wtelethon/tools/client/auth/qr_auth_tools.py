import asyncio
from typing import TYPE_CHECKING

from wtelethon import tl_types, tl_functions

if TYPE_CHECKING:
    from wtelethon import TelegramClient


class QRAuthTools:
    """Инструменты для QR-авторизации клиента."""

    async def accept_qr_login_token(self: "TelegramClient", token: str) -> tl_types.Authorization:
        """Принимает QR-токен для авторизации другого устройства.

        Args:
            token: QR-токен для авторизации.

        Returns:
            Объект Authorization при успешном принятии токена.

        Example:
            >>> qr_token = "AQABc3RyaW5nDATYJ..."
            >>> auth = await client.accept_qr_login_token(qr_token)
        """
        return await self(tl_functions.auth.AcceptLoginTokenRequest(token=token))

    @staticmethod
    async def ensure_qr_login(recipient_client: "TelegramClient", donor_client: "TelegramClient") -> bool:
        """Выполняет QR-авторизацию между двумя клиентами.

        Args:
            recipient_client: Клиент, который получит авторизацию.
            donor_client: Клиент-донор с существующей авторизацией.

        Returns:
            True при успешной авторизации.

        Example:
            >>> await QRAuthTools.ensure_qr_login(new_client, old_client)
        """
        qr_login = await recipient_client.qr_login()
        await asyncio.gather(
            asyncio.ensure_future(qr_login.wait()),
            donor_client.accept_qr_login_token(token=qr_login.token),
        )
        return True
