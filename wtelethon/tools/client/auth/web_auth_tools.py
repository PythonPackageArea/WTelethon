import asyncio
import os
from typing import Union, TYPE_CHECKING, Optional

from telethon.helpers import TotalList
from wtelethon import tl_types, tl_functions, tl_errors
from wtelethon import utils


if TYPE_CHECKING:
    from wtelethon import TelegramClient


class WebAuthTools:
    """Инструменты для веб-авторизации клиента."""

    async def accept_web_auth_request(self: "TelegramClient", url: str = "https://web.telegram.org/k/") -> Union[
        tl_types.UrlAuthResultRequest,
        tl_types.UrlAuthResultAccepted,
        tl_types.UrlAuthResultDefault,
    ]:
        """Принимает запрос веб-авторизации для указанного URL.

        Args:
            url: URL веб-приложения Telegram (по умолчанию Telegram Web K).

        Returns:
            Результат веб-авторизации - запрос, принятие или значение по умолчанию.

        Example:
            >>> # Принять авторизацию для Telegram Web
            >>> result = await client.accept_web_auth_request()
            >>>
            >>> if isinstance(result, tl_types.UrlAuthResultAccepted):
            >>>     print(f"Авторизация принята: {result.url}")
        """
        response = await self(tl_functions.messages.AcceptUrlAuthRequest(url=url))
        return response

    async def accept_web_login_token(self: "TelegramClient", token: str, dc_id: int) -> tl_types.Authorization:
        """Принимает веб-токен для авторизации клиента.

        Переключается на указанный дата-центр и выполняет авторизацию
        с помощью веб-токена.

        Args:
            token: Веб-токен авторизации.
            dc_id: ID дата-центра для подключения.

        Returns:
            Объект Authorization при успешной авторизации.

        Example:
            >>> # Авторизоваться с веб-токеном
            >>> token = "MTAxNDkyNDQ..."
            >>> auth = await client.accept_web_login_token(token, dc_id=2)
            >>> print("Веб-авторизация завершена")
        """
        self.session.set_dc(dc_id, utils.get_dc_address(dc_id), 443)

        auth = await self(
            tl_functions.auth.ImportWebTokenAuthorizationRequest(
                web_auth_token=token,
                api_id=self.api_id,
                api_hash=self.api_hash,
            )
        )

        await self._on_login(auth.user)
        return auth
